from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db import models
from app.schemas.content import (
    AIKnowledgeEntryPayload,
    CertificatePayload,
    CoursePayload,
    EducationPayload,
    ExperiencePayload,
    ProjectPayload,
    ProfilePayload,
    SkillPayload,
    SocialLinkPayload,
)


def _populate_translations(parent, translation_cls, payloads):
    """
    Merge/update translations per-language instead of replacing all.
    
    This prevents data loss when doing partial updates (e.g., updating only
    the Persian translation should not delete the English translation).
    """
    # Build a map of existing translations by lang
    existing_map = {t.lang: t for t in parent.translations}
    
    # Process each payload
    for payload in payloads:
        data = payload.model_dump(exclude_none=True)
        lang = data.get('lang')
        
        if lang in existing_map:
            # Update existing translation
            existing = existing_map[lang]
            for key, value in data.items():
                if key != 'lang':  # Don't change the lang
                    setattr(existing, key, value)
        else:
            # Create new translation
            parent.translations.append(translation_cls(**data))


async def _set_project_skills(session: AsyncSession, project: models.Project, skill_ids: list[int] | None) -> None:
    if skill_ids is None:
        return
    if not skill_ids:
        project.skills = []
        return
    skills = (await session.execute(select(models.Skill).where(models.Skill.id.in_(skill_ids)))).scalars().all()
    project.skills = [models.ProjectSkill(skill=skill) for skill in skills]


async def get_profile(session: AsyncSession, lang: str) -> dict | None:
    profile = await session.scalar(select(models.Profile).limit(1))
    if not profile:
        return None
    translations = (await session.execute(
        select(models.ProfileTranslation).where(
            models.ProfileTranslation.profile_id == profile.id,
            models.ProfileTranslation.lang.in_([lang, "en"]),
        )
    )).scalars().all()
    translation = None
    for item in translations:
        if item.lang == lang:
            translation = item
            break
    if translation is None and translations:
        translation = translations[0]
    return {
        "id": profile.id,
        "name": profile.name,
        "photo_url": profile.photo_url,
        "email": profile.email,
        "phone": profile.phone,
        "location": profile.location,
        "availability_status": profile.availability_status,
        "github_url": profile.github_url,
        "linkedin_url": profile.linkedin_url,
        "website_url": profile.website_url,
        "cv_pdf_url": profile.cv_pdf_url,
        "translation": {
            "lang": translation.lang if translation else None,
            "title": translation.title if translation else None,
            "summary": translation.summary if translation else None,
            "bio": translation.bio if translation else None,
        },
    }


async def update_profile(session: AsyncSession, payload: ProfilePayload) -> dict:
    profile = await session.scalar(select(models.Profile).limit(1))
    if profile is None:
        profile = models.Profile(**payload.model_dump(exclude_none=True, exclude={"translations"}))
    else:
        for key, value in payload.model_dump(exclude_none=True, exclude={"translations"}).items():
            setattr(profile, key, value)

    if payload.translations:
        _populate_translations(profile, models.ProfileTranslation, payload.translations)

    session.add(profile)
    await session.commit()
    await session.refresh(profile)
    return await get_profile(session, payload.translations[0].lang if payload.translations else "en")


async def list_skills(session: AsyncSession, limit: int = 100, offset: int = 0) -> list[dict]:
    skills = (await session.execute(
        select(models.Skill)
        .options(selectinload(models.Skill.translations))
        .order_by(models.Skill.display_order)
        .limit(limit)
        .offset(offset)
    )).scalars().all()
    result = []
    for skill in skills:
        result.append(
            {
                "id": skill.id,
                "category": skill.category,
                "proficiency": skill.proficiency,
                "years_experience": float(skill.years_experience) if skill.years_experience is not None else None,
                "display_order": skill.display_order,
                "translations": [
                    {
                        "lang": translation.lang,
                        "name": translation.name,
                        "description": translation.description,
                    }
                    for translation in skill.translations
                ],
            }
        )
    return result


async def create_skill(session: AsyncSession, payload: SkillPayload) -> dict:
    skill = models.Skill(**payload.model_dump(exclude_none=True, exclude={"translations"}))
    if payload.translations:
        _populate_translations(skill, models.SkillTranslation, payload.translations)
    session.add(skill)
    await session.commit()
    await session.refresh(skill)
    return {"id": skill.id}


async def update_skill(session: AsyncSession, skill_id: int, payload: SkillPayload) -> dict:
    skill = await session.scalar(select(models.Skill).where(models.Skill.id == skill_id))
    if skill is None:
        raise ValueError("Skill not found")
    for key, value in payload.model_dump(exclude_none=True, exclude={"translations"}).items():
        setattr(skill, key, value)
    if payload.translations:
        _populate_translations(skill, models.SkillTranslation, payload.translations)
    session.add(skill)
    await session.commit()
    return {"id": skill.id}


async def delete_skill(session: AsyncSession, skill_id: int) -> None:
    await session.execute(delete(models.Skill).where(models.Skill.id == skill_id))
    await session.commit()


async def list_experiences(session: AsyncSession, limit: int = 100, offset: int = 0) -> list[dict]:
    experiences = (
        await session.execute(
            select(models.Experience)
            .options(selectinload(models.Experience.translations))
            .order_by(models.Experience.display_order)
            .limit(limit)
            .offset(offset)
        )
    ).scalars().all()
    result = []
    for experience in experiences:
        result.append(
            {
                "id": experience.id,
                "company": experience.company,
                "start_date": experience.start_date,
                "end_date": experience.end_date,
                "is_current": experience.is_current,
                "location": experience.location,
                "display_order": experience.display_order,
                "translations": [
                    {
                        "lang": translation.lang,
                        "role": translation.role,
                        "description": translation.description,
                    }
                    for translation in experience.translations
                ],
            }
        )
    return result


async def create_experience(session: AsyncSession, payload: ExperiencePayload) -> dict:
    experience = models.Experience(**payload.model_dump(exclude_none=True, exclude={"translations"}))
    if payload.translations:
        _populate_translations(experience, models.ExperienceTranslation, payload.translations)
    session.add(experience)
    await session.commit()
    await session.refresh(experience)
    return {"id": experience.id}


async def update_experience(session: AsyncSession, experience_id: int, payload: ExperiencePayload) -> dict:
    experience = await session.scalar(select(models.Experience).where(models.Experience.id == experience_id))
    if experience is None:
        raise ValueError("Experience not found")
    for key, value in payload.model_dump(exclude_none=True, exclude={"translations"}).items():
        setattr(experience, key, value)
    if payload.translations:
        _populate_translations(experience, models.ExperienceTranslation, payload.translations)
    session.add(experience)
    await session.commit()
    return {"id": experience.id}


async def delete_experience(session: AsyncSession, experience_id: int) -> None:
    await session.execute(delete(models.Experience).where(models.Experience.id == experience_id))
    await session.commit()


async def list_education(session: AsyncSession, limit: int = 100, offset: int = 0) -> list[dict]:
    educations = (
        await session.execute(
            select(models.Education)
            .options(selectinload(models.Education.translations))
            .order_by(models.Education.display_order)
            .limit(limit)
            .offset(offset)
        )
    ).scalars().all()
    result = []
    for education in educations:
        result.append(
            {
                "id": education.id,
                "institution": education.institution,
                "start_date": education.start_date,
                "end_date": education.end_date,
                "location": education.location,
                "display_order": education.display_order,
                "translations": [
                    {
                        "lang": translation.lang,
                        "degree": translation.degree,
                        "field_of_study": translation.field_of_study,
                        "description": translation.description,
                    }
                    for translation in education.translations
                ],
            }
        )
    return result


async def create_education(session: AsyncSession, payload: EducationPayload) -> dict:
    education = models.Education(**payload.model_dump(exclude_none=True, exclude={"translations"}))
    if payload.translations:
        _populate_translations(education, models.EducationTranslation, payload.translations)
    session.add(education)
    await session.commit()
    await session.refresh(education)
    return {"id": education.id}


async def update_education(session: AsyncSession, education_id: int, payload: EducationPayload) -> dict:
    education = await session.scalar(select(models.Education).where(models.Education.id == education_id))
    if education is None:
        raise ValueError("Education not found")
    for key, value in payload.model_dump(exclude_none=True, exclude={"translations"}).items():
        setattr(education, key, value)
    if payload.translations:
        _populate_translations(education, models.EducationTranslation, payload.translations)
    session.add(education)
    await session.commit()
    return {"id": education.id}


async def delete_education(session: AsyncSession, education_id: int) -> None:
    await session.execute(delete(models.Education).where(models.Education.id == education_id))
    await session.commit()


async def list_courses(session: AsyncSession, limit: int = 100, offset: int = 0) -> list[dict]:
    courses = (
        await session.execute(
            select(models.Course)
            .options(selectinload(models.Course.translations))
            .order_by(models.Course.display_order)
            .limit(limit)
            .offset(offset)
        )
    ).scalars().all()
    result = []
    for course in courses:
        result.append(
            {
                "id": course.id,
                "provider": course.provider,
                "completion_date": course.completion_date,
                "credential_url": course.credential_url,
                "display_order": course.display_order,
                "translations": [
                    {
                        "lang": translation.lang,
                        "title": translation.title,
                        "description": translation.description,
                    }
                    for translation in course.translations
                ],
            }
        )
    return result


async def create_course(session: AsyncSession, payload: CoursePayload) -> dict:
    course = models.Course(**payload.model_dump(exclude_none=True, exclude={"translations"}))
    if payload.translations:
        _populate_translations(course, models.CourseTranslation, payload.translations)
    session.add(course)
    await session.commit()
    await session.refresh(course)
    return {"id": course.id}


async def update_course(session: AsyncSession, course_id: int, payload: CoursePayload) -> dict:
    course = await session.scalar(select(models.Course).where(models.Course.id == course_id))
    if course is None:
        raise ValueError("Course not found")
    for key, value in payload.model_dump(exclude_none=True, exclude={"translations"}).items():
        setattr(course, key, value)
    if payload.translations:
        _populate_translations(course, models.CourseTranslation, payload.translations)
    session.add(course)
    await session.commit()
    return {"id": course.id}


async def delete_course(session: AsyncSession, course_id: int) -> None:
    await session.execute(delete(models.Course).where(models.Course.id == course_id))
    await session.commit()


async def list_certificates(session: AsyncSession, limit: int = 100, offset: int = 0) -> list[dict]:
    certificates = (
        await session.execute(
            select(models.Certificate)
            .options(selectinload(models.Certificate.translations))
            .order_by(models.Certificate.display_order)
            .limit(limit)
            .offset(offset)
        )
    ).scalars().all()
    result = []
    for certificate in certificates:
        result.append(
            {
                "id": certificate.id,
                "issuer": certificate.issuer,
                "issue_date": certificate.issue_date,
                "credential_url": certificate.credential_url,
                "display_order": certificate.display_order,
                "translations": [
                    {
                        "lang": translation.lang,
                        "title": translation.title,
                        "description": translation.description,
                    }
                    for translation in certificate.translations
                ],
            }
        )
    return result


async def create_certificate(session: AsyncSession, payload: CertificatePayload) -> dict:
    certificate = models.Certificate(**payload.model_dump(exclude_none=True, exclude={"translations"}))
    if payload.translations:
        _populate_translations(certificate, models.CertificateTranslation, payload.translations)
    session.add(certificate)
    await session.commit()
    await session.refresh(certificate)
    return {"id": certificate.id}


async def update_certificate(session: AsyncSession, certificate_id: int, payload: CertificatePayload) -> dict:
    certificate = await session.scalar(select(models.Certificate).where(models.Certificate.id == certificate_id))
    if certificate is None:
        raise ValueError("Certificate not found")
    for key, value in payload.model_dump(exclude_none=True, exclude={"translations"}).items():
        setattr(certificate, key, value)
    if payload.translations:
        _populate_translations(certificate, models.CertificateTranslation, payload.translations)
    session.add(certificate)
    await session.commit()
    return {"id": certificate.id}


async def delete_certificate(session: AsyncSession, certificate_id: int) -> None:
    await session.execute(delete(models.Certificate).where(models.Certificate.id == certificate_id))
    await session.commit()


async def list_projects(session: AsyncSession, limit: int = 100, offset: int = 0) -> list[dict]:
    projects = (
        await session.execute(
            select(models.Project)
            .options(
                selectinload(models.Project.translations),
                selectinload(models.Project.skills),
            )
            .order_by(models.Project.display_order)
            .limit(limit)
            .offset(offset)
        )
    ).scalars().all()
    result = []
    for project in projects:
        result.append(
            {
                "id": project.id,
                "start_date": project.start_date,
                "end_date": project.end_date,
                "live_url": project.live_url,
                "github_url": project.github_url,
                "tech_stack": project.tech_stack,
                "featured": project.featured,
                "display_order": project.display_order,
                "skill_ids": [link.skill_id for link in project.skills],
                "translations": [
                    {
                        "lang": translation.lang,
                        "title": translation.title,
                        "short_description": translation.short_description,
                        "description": translation.description,
                        "role": translation.role,
                        "impact": translation.impact,
                    }
                    for translation in project.translations
                ],
            }
        )
    return result


async def create_project(session: AsyncSession, payload: ProjectPayload) -> dict:
    data = payload.model_dump(exclude_none=True, exclude={"translations", "skill_ids"})
    project = models.Project(**data)
    if payload.translations:
        _populate_translations(project, models.ProjectTranslation, payload.translations)
    await _set_project_skills(session, project, payload.skill_ids)
    session.add(project)
    await session.commit()
    await session.refresh(project)
    return {"id": project.id}


async def update_project(session: AsyncSession, project_id: int, payload: ProjectPayload) -> dict:
    project = await session.scalar(select(models.Project).where(models.Project.id == project_id))
    if project is None:
        raise ValueError("Project not found")
    for key, value in payload.model_dump(exclude_none=True, exclude={"translations", "skill_ids"}).items():
        setattr(project, key, value)
    if payload.translations:
        _populate_translations(project, models.ProjectTranslation, payload.translations)
    await _set_project_skills(session, project, payload.skill_ids)
    session.add(project)
    await session.commit()
    return {"id": project.id}


async def delete_project(session: AsyncSession, project_id: int) -> None:
    await session.execute(delete(models.Project).where(models.Project.id == project_id))
    await session.commit()


async def list_social_links(session: AsyncSession, limit: int = 100, offset: int = 0) -> list[dict]:
    links = (
        await session.execute(
            select(models.SocialLink)
            .order_by(models.SocialLink.display_order)
            .limit(limit)
            .offset(offset)
        )
    ).scalars().all()
    return [
        {
            "id": link.id,
            "platform": link.platform,
            "url": link.url,
            "display_order": link.display_order,
            "is_visible": link.is_visible,
        }
        for link in links
    ]


async def create_social_link(session: AsyncSession, payload: SocialLinkPayload) -> dict:
    link = models.SocialLink(**payload.model_dump(exclude_none=True))
    session.add(link)
    await session.commit()
    await session.refresh(link)
    return {"id": link.id}


async def update_social_link(session: AsyncSession, social_link_id: int, payload: SocialLinkPayload) -> dict:
    link = await session.scalar(select(models.SocialLink).where(models.SocialLink.id == social_link_id))
    if link is None:
        raise ValueError("Social link not found")
    for key, value in payload.model_dump(exclude_none=True).items():
        setattr(link, key, value)
    session.add(link)
    await session.commit()
    return {"id": link.id}


async def delete_social_link(session: AsyncSession, social_link_id: int) -> None:
    await session.execute(delete(models.SocialLink).where(models.SocialLink.id == social_link_id))
    await session.commit()


async def list_ai_knowledge_entries(session: AsyncSession, limit: int = 100, offset: int = 0) -> list[dict]:
    entries = (
        await session.execute(
            select(models.AIKnowledgeEntry)
            .options(selectinload(models.AIKnowledgeEntry.translations))
            .order_by(models.AIKnowledgeEntry.display_order)
            .limit(limit)
            .offset(offset)
        )
    ).scalars().all()
    result = []
    for entry in entries:
        result.append(
            {
                "id": entry.id,
                "display_order": entry.display_order,
                "translations": [
                    {
                        "lang": translation.lang,
                        "title": translation.title,
                        "content": translation.content,
                    }
                    for translation in entry.translations
                ],
            }
        )
    return result


async def create_ai_knowledge_entry(session: AsyncSession, payload: AIKnowledgeEntryPayload) -> dict:
    entry = models.AIKnowledgeEntry(**payload.model_dump(exclude_none=True, exclude={"translations"}))
    if payload.translations:
        _populate_translations(entry, models.AIKnowledgeTranslation, payload.translations)
    session.add(entry)
    await session.commit()
    await session.refresh(entry)
    return {"id": entry.id}


async def update_ai_knowledge_entry(session: AsyncSession, entry_id: int, payload: AIKnowledgeEntryPayload) -> dict:
    entry = await session.scalar(select(models.AIKnowledgeEntry).where(models.AIKnowledgeEntry.id == entry_id))
    if entry is None:
        raise ValueError("AI knowledge entry not found")
    for key, value in payload.model_dump(exclude_none=True, exclude={"translations"}).items():
        setattr(entry, key, value)
    if payload.translations:
        _populate_translations(entry, models.AIKnowledgeTranslation, payload.translations)
    session.add(entry)
    await session.commit()
    return {"id": entry.id}


async def delete_ai_knowledge_entry(session: AsyncSession, entry_id: int) -> None:
    await session.execute(delete(models.AIKnowledgeEntry).where(models.AIKnowledgeEntry.id == entry_id))
    await session.commit()


async def knowledge_status(session: AsyncSession) -> dict:
    total_chunks = await session.scalar(select(func.count()).select_from(models.KnowledgeChunk))
    last_indexed = await session.scalar(select(func.max(models.KnowledgeChunk.created_at)))
    return {
        "chunk_count": int(total_chunks or 0),
        "last_indexed_at": last_indexed.isoformat() if last_indexed else None,
    }
