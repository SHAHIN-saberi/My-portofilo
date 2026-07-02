"""Admin API skeleton (auth required).

Login issues a JWT for the single admin. CRUD endpoints and reindex/status are
stubbed here and implemented in Phase 7 (Admin) / Phase 4 (RAG).
"""
from fastapi import APIRouter, Depends, HTTPException, status

from app.core.config import Settings, get_settings
from app.core.security import create_access_token, require_admin, verify_password
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.common import Envelope, Message

router = APIRouter(tags=["admin"])


@router.post("/login", response_model=TokenResponse)
async def login(
    payload: LoginRequest, settings: Settings = Depends(get_settings)
) -> TokenResponse:
    email_ok = payload.email.lower() == settings.admin_email.lower()
    password_ok = verify_password(payload.password, settings.admin_password_hash)
    if not (email_ok and password_ok):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    token = create_access_token(subject=settings.admin_email, settings=settings)
    return TokenResponse(
        access_token=token,
        expires_in_minutes=settings.auth_token_ttl_minutes,
    )


@router.get("/me", response_model=Envelope)
async def whoami(admin: str = Depends(require_admin)) -> Envelope:
    return Envelope(data={"email": admin, "role": "admin"})


@router.post("/reindex", response_model=Message)
async def reindex(admin: str = Depends(require_admin)) -> Message:
    # Implemented in Phase 4 (RAG pipeline).
    return Message(message="Reindex endpoint stub — implemented in Phase 4.")


@router.get("/knowledge-status", response_model=Envelope)
async def knowledge_status(admin: str = Depends(require_admin)) -> Envelope:
    # Implemented in Phase 4 (RAG pipeline).
    return Envelope(data={"last_indexed_at": None, "chunk_count": 0})
