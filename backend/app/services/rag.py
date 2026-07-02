from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sqlalchemy import cast, func, literal, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.db import models
from app.services.ai_provider.base import AIProvider, AIProviderError


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
    lang: str,
    sources: list[RetrievalSource],
) -> tuple[str, list[str]]:
    system_prompt = (
        "You are an assistant that answers questions only using the provided owner-specific knowledge. "
        "Do not hallucinate new facts. If the answer is unknown, say so and suggest contacting the owner."
    )
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"},
    ]
    try:
        answer = await ai_provider.chat(messages, context=None)
    except AIProviderError as exc:
        return (
            "I'm sorry, I couldn't generate an answer right now. Please try again later.",
            [],
        )

    citations = await validate_citations(answer, sources)
    return answer, citations


async def build_question_answer(
    session: AsyncSession,
    ai_provider: AIProvider,
    question: str,
    lang: str,
    top_k: int,
) -> dict[str, Any]:
    embedding = await embed_query(question, ai_provider)
    sources = await retrieve_chunks(session, embedding, lang, top_k=top_k)
    reranked = await rerank_sources(ai_provider, question, sources)
    context = await assemble_context(reranked[: top_k])
    answer, citations = await generate_chat_response(ai_provider, question, context, lang, reranked[:top_k])
    return {
        "answer": answer,
        "status": "answered" if answer else "no_answer",
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


async def context_relevance_filter(
    session: AsyncSession,
    question: str,
    top_k: int = 10,
) -> bool:
    question_words = set(question.lower().split())
    chunks = (await session.execute(select(models.KnowledgeChunk).limit(10))).scalars().all()
    for chunk in chunks:
        if any(word in chunk.chunk_text.lower() for word in question_words):
            return True
    return bool(chunks)
