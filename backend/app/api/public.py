"""Public API skeleton (no auth).

Endpoints return empty/placeholder envelopes in Phase 2. Real data access is
wired up once the Phase 3 schema and Phase 6 content wiring land.
"""
from fastapi import APIRouter, Query

from app.schemas.common import Envelope, Lang

router = APIRouter(tags=["public"])


@router.get("/profile", response_model=Envelope)
async def get_profile(lang: Lang = Query("en")) -> Envelope:
    return Envelope(data=None, meta={"lang": lang, "phase": "skeleton"})


@router.get("/skills", response_model=Envelope)
async def list_skills(
    lang: Lang = Query("en"), category: str | None = Query(None)
) -> Envelope:
    return Envelope(data=[], meta={"lang": lang, "category": category})


@router.get("/experiences", response_model=Envelope)
async def list_experiences(lang: Lang = Query("en")) -> Envelope:
    return Envelope(data=[], meta={"lang": lang})


@router.get("/projects", response_model=Envelope)
async def list_projects(
    lang: Lang = Query("en"), featured: bool | None = Query(None)
) -> Envelope:
    return Envelope(data=[], meta={"lang": lang, "featured": featured})


@router.get("/education", response_model=Envelope)
async def list_education(lang: Lang = Query("en")) -> Envelope:
    return Envelope(data=[], meta={"lang": lang})


@router.get("/courses", response_model=Envelope)
async def list_courses(lang: Lang = Query("en")) -> Envelope:
    return Envelope(data=[], meta={"lang": lang})


@router.get("/certificates", response_model=Envelope)
async def list_certificates(lang: Lang = Query("en")) -> Envelope:
    return Envelope(data=[], meta={"lang": lang})


@router.get("/social-links", response_model=Envelope)
async def list_social_links() -> Envelope:
    return Envelope(data=[])
