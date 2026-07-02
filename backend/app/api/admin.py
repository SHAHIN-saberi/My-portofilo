"""Admin API implementation for content management and RAG maintenance."""
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.core.limiter import limiter
from app.core.security import create_access_token, require_admin, set_auth_cookie, clear_auth_cookie, verify_password
from app.db.session import get_db
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.common import Envelope, Message
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
from app.services.admin_service import (
    create_ai_knowledge_entry,
    create_certificate,
    create_course,
    create_education,
    create_experience,
    create_project,
    create_skill,
    create_social_link,
    delete_ai_knowledge_entry,
    delete_certificate,
    delete_course,
    delete_education,
    delete_experience,
    delete_project,
    delete_skill,
    delete_social_link,
    get_profile,
    knowledge_status,
    list_ai_knowledge_entries,
    list_certificates,
    list_courses,
    list_education,
    list_experiences,
    list_projects,
    list_skills,
    list_social_links,
    update_ai_knowledge_entry,
    update_certificate,
    update_course,
    update_education,
    update_experience,
    update_project,
    update_profile,
    update_skill,
    update_social_link,
)
from app.services.ai_provider.factory import get_ai_provider
from app.services.reindex import reindex_all

router = APIRouter(tags=["admin"])


@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")
async def login(
    request: Request,
    response: Response,
    payload: LoginRequest, 
    settings: Settings = Depends(get_settings)
) -> TokenResponse:
    email_ok = payload.email.lower() == settings.admin_email.lower()
    password_ok = verify_password(payload.password, settings.admin_password_hash)
    if not (email_ok and password_ok):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    token = create_access_token(subject=settings.admin_email, settings=settings)
    
    # Set HttpOnly Secure cookie
    set_auth_cookie(
        response, 
        token, 
        max_age_seconds=settings.auth_token_ttl_minutes * 60
    )
    
    # Also return token in response body for backward compatibility
    return TokenResponse(
        access_token=token,
        expires_in_minutes=settings.auth_token_ttl_minutes,
    )


@router.post("/logout")
async def logout(response: Response) -> Message:
    """Clear the auth cookie to log out the admin user."""
    clear_auth_cookie(response)
    return Message(message="Logged out successfully")


@router.get("/me", response_model=Envelope)
async def whoami(admin: str = Depends(require_admin)) -> Envelope:
    return Envelope(data={"email": admin, "role": "admin"})


@router.get("/profile", response_model=Envelope)
async def get_profile_endpoint(
    admin: str = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
    lang: str = "en",
) -> Envelope:
    return Envelope(data=await get_profile(session, lang))


@router.put("/profile", response_model=Envelope)
async def update_profile_endpoint(
    payload: ProfilePayload,
    admin: str = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> Envelope:
    return Envelope(data=await update_profile(session, payload))


@router.get("/skills", response_model=Envelope)
async def list_skills_endpoint(
    admin: str = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
    limit: int = 100,
    offset: int = 0,
) -> Envelope:
    return Envelope(data=await list_skills(session, limit=limit, offset=offset))


@router.post("/skills", response_model=Envelope)
async def create_skill_endpoint(
    payload: SkillPayload,
    admin: str = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> Envelope:
    return Envelope(data=await create_skill(session, payload))


@router.put("/skills/{skill_id}", response_model=Envelope)
async def update_skill_endpoint(
    skill_id: int,
    payload: SkillPayload,
    admin: str = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> Envelope:
    try:
        return Envelope(data=await update_skill(session, skill_id, payload))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.delete("/skills/{skill_id}", response_model=Message)
async def delete_skill_endpoint(
    skill_id: int,
    admin: str = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> Message:
    await delete_skill(session, skill_id)
    return Message(message="Skill deleted")


@router.get("/experiences", response_model=Envelope)
async def list_experiences_endpoint(
    admin: str = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
    limit: int = 100,
    offset: int = 0,
) -> Envelope:
    return Envelope(data=await list_experiences(session, limit=limit, offset=offset))


@router.post("/experiences", response_model=Envelope)
async def create_experience_endpoint(
    payload: ExperiencePayload,
    admin: str = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> Envelope:
    return Envelope(data=await create_experience(session, payload))


@router.put("/experiences/{experience_id}", response_model=Envelope)
async def update_experience_endpoint(
    experience_id: int,
    payload: ExperiencePayload,
    admin: str = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> Envelope:
    try:
        return Envelope(data=await update_experience(session, experience_id, payload))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.delete("/experiences/{experience_id}", response_model=Message)
async def delete_experience_endpoint(
    experience_id: int,
    admin: str = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> Message:
    await delete_experience(session, experience_id)
    return Message(message="Experience deleted")


@router.get("/education", response_model=Envelope)
async def list_education_endpoint(
    admin: str = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
    limit: int = 100,
    offset: int = 0,
) -> Envelope:
    return Envelope(data=await list_education(session, limit=limit, offset=offset))


@router.post("/education", response_model=Envelope)
async def create_education_endpoint(
    payload: EducationPayload,
    admin: str = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> Envelope:
    return Envelope(data=await create_education(session, payload))


@router.put("/education/{education_id}", response_model=Envelope)
async def update_education_endpoint(
    education_id: int,
    payload: EducationPayload,
    admin: str = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> Envelope:
    try:
        return Envelope(data=await update_education(session, education_id, payload))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.delete("/education/{education_id}", response_model=Message)
async def delete_education_endpoint(
    education_id: int,
    admin: str = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> Message:
    await delete_education(session, education_id)
    return Message(message="Education deleted")


@router.get("/courses", response_model=Envelope)
async def list_courses_endpoint(
    admin: str = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
    limit: int = 100,
    offset: int = 0,
) -> Envelope:
    return Envelope(data=await list_courses(session, limit=limit, offset=offset))


@router.post("/courses", response_model=Envelope)
async def create_course_endpoint(
    payload: CoursePayload,
    admin: str = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> Envelope:
    return Envelope(data=await create_course(session, payload))


@router.put("/courses/{course_id}", response_model=Envelope)
async def update_course_endpoint(
    course_id: int,
    payload: CoursePayload,
    admin: str = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> Envelope:
    try:
        return Envelope(data=await update_course(session, course_id, payload))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.delete("/courses/{course_id}", response_model=Message)
async def delete_course_endpoint(
    course_id: int,
    admin: str = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> Message:
    await delete_course(session, course_id)
    return Message(message="Course deleted")


@router.get("/certificates", response_model=Envelope)
async def list_certificates_endpoint(
    admin: str = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
    limit: int = 100,
    offset: int = 0,
) -> Envelope:
    return Envelope(data=await list_certificates(session, limit=limit, offset=offset))


@router.post("/certificates", response_model=Envelope)
async def create_certificate_endpoint(
    payload: CertificatePayload,
    admin: str = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> Envelope:
    return Envelope(data=await create_certificate(session, payload))


@router.put("/certificates/{certificate_id}", response_model=Envelope)
async def update_certificate_endpoint(
    certificate_id: int,
    payload: CertificatePayload,
    admin: str = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> Envelope:
    try:
        return Envelope(data=await update_certificate(session, certificate_id, payload))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.delete("/certificates/{certificate_id}", response_model=Message)
async def delete_certificate_endpoint(
    certificate_id: int,
    admin: str = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> Message:
    await delete_certificate(session, certificate_id)
    return Message(message="Certificate deleted")


@router.get("/projects", response_model=Envelope)
async def list_projects_endpoint(
    admin: str = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
    limit: int = 100,
    offset: int = 0,
) -> Envelope:
    return Envelope(data=await list_projects(session, limit=limit, offset=offset))


@router.post("/projects", response_model=Envelope)
async def create_project_endpoint(
    payload: ProjectPayload,
    admin: str = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> Envelope:
    return Envelope(data=await create_project(session, payload))


@router.put("/projects/{project_id}", response_model=Envelope)
async def update_project_endpoint(
    project_id: int,
    payload: ProjectPayload,
    admin: str = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> Envelope:
    try:
        return Envelope(data=await update_project(session, project_id, payload))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.delete("/projects/{project_id}", response_model=Message)
async def delete_project_endpoint(
    project_id: int,
    admin: str = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> Message:
    await delete_project(session, project_id)
    return Message(message="Project deleted")


@router.get("/social-links", response_model=Envelope)
async def list_social_links_endpoint(
    admin: str = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
    limit: int = 100,
    offset: int = 0,
) -> Envelope:
    return Envelope(data=await list_social_links(session, limit=limit, offset=offset))


@router.post("/social-links", response_model=Envelope)
async def create_social_link_endpoint(
    payload: SocialLinkPayload,
    admin: str = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> Envelope:
    return Envelope(data=await create_social_link(session, payload))


@router.put("/social-links/{social_link_id}", response_model=Envelope)
async def update_social_link_endpoint(
    social_link_id: int,
    payload: SocialLinkPayload,
    admin: str = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> Envelope:
    try:
        return Envelope(data=await update_social_link(session, social_link_id, payload))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.delete("/social-links/{social_link_id}", response_model=Message)
async def delete_social_link_endpoint(
    social_link_id: int,
    admin: str = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> Message:
    await delete_social_link(session, social_link_id)
    return Message(message="Social link deleted")


@router.get("/ai-knowledge", response_model=Envelope)
async def list_ai_knowledge_entries_endpoint(
    admin: str = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
    limit: int = 100,
    offset: int = 0,
) -> Envelope:
    return Envelope(data=await list_ai_knowledge_entries(session, limit=limit, offset=offset))


@router.post("/ai-knowledge", response_model=Envelope)
async def create_ai_knowledge_entry_endpoint(
    payload: AIKnowledgeEntryPayload,
    admin: str = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> Envelope:
    return Envelope(data=await create_ai_knowledge_entry(session, payload))


@router.put("/ai-knowledge/{entry_id}", response_model=Envelope)
async def update_ai_knowledge_entry_endpoint(
    entry_id: int,
    payload: AIKnowledgeEntryPayload,
    admin: str = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> Envelope:
    try:
        return Envelope(data=await update_ai_knowledge_entry(session, entry_id, payload))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.delete("/ai-knowledge/{entry_id}", response_model=Message)
async def delete_ai_knowledge_entry_endpoint(
    entry_id: int,
    admin: str = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> Message:
    await delete_ai_knowledge_entry(session, entry_id)
    return Message(message="AI knowledge entry deleted")


@router.post("/reindex", response_model=Message)
async def reindex_endpoint(
    admin: str = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
    ai_provider=Depends(get_ai_provider),
    settings: Settings = Depends(get_settings),
) -> Message:
    total = 0
    for lang in ("en", "fa"):
        total += await reindex_all(session, ai_provider, settings, lang)
    return Message(message=f"Reindex completed with {total} chunks")


@router.get("/knowledge-status", response_model=Envelope)
async def knowledge_status_endpoint(
    admin: str = Depends(require_admin), session: AsyncSession = Depends(get_db)
) -> Envelope:
    return Envelope(data=await knowledge_status(session))
