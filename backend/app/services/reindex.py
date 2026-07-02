from __future__ import annotations

from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.db import models
from app.services.ai_provider.base import AIProvider


async def _chunk_texts_for_source(
    source_type: str,
    source_id: int,
    lang: str,
    text: str,
    max_chunk_size: int = 500,
) -> list[dict[str, Any]]:
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks: list[dict[str, Any]] = []
    for paragraph in paragraphs:
        if len(paragraph) <= max_chunk_size:
            chunks.append({"chunk_text": paragraph, "source_type": source_type, "source_id": source_id, "lang": lang})
            continue
        start = 0
        while start < len(paragraph):
            end = min(start + max_chunk_size, len(paragraph))
            chunks.append(
                {
                    "chunk_text": paragraph[start:end].strip(),
                    "source_type": source_type,
                    "source_id": source_id,
                    "lang": lang,
                }
            )
            start = end
    return chunks


async def _gather_sources(session: AsyncSession, lang: str) -> list[dict[str, Any]]:
    rows = []

    profile = await session.scalar(select(models.Profile).limit(1))
    if profile:
        translation = await session.scalar(
            select(models.ProfileTranslation)
            .where(models.ProfileTranslation.profile_id == profile.id)
            .where(models.ProfileTranslation.lang == lang)
        )
        translation = translation or await session.scalar(
            select(models.ProfileTranslation)
            .where(models.ProfileTranslation.profile_id == profile.id)
            .where(models.ProfileTranslation.lang == "en")
        )
        if translation:
            rows.append(
                {
                    "source_type": "profile",
                    "source_id": profile.id,
                    "lang": translation.lang,
                    "text": f"{translation.title or ''}\n{translation.summary or ''}\n{translation.bio or ''}",
                }
            )

    # The following query implementations should be repeated for each entity domain.
    return rows


async def _create_chunks_from_source(
    session: AsyncSession,
    ai_provider: AIProvider,
    source: dict[str, Any],
) -> list[models.KnowledgeChunk]:
    chunks_data = await _chunk_texts_for_source(
        source_type=source["source_type"],
        source_id=source["source_id"],
        lang=source["lang"],
        text=source["text"],
    )
    if not chunks_data:
        return []

    embeddings = await ai_provider.embed_batch([chunk["chunk_text"] for chunk in chunks_data])
    created = []
    for chunk_data, embedding in zip(chunks_data, embeddings):
        created.append(
            models.KnowledgeChunk(
                source_type=chunk_data["source_type"],
                source_id=chunk_data["source_id"],
                lang=chunk_data["lang"],
                chunk_text=chunk_data["chunk_text"],
                extra_metadata=None,
                embedding=embedding,
            )
        )
    return created


async def reindex_all(
    session: AsyncSession,
    ai_provider: AIProvider,
    settings: Settings,
    lang: str,
) -> int:
    await session.execute(delete(models.KnowledgeChunk).where(models.KnowledgeChunk.lang == lang))
    sources = await _gather_sources(session, lang)
    chunks: list[models.KnowledgeChunk] = []
    for source in sources:
        chunks.extend(await _create_chunks_from_source(session, ai_provider, source))
    session.add_all(chunks)
    await session.commit()
    return len(chunks)
