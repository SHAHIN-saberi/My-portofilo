from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import models
from app.schemas.common import Lang


def _choose_translation(translations: list[models.ProfileTranslation] | list[models.SkillTranslation] | list[models.ExperienceTranslation] | list[models.EducationTranslation] | list[models.CourseTranslation] | list[models.CertificateTranslation] | list[models.ProjectTranslation] | list[models.AIKnowledgeTranslation], lang: Lang):
    preferred = [item for item in translations if item.lang == lang]
    if preferred:
        return preferred[0]
    fallback = [item for item in translations if item.lang == "en"]
    if fallback:
        return fallback[0]
    return translations[0] if translations else None


async def get_profile(session: AsyncSession, lang: Lang) -> dict | None:
    profile = await session.scalar(select(models.Profile).limit(1))
    if profile is None:
        return None

    translations = (await session.execute(
        select(models.ProfileTranslation).where(
            models.ProfileTranslation.profile_id == profile.id,
            models.ProfileTranslation.lang.in_([lang, "en"]),
        )
    )).scalars().all()
    translation = _choose_translation(translations, lang)

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


async def list_skills(session: AsyncSession, lang: Lang, category: str | None = None) -> list[dict]:
    stmt = select(models.Skill)
    if category:
        stmt = stmt.where(models.Skill.category.ilike(f"%{category}%"))
    stmt = stmt.order_by(models.Skill.display_order)
    skills = (await session.execute(stmt)).scalars().all()
    skill_ids = [skill.id for skill in skills]

    translations = {}
    if skill_ids:
        rows = (await session.execute(
            select(models.SkillTranslation).where(
                models.SkillTranslation.skill_id.in_(skill_ids),
                models.SkillTranslation.lang.in_([lang, "en"]),
            )
        )).scalars().all()
        for row in rows:
            translations.setdefault(row.skill_id, []).append(row)

    output = []
    for skill in skills:
        translation = _choose_translation(translations.get(skill.id, []), lang)
        output.append(
            {
                "id": skill.id,
                "category": skill.category,
                "proficiency": skill.proficiency,
                "years_experience": float(skill.years_experience) if skill.years_experience is not None else None,
                "display_order": skill.display_order,
                "translation": {
                    "lang": translation.lang if translation else None,
                    "name": translation.name if translation else None,
                    "description": translation.description if translation else None,
                },
            }
        )
    return output


async def list_experiences(session: AsyncSession, lang: Lang) -> list[dict]:
    experiences = (await session.execute(
        select(models.Experience).order_by(models.Experience.display_order)
    )).scalars().all()
    experience_ids = [experience.id for experience in experiences]

    translations = {}
    if experience_ids:
        rows = (await session.execute(
            select(models.ExperienceTranslation).where(
                models.ExperienceTranslation.experience_id.in_(experience_ids),
                models.ExperienceTranslation.lang.in_([lang, "en"]),
            )
        )).scalars().all()
        for row in rows:
            translations.setdefault(row.experience_id, []).append(row)

    return [
        {
            "id": experience.id,
            "company": experience.company,
            "start_date": experience.start_date,
            "end_date": experience.end_date,
            "is_current": experience.is_current,
            "location": experience.location,
            "display_order": experience.display_order,
            "translation": {
                "lang": translation.lang if (translation := _choose_translation(translations.get(experience.id, []), lang)) else None,
                "role": translation.role if translation else None,
                "description": translation.description if translation else None,
            },
        }
        for experience in experiences
    ]


async def list_projects(session: AsyncSession, lang: Lang, featured: bool | None = None) -> list[dict]:
    stmt = select(models.Project)
    if featured is not None:
        stmt = stmt.where(models.Project.featured == featured)
    projects = (await session.execute(stmt.order_by(models.Project.display_order))).scalars().all()
    project_ids = [project.id for project in projects]

    translations = {}
    if project_ids:
        rows = (await session.execute(
            select(models.ProjectTranslation).where(
                models.ProjectTranslation.project_id.in_(project_ids),
                models.ProjectTranslation.lang.in_([lang, "en"]),
            )
        )).scalars().all()
        for row in rows:
            translations.setdefault(row.project_id, []).append(row)

    skill_map = {}
    if project_ids:
        rows = (await session.execute(
            select(models.ProjectSkill).where(models.ProjectSkill.project_id.in_(project_ids))
        )).scalars().all()
        for row in rows:
            skill_map.setdefault(row.project_id, []).append(row.skill_id)

    output = []
    for project in projects:
        translation = _choose_translation(translations.get(project.id, []), lang)
        output.append(
            {
                "id": project.id,
                "start_date": project.start_date,
                "end_date": project.end_date,
                "live_url": project.live_url,
                "github_url": project.github_url,
                "tech_stack": project.tech_stack,
                "featured": project.featured,
                "display_order": project.display_order,
                "skill_ids": skill_map.get(project.id, []),
                "translation": {
                    "lang": translation.lang if translation else None,
                    "title": translation.title if translation else None,
                    "description": translation.description if translation else None,
                    "role": translation.role if translation else None,
                    "impact": translation.impact if translation else None,
                },
            }
        )
    return output


async def list_education(session: AsyncSession, lang: Lang) -> list[dict]:
    educations = (await session.execute(select(models.Education).order_by(models.Education.display_order))).scalars().all()
    education_ids = [education.id for education in educations]

    translations = {}
    if education_ids:
        rows = (await session.execute(
            select(models.EducationTranslation).where(
                models.EducationTranslation.education_id.in_(education_ids),
                models.EducationTranslation.lang.in_([lang, "en"]),
            )
        )).scalars().all()
        for row in rows:
            translations.setdefault(row.education_id, []).append(row)

    return [
        {
            "id": education.id,
            "institution": education.institution,
            "start_date": education.start_date,
            "end_date": education.end_date,
            "location": education.location,
            "display_order": education.display_order,
            "translation": {
                "lang": translation.lang if (translation := _choose_translation(translations.get(education.id, []), lang)) else None,
                "degree": translation.degree if translation else None,
                "field_of_study": translation.field_of_study if translation else None,
                "description": translation.description if translation else None,
            },
        }
        for education in educations
    ]


async def list_courses(session: AsyncSession, lang: Lang) -> list[dict]:
    courses = (await session.execute(select(models.Course).order_by(models.Course.display_order))).scalars().all()
    course_ids = [course.id for course in courses]

    translations = {}
    if course_ids:
        rows = (await session.execute(
            select(models.CourseTranslation).where(
                models.CourseTranslation.course_id.in_(course_ids),
                models.CourseTranslation.lang.in_([lang, "en"]),
            )
        )).scalars().all()
        for row in rows:
            translations.setdefault(row.course_id, []).append(row)

    return [
        {
            "id": course.id,
            "provider": course.provider,
            "completion_date": course.completion_date,
            "credential_url": course.credential_url,
            "display_order": course.display_order,
            "translation": {
                "lang": translation.lang if (translation := _choose_translation(translations.get(course.id, []), lang)) else None,
                "title": translation.title if translation else None,
                "description": translation.description if translation else None,
            },
        }
        for course in courses
    ]


async def list_certificates(session: AsyncSession, lang: Lang) -> list[dict]:
    certificates = (await session.execute(select(models.Certificate).order_by(models.Certificate.display_order))).scalars().all()
    certificate_ids = [certificate.id for certificate in certificates]

    translations = {}
    if certificate_ids:
        rows = (await session.execute(
            select(models.CertificateTranslation).where(
                models.CertificateTranslation.certificate_id.in_(certificate_ids),
                models.CertificateTranslation.lang.in_([lang, "en"]),
            )
        )).scalars().all()
        for row in rows:
            translations.setdefault(row.certificate_id, []).append(row)

    return [
        {
            "id": certificate.id,
            "issuer": certificate.issuer,
            "issue_date": certificate.issue_date,
            "credential_url": certificate.credential_url,
            "display_order": certificate.display_order,
            "translation": {
                "lang": translation.lang if (translation := _choose_translation(translations.get(certificate.id, []), lang)) else None,
                "title": translation.title if translation else None,
                "description": translation.description if translation else None,
            },
        }
        for certificate in certificates
    ]


async def list_social_links(session: AsyncSession) -> list[dict]:
    links = (await session.execute(select(models.SocialLink).order_by(models.SocialLink.display_order))).scalars().all()
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
