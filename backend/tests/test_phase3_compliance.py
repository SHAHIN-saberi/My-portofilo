import re

from sqlalchemy import UniqueConstraint
from sqlalchemy.sql.schema import PrimaryKeyConstraint

import app.db.models as models


def test_phase3_required_tables_and_translations_exist() -> None:
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

    actual_tables = set(models.Base.metadata.tables)
    assert expected_tables <= actual_tables


def test_phase3_relationships_and_constraints() -> None:
    project_skill_table = models.ProjectSkill.__table__
    assert project_skill_table.primary_key
    assert {col.name for col in project_skill_table.primary_key.columns} == {"project_id", "skill_id"}

    profile_translation_constraints = {
        constraint.name for constraint in models.ProfileTranslation.__table__.constraints
        if isinstance(constraint, UniqueConstraint)
    }
    assert "uq_profile_lang" in profile_translation_constraints

    assert models.AdminUser.__table__.c.email.unique
    assert models.Project.__table__.c.tech_stack.type.__class__.__name__ == "ARRAY"


def test_knowledge_chunk_indexes_and_vector_dimensions() -> None:
    table = models.KnowledgeChunk.__table__
    index_names = {index.name for index in table.indexes}
    assert "idx_knowledge_chunks_embedding" in index_names
    assert "idx_knowledge_chunks_source" in index_names
    assert "idx_knowledge_chunks_lang" in index_names

    embedding_type = table.c.embedding.type
    assert "VECTOR" in embedding_type.__class__.__name__.upper()
    assert getattr(embedding_type, "dim", None) == 1024

    assert "metadata" in table.c
    assert table.c.metadata.type.__class__.__name__.upper() == "JSONB"


def test_migration_includes_pgvector_setup() -> None:
    with open(
        "backend/alembic/versions/0001_initial.py",
        encoding="utf-8",
    ) as source_file:
        source = source_file.read()

    assert "CREATE EXTENSION IF NOT EXISTS vector" in source
    assert re.search(r"Vector\(1024\)", source)
    assert "vector_cosine_ops" in source
    assert "idx_knowledge_chunks_embedding" in source
    assert "idx_knowledge_chunks_source" in source
    assert "idx_knowledge_chunks_lang" in source
