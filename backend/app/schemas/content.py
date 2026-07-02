from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, HttpUrl

from app.schemas.common import Lang


class TranslationBase(BaseModel):
    lang: Lang

    model_config = {
        "extra": "ignore",
    }


class ProfileTranslationPayload(TranslationBase):
    title: str | None = None
    summary: str | None = None
    bio: str | None = None


class ProfilePayload(BaseModel):
    name: str | None = None
    photo_url: HttpUrl | None = None
    email: str | None = None
    phone: str | None = None
    location: str | None = None
    availability_status: str | None = None
    github_url: HttpUrl | None = None
    linkedin_url: HttpUrl | None = None
    website_url: HttpUrl | None = None
    cv_pdf_url: HttpUrl | None = None
    translations: list[ProfileTranslationPayload] = []

    model_config = {
        "extra": "ignore",
    }


class SkillTranslationPayload(TranslationBase):
    name: str | None = None
    description: str | None = None


class SkillPayload(BaseModel):
    category: str | None = None
    proficiency: str | None = None
    years_experience: float | None = None
    display_order: int | None = None
    translations: list[SkillTranslationPayload] = []

    model_config = {
        "extra": "ignore",
    }


class ExperienceTranslationPayload(TranslationBase):
    role: str | None = None
    description: str | None = None


class ExperiencePayload(BaseModel):
    company: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    is_current: bool | None = None
    location: str | None = None
    display_order: int | None = None
    translations: list[ExperienceTranslationPayload] = []

    model_config = {
        "extra": "ignore",
    }


class EducationTranslationPayload(TranslationBase):
    degree: str | None = None
    field_of_study: str | None = None
    description: str | None = None


class EducationPayload(BaseModel):
    institution: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    location: str | None = None
    display_order: int | None = None
    translations: list[EducationTranslationPayload] = []

    model_config = {
        "extra": "ignore",
    }


class CourseTranslationPayload(TranslationBase):
    title: str | None = None
    description: str | None = None


class CoursePayload(BaseModel):
    provider: str | None = None
    completion_date: str | None = None
    credential_url: HttpUrl | None = None
    display_order: int | None = None
    translations: list[CourseTranslationPayload] = []

    model_config = {
        "extra": "ignore",
    }


class CertificateTranslationPayload(TranslationBase):
    title: str | None = None
    description: str | None = None


class CertificatePayload(BaseModel):
    issuer: str | None = None
    issue_date: str | None = None
    credential_url: HttpUrl | None = None
    display_order: int | None = None
    translations: list[CertificateTranslationPayload] = []

    model_config = {
        "extra": "ignore",
    }


class ProjectTranslationPayload(TranslationBase):
    title: str | None = None
    short_description: str | None = None
    description: str | None = None
    role: str | None = None
    impact: str | None = None


class ProjectPayload(BaseModel):
    start_date: str | None = None
    end_date: str | None = None
    live_url: HttpUrl | None = None
    github_url: HttpUrl | None = None
    tech_stack: list[str] | None = None
    featured: bool | None = None
    display_order: int | None = None
    translations: list[ProjectTranslationPayload] = []
    skill_ids: list[int] = []

    model_config = {
        "extra": "ignore",
    }


class SocialLinkPayload(BaseModel):
    platform: str | None = None
    url: HttpUrl | None = None
    display_order: int | None = None
    is_visible: bool | None = None

    model_config = {
        "extra": "ignore",
    }


class AIKnowledgeTranslationPayload(TranslationBase):
    title: str | None = None
    content: str | None = None


class AIKnowledgeEntryPayload(BaseModel):
    display_order: int | None = None
    translations: list[AIKnowledgeTranslationPayload] = []

    model_config = {
        "extra": "ignore",
    }
