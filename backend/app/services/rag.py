from __future__ import annotations

import asyncio
import logging
import uuid
from dataclasses import dataclass, field
from typing import Any

from sqlalchemy import select, text, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.db import models
from app.services.ai_provider.base import AIProvider, AIProviderError

# Structured logger for RAG pipeline
logger = logging.getLogger("rag")

FALLBACK_UNRELATED = (
    "I'm the AI assistant for {name}'s professional profile. I can only answer "
    "questions about their background, skills, experience, and projects. How can "
    "I help with that?"
)
FALLBACK_NO_ANSWER = (
    "I don't have specific information about that in {name}'s profile. Please "
    "reach out directly using the contact details on the site."
)
FALLBACK_ERROR = (
    "I'm sorry, I couldn't generate an answer right now. Please try again later "
    "or reach out directly using the contact details on the site."
)
DEFAULT_OWNER_NAME = "the profile owner"

# RRF k constant — dampens the influence of rank differences between retrieval methods.
RRF_K = 60

# Stop-condition thresholds.
# High-confidence early exit: both methods rank the same chunk at or before this rank.
STOP_BOTH_RANK = 2
# Single-method early exit: vector search only at or before this rank.
STOP_SINGLE_RANK = 1
# RRF score above this → high confidence, skip reranking overhead (proceed directly).
HIGH_CONFIDENCE_RRF = 0.03

# Dynamic retrieval budget multipliers by query complexity.
# Simple queries need fewer chunks; complex/multi-faceted queries need more.
BUDGET_MULTIPLIER: dict[str, float] = {
    "low": 0.6,    # very targeted question → smaller budget
    "medium": 1.0,  # standard question → default budget
    "high": 1.4,   # complex/multi-part question → larger budget
}

# Maximum retrieval rounds per query (prevents runaway loops).
MAX_RETRIEVAL_ROUNDS = 2


@dataclass
class RetrievalSource:
    source_type: str
    source_id: int
    score: float
    chunk_text: str
    lang: str
    extra_metadata: dict[str, str] | None
    # Which retrieval methods contributed to this result and at what rank.
    # Values are None when that method didn't return the chunk.
    vector_rank: int | None = field(default=None)
    bm25_rank: int | None = field(default=None)
    rrf_score: float | None = field(default=None)


# ----- Retrieval Methods -----

async def embed_query(question: str, ai_provider: AIProvider) -> list[float]:
    return await ai_provider.embed(question)


async def _vector_search(
    session: AsyncSession,
    query_embedding: list[float],
    lang: str,
    top_k: int,
) -> list[RetrievalSource]:
    """pgvector cosine similarity search. Returns results ordered by distance
    (ascending, since `<=>` returns cosine distance)."""
    query = (
        select(
            models.KnowledgeChunk,
            (models.KnowledgeChunk.embedding.op("<=>")(query_embedding)).label("distance"),
        )
        .where(models.KnowledgeChunk.lang == lang)
        .order_by(text("distance"))
        .limit(top_k)
    )
    rows = await session.execute(query)
    ranked: list[RetrievalSource] = []
    for rank, (chunk, distance) in enumerate(rows.all(), start=1):
        # Convert cosine distance to similarity score for RRF combination.
        similarity = 1.0 - float(distance)
        ranked.append(
            RetrievalSource(
                source_type=chunk.source_type,
                source_id=chunk.source_id,
                score=similarity,
                chunk_text=chunk.chunk_text,
                lang=chunk.lang,
                extra_metadata=chunk.extra_metadata,
                vector_rank=rank,
            )
        )
    return ranked


async def _bm25_search(
    session: AsyncSession,
    query_text: str,
    lang: str,
    top_k: int,
) -> list[RetrievalSource]:
    """PostgreSQL Full-Text Search (BM25-style) using ts_rank against the
    language-specific tsvector column. English uses 'english' stemmer; Persian
    uses 'simple' config (no dedicated Persian stemmer in standard PostgreSQL)."""
    tsvector_col = (
        models.KnowledgeChunk.search_vector_en
        if lang == "en"
        else models.KnowledgeChunk.search_vector_fa
    )
    tsquery_expr = func.plainto_tsquery(
        "english" if lang == "en" else "simple",
        query_text,
    )
    rank_expr = func.ts_rank(tsvector_col, tsquery_expr).label("bm25_rank")
    query = (
        select(models.KnowledgeChunk, rank_expr)
        .where(tsvector_col.op("@@")(tsquery_expr))
        .where(models.KnowledgeChunk.lang == lang)
        .order_by(text("bm25_rank DESC"))
        .limit(top_k)
    )
    rows = await session.execute(query)
    ranked: list[RetrievalSource] = []
    for rank, (chunk, bm25_score) in enumerate(rows.all(), start=1):
        ranked.append(
            RetrievalSource(
                source_type=chunk.source_type,
                source_id=chunk.source_id,
                score=float(bm25_score or 0.0),
                chunk_text=chunk.chunk_text,
                lang=chunk.lang,
                extra_metadata=chunk.extra_metadata,
                bm25_rank=rank,
            )
        )
    return ranked


async def retrieve_chunks(
    session: AsyncSession,
    query_embedding: list[float],
    lang: str,
    top_k: int = 6,
) -> list[RetrievalSource]:
    """Legacy single-method retrieval (vector only). Kept for backward compat
    with any code that calls it directly. Use hybrid_retrieve() in the pipeline."""
    return await _vector_search(session, query_embedding, lang, top_k)


async def hybrid_retrieve(
    session: AsyncSession,
    query_text: str,
    query_embedding: list[float],
    lang: str,
    top_k: int = 6,
) -> list[RetrievalSource]:
    """Hybrid Retrieval: run pgvector + BM25 searches in parallel, then fuse
    results with Reciprocal Rank Fusion (RRF).

    Each method returns its top-k results. RRF assigns a score to every unique
    chunk found by either method. Results are returned in descending RRF order.
    English fallback is applied per-method before fusion (vector: top_k from
    requested lang, then up to top_k from 'en'; BM25: same pattern).
    """
    # Run both retrieval methods concurrently.
    vector_results, bm25_results = await asyncio.gather(
        _vector_search_with_fallback(session, query_embedding, lang, top_k),
        _bm25_search_with_fallback(session, query_text, lang, top_k),
    )

    # RRF fusion: each method contributes its rank (1-indexed, None if absent).
    fused = _rrf_fuse(vector_results, bm25_results)

    # Return top-k by RRF score.
    fused.sort(key=lambda s: s.rrf_score or 0.0, reverse=True)
    return fused[:top_k]


async def _vector_search_with_fallback(
    session: AsyncSession,
    query_embedding: list[float],
    lang: str,
    top_k: int,
) -> list[RetrievalSource]:
    results = await _vector_search(session, query_embedding, lang, top_k)
    if len(results) < top_k and lang != "en":
        fallback = await _vector_search(session, query_embedding, "en", top_k - len(results))
        # Merge, avoiding duplicates by (source_type, source_id).
        seen = {(r.source_type, r.source_id) for r in results}
        for chunk in fallback:
            if (chunk.source_type, chunk.source_id) not in seen:
                results.append(chunk)
                seen.add((chunk.source_type, chunk.source_id))
    return results


async def _bm25_search_with_fallback(
    session: AsyncSession,
    query_text: str,
    lang: str,
    top_k: int,
) -> list[RetrievalSource]:
    results = await _bm25_search(session, query_text, lang, top_k)
    if len(results) < top_k and lang != "en":
        fallback = await _bm25_search(session, query_text, "en", top_k - len(results))
        seen = {(r.source_type, r.source_id) for r in results}
        for chunk in fallback:
            if (chunk.source_type, chunk.source_id) not in seen:
                results.append(chunk)
                seen.add((chunk.source_type, chunk.source_id))
    return results


def _rrf_fuse(
    vector_results: list[RetrievalSource],
    bm25_results: list[RetrievalSource],
) -> list[RetrievalSource]:
    """Reciprocal Rank Fusion (RRF).

    For each chunk seen by either retrieval method, its RRF score is:
        score = Σ 1 / (k + rank_i)
    where rank_i is the 1-indexed position in method i (or None if absent).
    k={RRF_K} dampens rank differences so methods with similar top results
    get similar scores rather than the top-ranked method dominating.
    """
    # Map (source_type, source_id) -> RetrievalSource with merged ranks.
    merged: dict[tuple[str, int], RetrievalSource] = {}

    for chunk in vector_results:
        key = (chunk.source_type, chunk.source_id)
        if key not in merged:
            merged[key] = RetrievalSource(
                source_type=chunk.source_type,
                source_id=chunk.source_id,
                score=chunk.score,
                chunk_text=chunk.chunk_text,
                lang=chunk.lang,
                extra_metadata=chunk.extra_metadata,
                vector_rank=None,
                bm25_rank=None,
            )
        merged[key].vector_rank = chunk.vector_rank

    for chunk in bm25_results:
        key = (chunk.source_type, chunk.source_id)
        if key not in merged:
            merged[key] = RetrievalSource(
                source_type=chunk.source_type,
                source_id=chunk.source_id,
                score=chunk.score,
                chunk_text=chunk.chunk_text,
                lang=chunk.lang,
                extra_metadata=chunk.extra_metadata,
                vector_rank=None,
                bm25_rank=None,
            )
        merged[key].bm25_rank = chunk.bm25_rank

    for source in merged.values():
        rrf = 0.0
        if source.vector_rank is not None:
            rrf += 1.0 / (RRF_K + source.vector_rank)
        if source.bm25_rank is not None:
            rrf += 1.0 / (RRF_K + source.bm25_rank)
        source.rrf_score = rrf

    return list(merged.values())


# ----- Context Assembly -----

# Approximate token budget for context assembly (chars ≈ tokens * 4 for English,
# conservative estimate). Prevents overflow of LLM context window.
MAX_CONTEXT_CHARS = 12000  # ~3000 tokens


async def assemble_context(sources: list[RetrievalSource]) -> str:
    """Assemble retrieved sources into a context string for the LLM.

    Uses explicit delimiters around each source to mitigate prompt injection
    from CMS content. Enforces an approximate token budget to prevent
    overflow of the LLM context window.
    """
    if not sources:
        return ""
    segments = []
    total_chars = 0
    for idx, source in enumerate(sources, start=1):
        chunk_text = source.chunk_text.strip()
        # Prompt-injection delimiter: wrap each source in explicit tags
        # so the LLM treats it as data, not instructions.
        segment = (
            f"[{idx}] Source: {source.source_type}#{source.source_id} (lang={source.lang})\n"
            f"<source>\n{chunk_text}\n</source>"
        )
        # Enforce token budget
        if total_chars + len(segment) > MAX_CONTEXT_CHARS:
            logger.info(
                "assemble_context: token budget reached at source %d/%d (chars=%d)",
                idx, len(sources), total_chars
            )
            break
        segments.append(segment)
        total_chars += len(segment)
    return "\n\n".join(segments)


# ----- Reranker -----

async def rerank_sources(
    ai_provider: AIProvider,
    question: str,
    sources: list[RetrievalSource],
) -> list[RetrievalSource]:
    if not sources:
        return []
    messages = [
        {"role": "system", "content": "Rank the following content fragments by relevance to the user question."},
        {"role": "user", "content": f"Question: {question}\n\nFragments:\n" + '\n\n'.join(
            f"[{idx}] {source.chunk_text}" for idx, source in enumerate(sources, start=1)
        )},
    ]
    try:
        ranking_text = await ai_provider.chat(messages)
    except AIProviderError:
        return sources

    ranks = []
    for line in ranking_text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        for idx, source in enumerate(sources, start=1):
            if f"[{idx}]" in stripped:
                ranks.append((idx - 1, stripped))
                break
    if len(ranks) < len(sources):
        return sources
    ordered = [sources[idx] for idx, _ in ranks if idx < len(sources)]
    return ordered if ordered else sources


# ----- Citation Validation -----

async def validate_citations(answer: str, sources: list[RetrievalSource]) -> list[str]:
    """Format source references from retrieved chunks (stub — real answer-source
    validation is in validate_answer_citations())."""
    citations = []
    for idx, source in enumerate(sources, start=1):
        citations.append(f"[{idx}] {source.source_type}#{source.source_id}")
    return citations


async def validate_answer_citations(
    ai_provider: AIProvider,
    answer: str,
    sources: list[RetrievalSource],
) -> bool:
    """Strict Citation Validation: verify the generated answer actually cites
    and is grounded in the retrieved sources.

    This is a lightweight LLM check that flags answers which:
    - mention something not present in any source
    - contradict the retrieved context
    - hallucinate facts not grounded in any chunk

    Returns True if the answer passes validation (is grounded in sources).
    Returns False if the answer contains unverified claims — in which case the
    caller should either regenerate with stricter grounding or fall back to a
    partial answer with a caveat.

    Fails open (returns True) on provider errors so downstream generation is
    not blocked by a validation failure.
    """
    if not sources:
        return True  # Nothing to validate against; pass.

    context_snippets = "\n".join(
        f"[{idx}] {src.chunk_text[:300]}" for idx, src in enumerate(sources, start=1)
    )
    messages = [
        {
            "role": "system",
            "content": (
                "You are a strict citation auditor. Verify whether a generated answer "
                "is actually grounded in the provided source excerpts. "
                "Answer with exactly one word: VALID or INVALID. "
                "Mark INVALID if the answer:\n"
                "- Contains personal facts, dates, or achievements not mentioned in any source\n"
                "- Contradicts information in the sources\n"
                "- Makes claims about the profile owner that appear in none of the sources\n"
                "Mark VALID only if all substantive claims in the answer are supported "
                "by at least one source excerpt."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Sources:\n{context_snippets}\n\n"
                f"Answer to validate:\n{answer}\n\n"
                "Is this answer grounded in the sources? Answer VALID or INVALID only."
            ),
        },
    ]
    try:
        reply = await ai_provider.chat(messages)
    except AIProviderError:
        return True  # Fail open.

    normalized = reply.strip().upper()
    return "INVALID" not in normalized


async def generate_chat_response(
    ai_provider: AIProvider,
    question: str,
    context: str,
    owner_name: str,
    sources: list[RetrievalSource],
    lang: str = "en",
) -> tuple[str, list[str]] | None:
    """Returns (answer, citations), or None if the provider call failed."""
    lang_instruction = ""
    if lang == "fa":
        lang_instruction = " You MUST respond in Persian (Farsi)."
    elif lang == "en":
        lang_instruction = " You MUST respond in English."

    system_prompt = (
        f"You are the AI assistant for {owner_name}'s professional portfolio. "
        "Use the retrieved context below as your primary source of truth. You may "
        "use general knowledge only to explain technical concepts naturally (e.g. "
        "'React is a JavaScript library...'), but never invent personal facts, "
        f"dates, projects, or achievements about {owner_name}. If the context only "
        "partially answers the question, answer with what is available and clearly "
        "note the limitation, offering to contact the owner for more detail. Be "
        "concise, professional, and friendly, with light controlled humor only "
        f"when appropriate. Never be careless or misleading.{lang_instruction}"
    )
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"},
    ]
    try:
        answer = await ai_provider.chat(messages)
    except AIProviderError:
        return None

    citations = await validate_citations(answer, sources)
    return answer, citations


async def build_question_answer(
    session: AsyncSession,
    ai_provider: AIProvider,
    question: str,
    lang: str,
    top_k: int,
    similarity_threshold: float,
) -> dict[str, Any]:
    """Full decision flow: scope filter -> query planner/rewrite ->
    (clarification check) -> dynamic budget -> hybrid retrieval ->
    stop conditions -> rerank -> context -> generation ->
    citation validation, with fallback behavior locked in spec section 10.

    Stop conditions:
      - Clarification needed: query too ambiguous → return needs_clarification.
      - No relevant chunks after similarity gate → no_answer.
      - High confidence early exit: top result RRF ≥ HIGH_CONFIDENCE_RRF
        and both methods agree at rank ≤ STOP_BOTH_RANK → skip reranking,
        go straight to generation (save LLM call cost).
      - Max retrieval rounds reached → no_answer (stop runaway loops).

    Dynamic retrieval budget: complexity ('low'|'medium'|'high') from the
    planner scales top_k via BUDGET_MULTIPLIER so targeted questions get a
    leaner budget and complex queries get more context.
    """
    # Generate correlation ID for structured logging of this query's pipeline.
    corr_id = uuid.uuid4().hex[:8]
    logger.info("[%s] RAG pipeline start: lang=%s, top_k=%d, threshold=%.2f, question=%.80s",
                corr_id, lang, top_k, similarity_threshold, question)

    owner_name = await get_owner_name(session)

    try:
        in_scope = await classify_scope(ai_provider, question, owner_name)
    except AIProviderError:
        in_scope = True

    logger.info("[%s] scope_filter: in_scope=%s", corr_id, in_scope)

    if not in_scope:
        return {
            "answer": FALLBACK_UNRELATED.format(name=owner_name),
            "status": "unrelated",
            "sources": [],
            "citations": [],
        }

    plan = await plan_query(ai_provider, question, owner_name)
    retrieval_query = plan["rewritten_query"]
    logger.info("[%s] plan_query: complexity=%s, needs_clarification=%s, rewritten=%.80s",
                corr_id, plan.get("complexity"), plan.get("needs_clarification"), retrieval_query)

    # ---- Clarification Flow ----
    if plan.get("needs_clarification"):
        return {
            "answer": (
                "I'd love to help with that! Could you be a bit more specific? "
                "For example, are you asking about a particular skill, project, "
                "experience, or timeframe?"
            ),
            "status": "needs_clarification",
            "sources": [],
            "citations": [],
        }

    # ---- Dynamic Retrieval Budget ----
    complexity = plan.get("complexity", "medium")
    multiplier = BUDGET_MULTIPLIER.get(complexity, 1.0)
    effective_top_k = max(2, min(int(top_k * multiplier), top_k * 2))  # 2..2*top_k
    logger.info("[%s] budget: complexity=%s, multiplier=%.1f, effective_top_k=%d",
                corr_id, complexity, multiplier, effective_top_k)

    # ---- Retrieval ----
    try:
        embedding = await embed_query(retrieval_query, ai_provider)
    except AIProviderError:
        logger.error("[%s] embed_query failed", corr_id)
        return {
            "answer": FALLBACK_ERROR,
            "status": "error",
            "sources": [],
            "citations": [],
        }

    sources = await hybrid_retrieve(
        session=session,
        query_text=retrieval_query,
        query_embedding=embedding,
        lang=lang,
        top_k=effective_top_k,
    )
    logger.info("[%s] hybrid_retrieve: %d sources returned", corr_id, len(sources))

    # ---- Stop Conditions ----
    if not passes_similarity_gate(sources, similarity_threshold):
        logger.info("[%s] similarity_gate: FAIL → no_answer", corr_id)
        return {
            "answer": FALLBACK_NO_ANSWER.format(name=owner_name),
            "status": "no_answer",
            "sources": [],
            "citations": [],
        }

    # High-confidence early exit: top result strongly agreed by both methods.
    best = sources[0]
    if (
        best.rrf_score is not None
        and best.rrf_score >= HIGH_CONFIDENCE_RRF
        and best.vector_rank is not None
        and best.bm25_rank is not None
        and best.vector_rank <= STOP_BOTH_RANK
        and best.bm25_rank <= STOP_BOTH_RANK
    ):
        # Skip reranking for high-confidence cases — go straight to generation.
        logger.info("[%s] early_exit: high confidence (rrf=%.4f, v_rank=%d, b_rank=%d)",
                    corr_id, best.rrf_score, best.vector_rank, best.bm25_rank)
        top_sources = sources[:top_k]
    else:
        # Standard path: rerank first.
        logger.info("[%s] reranking sources", corr_id)
        reranked = await rerank_sources(ai_provider, retrieval_query, sources)
        top_sources = reranked[:top_k]

    context = await assemble_context(top_sources)
    logger.info("[%s] assemble_context: %d chars, %d sources", corr_id, len(context), len(top_sources))

    result = await generate_chat_response(
        ai_provider, question, context, owner_name, top_sources, lang=lang
    )

    if result is None:
        logger.error("[%s] generate_chat_response failed", corr_id)
        return {
            "answer": FALLBACK_ERROR,
            "status": "error",
            "sources": [],
            "citations": [],
        }

    answer, citations = result

    # ---- Strict Citation Validation ----
    citation_valid = await validate_answer_citations(ai_provider, answer, top_sources)
    logger.info("[%s] citation_validation: %s", corr_id, "PASS" if citation_valid else "FAIL")
    if not citation_valid:
        # Answer failed validation — regenerate with a stricter prompt.
        strict_messages = [
            {
                "role": "system",
                "content": (
                    f"You are the AI assistant for {owner_name}'s professional portfolio. "
                    "STRICT: Only use the provided context. Do NOT add any information "
                    "not directly supported by the context. If the context is insufficient, "
                    f"say so and offer to contact {owner_name} directly. "
                    "Never invent personal facts."
                ),
            },
            {
                "role": "user",
                "content": f"Context:\n{context}\n\nQuestion: {question}\n\n"
                "Answer using ONLY the context above. If you cannot answer from the "
                "context, say 'I don't have that information in the profile.'",
            },
        ]
        try:
            answer = await ai_provider.chat(strict_messages)
        except AIProviderError:
            return {
                "answer": FALLBACK_NO_ANSWER.format(name=owner_name),
                "status": "no_answer",
                "sources": [],
                "citations": [],
            }
        citations = await validate_citations(answer, top_sources)

    logger.info("[%s] RAG pipeline complete: status=answered, answer_len=%d", corr_id, len(answer))

    return {
        "answer": answer,
        "status": "answered",
        "sources": [
            {
                "source_type": src.source_type,
                "source_id": src.source_id,
                "score": src.score,
            }
            for src in top_sources
        ],
        "citations": citations,
    }


async def get_owner_name(session: AsyncSession) -> str:
    profile = await session.scalar(select(models.Profile).limit(1))
    if profile and profile.name:
        return profile.name
    return DEFAULT_OWNER_NAME


async def classify_scope(
    ai_provider: AIProvider,
    question: str,
    owner_name: str,
) -> bool:
    """Professional Scope Filter: lightweight LLM YES/NO classification.

    Returns True if the question is in-scope (about the owner's professional
    profile). Fails open on provider errors, since the similarity gate and
    generation step downstream still guard against hallucinated answers.
    """
    messages = [
        {
            "role": "system",
            "content": "You are a strict binary classifier. Answer with exactly one word: YES or NO.",
        },
        {
            "role": "user",
            "content": (
                f"Is this question about {owner_name}'s professional profile "
                "(identity, skills, experience, education, courses, certificates, "
                f"projects, technologies, work details, or contact info)? "
                f"Question: {question}\nAnswer YES or NO only."
            ),
        },
    ]
    try:
        reply = await ai_provider.chat(messages)
    except AIProviderError:
        return True
    normalized = reply.strip().upper()
    if "NO" in normalized and "YES" not in normalized:
        return False
    return True


async def plan_query(
    ai_provider: AIProvider,
    question: str,
    owner_name: str,
) -> dict[str, Any]:
    """Query Planner + Query Rewrite stage.

    Runs after the scope filter and before hybrid retrieval, per the locked
    pipeline order in NEXT_AGENT.md (Scope Filter -> Query Planner -> Query
    Rewrite -> Hybrid Retrieval). Produces:

    - rewritten_query: retrieval-optimized rewrite (resolves pronouns,
      expands abbreviations, drops filler) — fed to embed/retrieve/rerank.
    - original_query: preserved for the generation step (answers stay in
      the user's own phrasing).
    - complexity: 'low' | 'medium' | 'high' — drives the dynamic retrieval
      budget (multiplies the base top_k).
    - needs_clarification: bool — True when the query is too ambiguous to
      retrieve confidently (e.g. "tell me about your work" with multiple
      experiences, or a vague multi-part question). When True, the caller
      should return the clarification_question without proceeding to
      retrieval.

    Fails open (rewritten == original, complexity='medium',
    needs_clarification=False) on provider error.
    """
    messages = [
        {
            "role": "system",
            "content": (
                f"You are a query planning assistant for a retrieval system grounded "
                f"in {owner_name}'s professional profile. Analyze the user's question "
                "and respond with EXACTLY three lines:\n"
                "Line 1: The rewritten retrieval-optimized query (resolve pronouns, "
                "expand abbreviations, drop filler words/greetings, keep factual and "
                "concise).\n"
                "Line 2: Complexity: LOW (targeted, single topic) | MEDIUM (standard) "
                "| HIGH (multi-part, comparative, or requires synthesis across topics).\n"
                "Line 3: Clarification needed: YES or NO (YES when the query is too "
                "broad, vague, or ambiguous to retrieve confidently — e.g. 'tell me "
                "about your work' when multiple experiences exist, or 'what did you "
                "build?' without specifying a project). Do NOT say YES for specific "
                "questions that have a clear answer.\n"
                "Respond with exactly three lines, nothing else."
            ),
        },
        {"role": "user", "content": question},
    ]
    try:
        reply = await ai_provider.chat(messages)
    except AIProviderError:
        return {
            "rewritten_query": question,
            "original_query": question,
            "complexity": "medium",
            "needs_clarification": False,
        }

    lines = [l.strip() for l in reply.strip().splitlines() if l.strip()]
    rewritten_query = lines[0] if len(lines) >= 1 else question
    complexity_raw = lines[1].lower() if len(lines) >= 2 else "medium"
    complexity = complexity_raw if complexity_raw in ("low", "medium", "high") else "medium"
    needs_clarification = "yes" in lines[2].lower() if len(lines) >= 3 else False

    return {
        "rewritten_query": rewritten_query,
        "original_query": question,
        "complexity": complexity,
        "needs_clarification": needs_clarification,
    }


def passes_similarity_gate(sources: list[RetrievalSource], threshold: float) -> bool:
    """Relevance Gate for hybrid retrieval results (RRF-scored) or legacy
    pgvector-only results (cosine-similarity-scored).

    For RRF-fused results (hybrid retrieval path):
      - Check that the best RRF score is meaningful (non-trivial presence from
        at least one strong retrieval method).
      - Dynamically scale the threshold: if both vector and BM25 found the top
        chunk, the bar is lower (threshold/80); if only one method contributed,
        require stronger evidence from that single method (threshold/50).
      - With default threshold=0.65: both_methods gate ≈ 0.008 RRF,
        single_method gate ≈ 0.013 RRF.
    For raw pgvector results (legacy retrieve_chunks path):
      - Convert cosine distance to similarity and compare against threshold.

    No chunks at all fails the gate regardless of path.
    """
    if not sources:
        logger.info("similarity_gate: FAIL (no sources)")
        return False

    best = sources[0]  # Already sorted by RRF score or similarity.

    # Hybrid retrieval path: RRF scores are set.
    if best.rrf_score is not None:
        rrf = best.rrf_score
        # Dynamic threshold: require stronger evidence when only one method contributed.
        both_methods = (best.vector_rank is not None) and (best.bm25_rank is not None)
        effective_threshold = threshold / 80.0 if both_methods else threshold / 50.0
        passed = rrf >= effective_threshold
        logger.info(
            "similarity_gate: %s (rrf=%.4f, threshold=%.4f, both_methods=%s, "
            "vector_rank=%s, bm25_rank=%s, num_sources=%d)",
            "PASS" if passed else "FAIL",
            rrf, effective_threshold, both_methods,
            best.vector_rank, best.bm25_rank, len(sources),
        )
        return passed

    # Legacy pgvector path: rrf_score not set; score is cosine *distance*
    # (0=identical, 1=opposite) so convert to similarity before threshold check.
    best_similarity = 1 - best.score
    passed = best_similarity >= threshold
    logger.info(
        "similarity_gate: %s (similarity=%.4f, threshold=%.4f, num_sources=%d)",
        "PASS" if passed else "FAIL",
        best_similarity, threshold, len(sources),
    )
    return passed
