"""create initial schema

Revision ID: 0001_initial
Revises: 
Create Date: 2026-07-01 03:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector;")

    op.create_table(
        "profiles",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=128), nullable=True),
        sa.Column("photo_url", sa.String(length=512), nullable=True),
        sa.Column("email", sa.String(length=256), nullable=True),
        sa.Column("phone", sa.String(length=64), nullable=True),
        sa.Column("location", sa.String(length=128), nullable=True),
        sa.Column("availability_status", sa.String(length=128), nullable=True),
        sa.Column("github_url", sa.String(length=512), nullable=True),
        sa.Column("linkedin_url", sa.String(length=512), nullable=True),
        sa.Column("website_url", sa.String(length=512), nullable=True),
        sa.Column("cv_pdf_url", sa.String(length=512), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    op.create_table(
        "profile_translations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("profile_id", sa.Integer(), sa.ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("lang", sa.String(length=2), nullable=False),
        sa.Column("title", sa.Text(), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("bio", sa.Text(), nullable=True),
        sa.CheckConstraint("lang IN ('en', 'fa')", name="ck_profile_translations_lang"),
        sa.UniqueConstraint("profile_id", "lang", name="uq_profile_lang"),
    )

    op.create_table(
        "skills",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("category", sa.String(length=64), nullable=True),
        sa.Column("proficiency", sa.String(length=32), nullable=True),
        sa.Column("years_experience", sa.Numeric(4, 1), nullable=True),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint(
            "proficiency IN ('beginner','intermediate','advanced','expert')",
            name="ck_skills_proficiency",
        ),
    )

    op.create_table(
        "skill_translations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("skill_id", sa.Integer(), sa.ForeignKey("skills.id", ondelete="CASCADE"), nullable=False),
        sa.Column("lang", sa.String(length=2), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("description", sa.String(length=1024), nullable=True),
        sa.UniqueConstraint("skill_id", "lang", name="uq_skill_lang"),
    )

    op.create_table(
        "experiences",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("company", sa.String(length=256), nullable=False),
        sa.Column("start_date", sa.String(length=32), nullable=True),
        sa.Column("end_date", sa.String(length=32), nullable=True),
        sa.Column("is_current", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("location", sa.String(length=128), nullable=True),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    op.create_table(
        "experience_translations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("experience_id", sa.Integer(), sa.ForeignKey("experiences.id", ondelete="CASCADE"), nullable=False),
        sa.Column("lang", sa.String(length=2), nullable=False),
        sa.Column("role", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.UniqueConstraint("experience_id", "lang", name="uq_experience_lang"),
    )

    op.create_table(
        "educations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("institution", sa.String(length=256), nullable=False),
        sa.Column("start_date", sa.String(length=32), nullable=True),
        sa.Column("end_date", sa.String(length=32), nullable=True),
        sa.Column("location", sa.String(length=128), nullable=True),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
    )

    op.create_table(
        "education_translations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("education_id", sa.Integer(), sa.ForeignKey("educations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("lang", sa.String(length=2), nullable=False),
        sa.Column("description", sa.String(length=4096), nullable=True),
        sa.UniqueConstraint("education_id", "lang", name="uq_education_lang"),
    )

    op.create_table(
        "courses",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("provider", sa.String(length=256), nullable=True),
        sa.Column("completion_date", sa.String(length=32), nullable=True),
        sa.Column("credential_url", sa.String(length=512), nullable=True),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
    )

    op.create_table(
        "course_translations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("course_id", sa.Integer(), sa.ForeignKey("courses.id", ondelete="CASCADE"), nullable=False),
        sa.Column("lang", sa.String(length=2), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.UniqueConstraint("course_id", "lang", name="uq_course_lang"),
    )

    op.create_table(
        "certificates",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("issuer", sa.String(length=256), nullable=True),
        sa.Column("issue_date", sa.String(length=32), nullable=True),
        sa.Column("credential_url", sa.String(length=512), nullable=True),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
    )

    op.create_table(
        "certificate_translations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("certificate_id", sa.Integer(), sa.ForeignKey("certificates.id", ondelete="CASCADE"), nullable=False),
        sa.Column("lang", sa.String(length=2), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.UniqueConstraint("certificate_id", "lang", name="uq_certificate_lang"),
    )

    op.create_table(
        "projects",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("start_date", sa.String(length=32), nullable=True),
        sa.Column("end_date", sa.String(length=32), nullable=True),
        sa.Column("live_url", sa.String(length=512), nullable=True),
        sa.Column("github_url", sa.String(length=512), nullable=True),
        sa.Column("tech_stack", sa.ARRAY(sa.String(length=64)), nullable=True),
        sa.Column("featured", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    op.create_table(
        "project_translations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("project_id", sa.Integer(), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("lang", sa.String(length=2), nullable=False),
        sa.Column("title", sa.String(length=256), nullable=False),
        sa.Column("short_description", sa.String(length=1024), nullable=True),
        sa.Column("description", sa.String(length=4096), nullable=True),
        sa.Column("impact", sa.String(length=4096), nullable=True),
        sa.UniqueConstraint("project_id", "lang", name="uq_project_lang"),
    )

    op.create_table(
        "project_skills",
        sa.Column("project_id", sa.Integer(), sa.ForeignKey("projects.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("skill_id", sa.Integer(), sa.ForeignKey("skills.id", ondelete="CASCADE"), primary_key=True),
    )

    op.create_table(
        "social_links",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("platform", sa.String(length=128), nullable=False),
        sa.Column("url", sa.String(length=512), nullable=False),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_visible", sa.Boolean(), nullable=False, server_default=sa.text("true")),
    )

    op.create_table(
        "ai_knowledge_entries",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    op.create_table(
        "ai_knowledge_translations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("entry_id", sa.Integer(), sa.ForeignKey("ai_knowledge_entries.id", ondelete="CASCADE"), nullable=False),
        sa.Column("lang", sa.String(length=2), nullable=False),
        sa.Column("title", sa.Text(), nullable=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.UniqueConstraint("entry_id", "lang", name="uq_ai_knowledge_lang"),
    )

    op.create_table(
        "knowledge_chunks",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("source_type", sa.String(length=64), nullable=False),
        sa.Column("source_id", sa.Integer(), nullable=False),
        sa.Column("lang", sa.String(length=2), nullable=False),
        sa.Column("chunk_text", sa.Text(), nullable=False),
        sa.Column("metadata", sa.dialects.postgresql.JSONB(), nullable=True),
        sa.Column("embedding", Vector(1024), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index(
        "idx_knowledge_chunks_embedding",
        "knowledge_chunks",
        ["embedding"],
        postgresql_using="hnsw",
        postgresql_ops={"embedding": "vector_cosine_ops"},
    )
    op.create_index(
        "idx_knowledge_chunks_source",
        "knowledge_chunks",
        ["source_type", "source_id", "lang"],
    )
    op.create_index(
        "idx_knowledge_chunks_lang",
        "knowledge_chunks",
        ["lang"],
    )

    op.create_table(
        "admin_users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(length=256), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(length=256), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("admin_users")
    op.drop_index("idx_knowledge_chunks_lang", table_name="knowledge_chunks")
    op.drop_index("idx_knowledge_chunks_source", table_name="knowledge_chunks")
    op.drop_index("idx_knowledge_chunks_embedding", table_name="knowledge_chunks")
    op.drop_table("knowledge_chunks")
    op.drop_table("ai_knowledge_translations")
    op.drop_table("ai_knowledge_entries")
    op.drop_table("social_links")
    op.drop_table("project_skills")
    op.drop_table("project_translations")
    op.drop_table("projects")
    op.drop_table("certificate_translations")
    op.drop_table("certificates")
    op.drop_table("course_translations")
    op.drop_table("courses")
    op.drop_table("education_translations")
    op.drop_table("educations")
    op.drop_table("experience_translations")
    op.drop_table("experiences")
    op.drop_table("skill_translations")
    op.drop_table("skills")
    op.drop_table("profile_translations")
    op.drop_table("profiles")
