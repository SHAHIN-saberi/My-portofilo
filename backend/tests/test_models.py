from app.db.base import Base
import app.db.models  # noqa: F401  # ensure models register on Base.metadata


def test_model_metadata_is_registered() -> None:
    expected_tables = {
        "profiles",
        "profile_translations",
        "skills",
        "skill_translations",
        "experiences",
        "experience_translations",
        "educations",
        "education_translations",
        "courses",
        "course_translations",
        "certificates",
        "certificate_translations",
        "projects",
        "project_translations",
        "project_skills",
        "social_links",
        "ai_knowledge_entries",
        "ai_knowledge_translations",
        "knowledge_chunks",
        "admin_users",
    }

    assert expected_tables.issubset(set(Base.metadata.tables))
