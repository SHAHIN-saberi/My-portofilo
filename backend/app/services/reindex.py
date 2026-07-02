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
    rows: list[dict[str, Any]] = []

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

    skills = (await session.execute(select(models.Skill).order_by(models.Skill.display_order))).scalars().all()
    for skill in skills:
        translation = await session.scalar(
            select(models.SkillTranslation)
            .where(models.SkillTranslation.skill_id == skill.id)
            .where(models.SkillTranslation.lang == lang)
        )
        translation = translation or await session.scalar(
            select(models.SkillTranslation)
            .where(models.SkillTranslation.skill_id == skill.id)
            .where(models.SkillTranslation.lang == "en")
        )
        if translation:
            rows.append(
                {
                    "source_type": "skill",
                    "source_id": skill.id,
                    "lang": translation.lang,
                    "text": f"{translation.name}\n{translation.description or ''}",
                }
            )

    experiences = (await session.execute(select(models.Experience).order_by(models.Experience.display_order))).scalars().all()
    for experience in experiences:
        translation = await session.scalar(
            select(models.ExperienceTranslation)
            .where(models.ExperienceTranslation.experience_id == experience.id)
            .where(models.ExperienceTranslation.lang == lang)
        )
        translation = translation or await session.scalar(
            select(models.ExperienceTranslation)
            .where(models.ExperienceTranslation.experience_id == experience.id)
            .where(models.ExperienceTranslation.lang == "en")
        )
        if translation:
            rows.append(
                {
                    "source_type": "experience",
                    "source_id": experience.id,
                    "lang": translation.lang,
                    "text": f"{experience.company or ''}\n{translation.role}\n{translation.description or ''}",
                }
            )

    educations = (await session.execute(select(models.Education).order_by(models.Education.display_order))).scalars().all()
    for education in educations:
        translation = await session.scalar(
            select(models.EducationTranslation)
            .where(models.EducationTranslation.education_id == education.id)
            .where(models.EducationTranslation.lang == lang)
        )
        translation = translation or await session.scalar(
            select(models.EducationTranslation)
            .where(models.EducationTranslation.education_id == education.id)
            .where(models.EducationTranslation.lang == "en")
        )
        if translation:
            rows.append(
                {
                    "source_type": "education",
                    "source_id": education.id,
                    "lang": translation.lang,
                    "text": f"{education.institution or ''}\n{translation.degree}\n{translation.field_of_study or ''}\n{translation.description or ''}",
                }
            )

    courses = (await session.execute(select(models.Course).order_by(models.Course.display_order))).scalars().all()
    for course in courses:
        translation = await session.scalar(
            select(models.CourseTranslation)
            .where(models.CourseTranslation.course_id == course.id)
            .where(models.CourseTranslation.lang == lang)
        )
        translation = translation or await session.scalar(
            select(models.CourseTranslation)
            .where(models.CourseTranslation.course_id == course.id)
            .where(models.CourseTranslation.lang == "en")
        )
        if translation:
            rows.append(
                {
                    "source_type": "course",
                    "source_id": course.id,
                    "lang": translation.lang,
                    "text": f"{course.provider or ''}\n{translation.title}\n{translation.description or ''}",
                }
            )

    certificates = (await session.execute(select(models.Certificate).order_by(models.Certificate.display_order))).scalars().all()
    for certificate in certificates:
        translation = await session.scalar(
            select(models.CertificateTranslation)
            .where(models.CertificateTranslation.certificate_id == certificate.id)
            .where(models.CertificateTranslation.lang == lang)
        )
        translation = translation or await session.scalar(
            select(models.CertificateTranslation)
            .where(models.CertificateTranslation.certificate_id == certificate.id)
            .where(models.CertificateTranslation.lang == "en")
        )
        if translation:
            rows.append(
                {
                    "source_type": "certificate",
                    "source_id": certificate.id,
                    "lang": translation.lang,
                    "text": f"{certificate.issuer or ''}\n{translation.title}\n{translation.description or ''}",
                }
            )

    projects = (await session.execute(select(models.Project).order_by(models.Project.display_order))).scalars().all()
    for project in projects:
        translation = await session.scalar(
            select(models.ProjectTranslation)
            .where(models.ProjectTranslation.project_id == project.id)
            .where(models.ProjectTranslation.lang == lang)
        )
        translation = translation or await session.scalar(
            select(models.ProjectTranslation)
            .where(models.ProjectTranslation.project_id == project.id)
            .where(models.ProjectTranslation.lang == "en")
        )
        if translation:
            tech_text = ", ".join(project.tech_stack or [])
            rows.append(
                {
                    "source_type": "project",
                    "source_id": project.id,
                    "lang": translation.lang,
                    "text": f"{translation.title or ''}\n{translation.description or ''}\n{translation.role or ''}\n{translation.impact or ''}\n{tech_text}",
                }
            )

    social_links = (await session.execute(select(models.SocialLink).order_by(models.SocialLink.display_order))).scalars().all()
    for link in social_links:
        rows.append(
            {
                "source_type": "social_link",
                "source_id": link.id,
                "lang": lang,
                "text": f"{link.platform}: {link.url}",
            }
        )

    ai_entries = (await session.execute(select(models.AIKnowledgeEntry).order_by(models.AIKnowledgeEntry.display_order))).scalars().all()
    for entry in ai_entries:
        translation = await session.scalar(
            select(models.AIKnowledgeTranslation)
            .where(models.AIKnowledgeTranslation.entry_id == entry.id)
            .where(models.AIKnowledgeTranslation.lang == lang)
        )
        translation = translation or await session.scalar(
            select(models.AIKnowledgeTranslation)
            .where(models.AIKnowledgeTranslation.entry_id == entry.id)
            .where(models.AIKnowledgeTranslation.lang == "en")
        )
        if translation:
            rows.append(
                {
                    "source_type": "ai_knowledge",
                    "source_id": entry.id,
                    "lang": translation.lang,
                    "text": f"{translation.title or ''}\n{translation.content}",
                }
            )

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
    # tsvector columns (search_vector_en, search_vector_fa) are populated
    # automatically by the DB trigger; Python side leaves them as NULL.
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
    # Clear existing chunks for the target language
    await session.execute(delete(models.KnowledgeChunk).where(models.KnowledgeChunk.lang == lang))
    sources = await _gather_sources(session, lang)
    chunks: list[models.KnowledgeChunk] = []
    for source in sources:
        chunks.extend(await _create_chunks_from_source(session, ai_provider, source))
    session.add_all(chunks)
    await session.commit()
    return len(chunks)
