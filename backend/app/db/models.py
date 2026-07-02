"""ORM models.

Phase 3 implements the full relational schema required by the spec.
This module is the single import point for Alembic and the application.
"""
from datetime import datetime
from decimal import Decimal

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    BOOLEAN,
    CheckConstraint,
    ForeignKey,
    Integer,
    BigInteger,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    Index,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Profile(Base):
    __tablename__ = "profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    photo_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    email: Mapped[str | None] = mapped_column(String(256), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(64), nullable=True)
    location: Mapped[str | None] = mapped_column(String(128), nullable=True)
    availability_status: Mapped[str | None] = mapped_column(String(128), nullable=True)
    github_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    linkedin_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    website_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    cv_pdf_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow
    )

    translations: Mapped[list["ProfileTranslation"]] = relationship(
        "ProfileTranslation",
        back_populates="profile",
        cascade="all, delete-orphan",
    )


class ProfileTranslation(Base):
    __tablename__ = "profile_translations"
    __table_args__ = (
        CheckConstraint("lang IN ('en', 'fa')", name="ck_profile_translations_lang"),
        UniqueConstraint("profile_id", "lang", name="uq_profile_lang"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    profile_id: Mapped[int] = mapped_column(ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False)
    lang: Mapped[str] = mapped_column(String(2), nullable=False)
    title: Mapped[str | None] = mapped_column(Text, nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)

    profile: Mapped[Profile] = relationship("Profile", back_populates="translations")


class Skill(Base):
    __tablename__ = "skills"

    id: Mapped[int] = mapped_column(primary_key=True)
    category: Mapped[str | None] = mapped_column(String(64), nullable=True)
    proficiency: Mapped[str | None] = mapped_column(String(32), nullable=True)
    years_experience: Mapped[Decimal | None] = mapped_column(Numeric(4, 1), nullable=True)
    display_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow
    )

    __table_args__ = (
        CheckConstraint(
            "proficiency IN ('beginner','intermediate','advanced','expert')",
            name="ck_skills_proficiency",
        ),
    )

    translations: Mapped[list["SkillTranslation"]] = relationship(
        "SkillTranslation",
        back_populates="skill",
        cascade="all, delete-orphan",
    )
    project_links: Mapped[list["ProjectSkill"]] = relationship(
        "ProjectSkill",
        back_populates="skill",
        cascade="all, delete-orphan",
    )


class SkillTranslation(Base):
    __tablename__ = "skill_translations"
    __table_args__ = (UniqueConstraint("skill_id", "lang", name="uq_skill_lang"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id", ondelete="CASCADE"), nullable=False)
    lang: Mapped[str] = mapped_column(String(2), nullable=False)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    skill: Mapped[Skill] = relationship("Skill", back_populates="translations")


class Experience(Base):
    __tablename__ = "experiences"

    id: Mapped[int] = mapped_column(primary_key=True)
    company: Mapped[str] = mapped_column(String(256), nullable=False)
    start_date: Mapped[str | None] = mapped_column(String(32), nullable=True)
    end_date: Mapped[str | None] = mapped_column(String(32), nullable=True)
    is_current: Mapped[bool] = mapped_column(BOOLEAN, nullable=False, default=False)
    location: Mapped[str | None] = mapped_column(String(128), nullable=True)
    display_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow
    )

    translations: Mapped[list["ExperienceTranslation"]] = relationship(
        "ExperienceTranslation",
        back_populates="experience",
        cascade="all, delete-orphan",
    )


class ExperienceTranslation(Base):
    __tablename__ = "experience_translations"
    __table_args__ = (UniqueConstraint("experience_id", "lang", name="uq_experience_lang"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    experience_id: Mapped[int] = mapped_column(ForeignKey("experiences.id", ondelete="CASCADE"), nullable=False)
    lang: Mapped[str] = mapped_column(String(2), nullable=False)
    role: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    experience: Mapped[Experience] = relationship("Experience", back_populates="translations")


class Education(Base):
    __tablename__ = "educations"

    id: Mapped[int] = mapped_column(primary_key=True)
    institution: Mapped[str] = mapped_column(String(256), nullable=False)
    start_date: Mapped[str | None] = mapped_column(String(32), nullable=True)
    end_date: Mapped[str | None] = mapped_column(String(32), nullable=True)
    location: Mapped[str | None] = mapped_column(String(128), nullable=True)
    display_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    translations: Mapped[list["EducationTranslation"]] = relationship(
        "EducationTranslation",
        back_populates="education",
        cascade="all, delete-orphan",
    )


class EducationTranslation(Base):
    __tablename__ = "education_translations"
    __table_args__ = (UniqueConstraint("education_id", "lang", name="uq_education_lang"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    education_id: Mapped[int] = mapped_column(ForeignKey("educations.id", ondelete="CASCADE"), nullable=False)
    lang: Mapped[str] = mapped_column(String(2), nullable=False)
    degree: Mapped[str] = mapped_column(Text, nullable=False)
    field_of_study: Mapped[str | None] = mapped_column(String(128), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    education: Mapped[Education] = relationship("Education", back_populates="translations")


class Course(Base):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(primary_key=True)
    provider: Mapped[str | None] = mapped_column(String(256), nullable=True)
    completion_date: Mapped[str | None] = mapped_column(String(32), nullable=True)
    credential_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    display_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    translations: Mapped[list["CourseTranslation"]] = relationship(
        "CourseTranslation",
        back_populates="course",
        cascade="all, delete-orphan",
    )


class CourseTranslation(Base):
    __tablename__ = "course_translations"
    __table_args__ = (UniqueConstraint("course_id", "lang", name="uq_course_lang"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    lang: Mapped[str] = mapped_column(String(2), nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    course: Mapped[Course] = relationship("Course", back_populates="translations")


class Certificate(Base):
    __tablename__ = "certificates"

    id: Mapped[int] = mapped_column(primary_key=True)
    issuer: Mapped[str | None] = mapped_column(String(256), nullable=True)
    issue_date: Mapped[str | None] = mapped_column(String(32), nullable=True)
    credential_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    display_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    translations: Mapped[list["CertificateTranslation"]] = relationship(
        "CertificateTranslation",
        back_populates="certificate",
        cascade="all, delete-orphan",
    )


class CertificateTranslation(Base):
    __tablename__ = "certificate_translations"
    __table_args__ = (UniqueConstraint("certificate_id", "lang", name="uq_certificate_lang"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    certificate_id: Mapped[int] = mapped_column(ForeignKey("certificates.id", ondelete="CASCADE"), nullable=False)
    lang: Mapped[str] = mapped_column(String(2), nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    certificate: Mapped[Certificate] = relationship("Certificate", back_populates="translations")


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True)
    start_date: Mapped[str | None] = mapped_column(String(32), nullable=True)
    end_date: Mapped[str | None] = mapped_column(String(32), nullable=True)
    live_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    github_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    tech_stack: Mapped[list[str] | None] = mapped_column(ARRAY(String(64)), nullable=True)
    featured: Mapped[bool] = mapped_column(BOOLEAN, nullable=False, default=False)
    display_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow
    )

    translations: Mapped[list["ProjectTranslation"]] = relationship(
        "ProjectTranslation",
        back_populates="project",
        cascade="all, delete-orphan",
    )
    skills: Mapped[list["ProjectSkill"]] = relationship(
        "ProjectSkill",
        back_populates="project",
        cascade="all, delete-orphan",
    )


class ProjectTranslation(Base):
    __tablename__ = "project_translations"
    __table_args__ = (UniqueConstraint("project_id", "lang", name="uq_project_lang"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    lang: Mapped[str] = mapped_column(String(2), nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    short_description: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    role: Mapped[str | None] = mapped_column(Text, nullable=True)
    impact: Mapped[str | None] = mapped_column(Text, nullable=True)

    project: Mapped[Project] = relationship("Project", back_populates="translations")


class ProjectSkill(Base):
    __tablename__ = "project_skills"

    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), primary_key=True)
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id", ondelete="CASCADE"), primary_key=True)

    project: Mapped[Project] = relationship("Project", back_populates="skills")
    skill: Mapped[Skill] = relationship("Skill", back_populates="project_links")


class SocialLink(Base):
    __tablename__ = "social_links"

    id: Mapped[int] = mapped_column(primary_key=True)
    platform: Mapped[str] = mapped_column(String(128), nullable=False)
    url: Mapped[str] = mapped_column(String(512), nullable=False)
    display_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_visible: Mapped[bool] = mapped_column(BOOLEAN, nullable=False, default=True)


class AIKnowledgeEntry(Base):
    __tablename__ = "ai_knowledge_entries"

    id: Mapped[int] = mapped_column(primary_key=True)
    display_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow
    )

    translations: Mapped[list["AIKnowledgeTranslation"]] = relationship(
        "AIKnowledgeTranslation",
        back_populates="entry",
        cascade="all, delete-orphan",
    )


class AIKnowledgeTranslation(Base):
    __tablename__ = "ai_knowledge_translations"
    __table_args__ = (UniqueConstraint("entry_id", "lang", name="uq_ai_knowledge_lang"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    entry_id: Mapped[int] = mapped_column(ForeignKey("ai_knowledge_entries.id", ondelete="CASCADE"), nullable=False)
    lang: Mapped[str] = mapped_column(String(2), nullable=False)
    title: Mapped[str | None] = mapped_column(Text, nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    entry: Mapped[AIKnowledgeEntry] = relationship("AIKnowledgeEntry", back_populates="translations")


class KnowledgeChunk(Base):
    __tablename__ = "knowledge_chunks"
    __table_args__ = (
        Index(
            "idx_knowledge_chunks_embedding",
            "embedding",
            postgresql_using="hnsw",
            postgresql_ops={"embedding": "vector_cosine_ops"},
        ),
        Index("idx_knowledge_chunks_source", "source_type", "source_id", "lang"),
        Index("idx_knowledge_chunks_lang", "lang"),
        Index(
            "idx_knowledge_chunks_search_en",
            "search_vector_en",
            postgresql_using="gin",
        ),
        Index(
            "idx_knowledge_chunks_search_fa",
            "search_vector_fa",
            postgresql_using="gin",
        ),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    source_type: Mapped[str] = mapped_column(String(64), nullable=False)
    source_id: Mapped[int] = mapped_column(Integer, nullable=False)
    lang: Mapped[str] = mapped_column(String(2), nullable=False)
    chunk_text: Mapped[str] = mapped_column(Text, nullable=False)
    extra_metadata: Mapped[dict[str, str] | None] = mapped_column("metadata", JSONB, nullable=True)
    embedding: Mapped[list[float]] = mapped_column(Vector(1024), nullable=False)
    # BM25 full-text search: populated automatically by a DB trigger on insert.
    # Python side never touches these; the trigger computes to_tsvector() from chunk_text.
    search_vector_en: Mapped[str | None] = mapped_column(Text, nullable=True)
    search_vector_fa: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow
    )


class AdminUser(Base):
    __tablename__ = "admin_users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(256), nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(String(256), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow
    )


__all__ = [
    "Base",
    "Profile",
    "ProfileTranslation",
    "Skill",
    "SkillTranslation",
    "Experience",
    "ExperienceTranslation",
    "Education",
    "EducationTranslation",
    "Course",
    "CourseTranslation",
    "Certificate",
    "CertificateTranslation",
    "Project",
    "ProjectTranslation",
    "ProjectSkill",
    "SocialLink",
    "AIKnowledgeEntry",
    "AIKnowledgeTranslation",
    "KnowledgeChunk",
    "AdminUser",
]
