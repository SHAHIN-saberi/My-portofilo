"""Public API implementation backed by database content services."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.common import Envelope, Lang
from app.services.content import (
    get_profile,
    list_certificates,
    list_courses,
    list_education,
    list_experiences,
    list_projects,
    list_skills,
    list_social_links,
)

router = APIRouter(tags=["public"])


@router.get("/profile", response_model=Envelope)
async def get_profile_endpoint(
    lang: Lang = Query("en"), session: AsyncSession = Depends(get_db)
) -> Envelope:
    return Envelope(data=await get_profile(session, lang), meta={"lang": lang})


@router.get("/skills", response_model=Envelope)
async def list_skills_endpoint(
    lang: Lang = Query("en"),
    category: str | None = Query(None),
    session: AsyncSession = Depends(get_db),
) -> Envelope:
    return Envelope(
        data=await list_skills(session, lang, category),
        meta={"lang": lang, "category": category},
    )


@router.get("/experiences", response_model=Envelope)
async def list_experiences_endpoint(
    lang: Lang = Query("en"), session: AsyncSession = Depends(get_db)
) -> Envelope:
    return Envelope(data=await list_experiences(session, lang), meta={"lang": lang})


@router.get("/projects", response_model=Envelope)
async def list_projects_endpoint(
    lang: Lang = Query("en"),
    featured: bool | None = Query(None),
    session: AsyncSession = Depends(get_db),
) -> Envelope:
    return Envelope(
        data=await list_projects(session, lang, featured),
        meta={"lang": lang, "featured": featured},
    )


@router.get("/education", response_model=Envelope)
async def list_education_endpoint(
    lang: Lang = Query("en"), session: AsyncSession = Depends(get_db)
) -> Envelope:
    return Envelope(data=await list_education(session, lang), meta={"lang": lang})


@router.get("/courses", response_model=Envelope)
async def list_courses_endpoint(
    lang: Lang = Query("en"), session: AsyncSession = Depends(get_db)
) -> Envelope:
    return Envelope(data=await list_courses(session, lang), meta={"lang": lang})


@router.get("/certificates", response_model=Envelope)
async def list_certificates_endpoint(
    lang: Lang = Query("en"), session: AsyncSession = Depends(get_db)
) -> Envelope:
    return Envelope(data=await list_certificates(session, lang), meta={"lang": lang})


@router.get("/social-links", response_model=Envelope)
async def list_social_links(session: AsyncSession = Depends(get_db)) -> Envelope:
    return Envelope(data=await list_social_links(session))
