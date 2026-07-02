from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.db import models
from app.services.ai_provider.base import AIProvider, AIProviderError

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


@dataclass
class RetrievalSource:
    source_type: str
    source_id: int
    score: float
    chunk_text: str
    lang: str
    extra_metadata: dict[str, str] | None


async def embed_query(question: str, ai_provider: AIProvider) -> list[float]:
    return await ai_provider.embed(question)


async def retrieve_chunks(
    session: AsyncSession,
    query_embedding: list[float],
    lang: str,
    top_k: int = 6,
) -> list[RetrievalSource]:
    query = select(
        models.KnowledgeChunk,
        (models.KnowledgeChunk.embedding.op("<=>")(query_embedding)).label("score"),
    ).where(models.KnowledgeChunk.lang == lang)
    query = query.order_by(text("score")).limit(top_k)
    rows = await session.execute(query)
    primary = rows.all()

    if len(primary) < top_k and lang != "en":
        fallback_query = select(
            models.KnowledgeChunk,
            (models.KnowledgeChunk.embedding.op("<=>")(query_embedding)).label("score"),
        ).where(models.KnowledgeChunk.lang == "en")
        fallback_query = fallback_query.order_by(text("score")).limit(top_k - len(primary))
        fallback_rows = await session.execute(fallback_query)
        primary.extend(fallback_rows.all())

    sources: list[RetrievalSource] = []
    for chunk, score in primary:
        sources.append(
            RetrievalSource(
                source_type=chunk.source_type,
                source_id=chunk.source_id,
                score=float(score),
                chunk_text=chunk.chunk_text,
                lang=chunk.lang,
                extra_metadata=chunk.extra_metadata,
            )
        )
    return sources


async def assemble_context(sources: list[RetrievalSource]) -> str:
    if not sources:
        return ""
    segments = []
    for idx, source in enumerate(sources, start=1):
        segments.append(
            f"[{idx}] Source: {source.source_type}#{source.source_id} (lang={source.lang})\n{source.chunk_text.strip()}"
        )
    return "\n\n".join(segments)


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


async def validate_citations(answers: str, sources: list[RetrievalSource]) -> list[str]:
    citations = []
    for idx, source in enumerate(sources, start=1):
        citations.append(f"[{idx}] {source.source_type}#{source.source_id}")
    return citations


async def generate_chat_response(
    ai_provider: AIProvider,
    question: str,
    context: str,
    owner_name: str,
    sources: list[RetrievalSource],
) -> tuple[str, list[str]] | None:
    """Returns (answer, citations), or None if the provider call failed."""
    system_prompt = (
        f"You are the AI assistant for {owner_name}'s professional portfolio. "
        "Use the retrieved context below as your primary source of truth. You may "
        "use general knowledge only to explain technical concepts naturally (e.g. "
        "'React is a JavaScript library...'), but never invent personal facts, "
        f"dates, projects, or achievements about {owner_name}. If the context only "
        "partially answers the question, answer with what is available and clearly "
        "note the limitation, offering to contact the owner for more detail. Be "
        "concise, professional, and friendly, with light controlled humor only "
        "when appropriate. Never be careless or misleading."
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
    """Full decision flow: scope filter -> query planner/rewrite -> retrieval
    -> relevance gate -> rerank -> context -> generation -> citation
    validation, with the fallback behavior locked in spec section 10
    (Chatbot)."""
    owner_name = await get_owner_name(session)

    try:
        in_scope = await classify_scope(ai_provider, question, owner_name)
    except AIProviderError:
        in_scope = True

    if not in_scope:
        return {
            "answer": FALLBACK_UNRELATED.format(name=owner_name),
            "status": "unrelated",
            "sources": [],
            "citations": [],
        }

    plan = await plan_query(ai_provider, question, owner_name)
    retrieval_query = plan["rewritten_query"]

    try:
        embedding = await embed_query(retrieval_query, ai_provider)
    except AIProviderError:
        return {
            "answer": FALLBACK_ERROR,
            "status": "error",
            "sources": [],
            "citations": [],
        }

    sources = await retrieve_chunks(session, embedding, lang, top_k=top_k)

    if not passes_similarity_gate(sources, similarity_threshold):
        return {
            "answer": FALLBACK_NO_ANSWER.format(name=owner_name),
            "status": "no_answer",
            "sources": [],
            "citations": [],
        }

    reranked = await rerank_sources(ai_provider, retrieval_query, sources)
    context = await assemble_context(reranked[:top_k])
    result = await generate_chat_response(ai_provider, question, context, owner_name, reranked[:top_k])

    if result is None:
        return {
            "answer": FALLBACK_ERROR,
            "status": "error",
            "sources": [],
            "citations": [],
        }

    answer, citations = result
    return {
        "answer": answer,
        "status": "answered",
        "sources": [
            {
                "source_type": src.source_type,
                "source_id": src.source_id,
                "score": src.score,
            }
            for src in reranked[:top_k]
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
) -> dict[str, str]:
    """Query Planner + Query Rewrite stage.

    Runs after the scope filter and before hybrid retrieval, per the locked
    pipeline order in NEXT_AGENT.md (Scope Filter -> Query Planner -> Query
    Rewrite -> Hybrid Retrieval). Produces a single, retrieval-optimized
    rewrite of the user's raw question -- resolving pronouns, expanding
    abbreviations, dropping filler words/greetings -- so downstream
    pgvector/BM25 retrieval matches against cleaner search text.

    Only the rewritten query is used for embedding/retrieval/rerank; the
    original question is still what gets shown to the generation step and
    answered in the user's own words. Fails open (rewritten == original) on
    provider error, since retrieval against the raw question still works.
    """
    messages = [
        {
            "role": "system",
            "content": (
                "You are a query rewriting assistant for a retrieval system grounded "
                f"in {owner_name}'s professional profile. Rewrite the user's question "
                "into a single, self-contained search query optimized for retrieval: "
                "resolve pronouns, expand abbreviations, drop filler words and "
                "greetings, and keep it factual and concise. Respond with EXACTLY one "
                "line containing only the rewritten query -- no quotes, no commentary."
            ),
        },
        {"role": "user", "content": question},
    ]
    try:
        reply = await ai_provider.chat(messages)
    except AIProviderError:
        return {"rewritten_query": question, "original_query": question}

    first_line = reply.strip().splitlines()[0].strip().strip('"') if reply.strip() else ""
    rewritten_query = first_line or question
    return {"rewritten_query": rewritten_query, "original_query": question}


def passes_similarity_gate(sources: list[RetrievalSource], threshold: float) -> bool:
    """Relevance Gate: pgvector `<=>` returns cosine *distance* (0 = identical).

    Convert the closest match to a similarity score and compare against the
    configured threshold. No chunks at all also fails the gate.
    """
    if not sources:
        return False
    best_distance = min(source.score for source in sources)
    best_similarity = 1 - best_distance
    return best_similarity >= threshold
