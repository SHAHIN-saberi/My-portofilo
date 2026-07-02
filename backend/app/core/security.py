"""Authentication helpers for the single-admin panel.

- Password verification against a bcrypt hash (stored in env / DB).
- Short-lived JWT bearer tokens signed with AUTH_SECRET.
- FastAPI dependency `require_admin` to protect admin routes.
- HttpOnly Secure cookies for token storage (XSS protection).
"""
from datetime import datetime, timedelta, timezone
import uuid

import bcrypt
import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import Settings, get_settings

_bearer = HTTPBearer(auto_error=False)
_ALGORITHM = "HS256"
_COOKIE_NAME = "admin_token"


def verify_password(plain_password: str, password_hash: str) -> bool:
    if not password_hash:
        return False
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"), password_hash.encode("utf-8")
        )
    except ValueError:
        return False


def hash_password(plain_password: str) -> str:
    return bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt()).decode(
        "utf-8"
    )


def create_access_token(subject: str, settings: Settings) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "iat": now,
        "exp": now + timedelta(minutes=settings.auth_token_ttl_minutes),
        "role": "admin",
        "jti": str(uuid.uuid4()),  # Unique JWT ID for potential revocation
    }
    return jwt.encode(payload, settings.auth_secret, algorithm=_ALGORITHM)


def decode_access_token(token: str, settings: Settings) -> dict:
    return jwt.decode(token, settings.auth_secret, algorithms=[_ALGORITHM])


def set_auth_cookie(response, token: str, max_age_seconds: int) -> None:
    """Set HttpOnly Secure SameSite=Strict cookie with the JWT token."""
    response.set_cookie(
        key=_COOKIE_NAME,
        value=token,
        max_age=max_age_seconds,
        httponly=True,      # Not accessible via JavaScript (XSS protection)
        secure=True,        # Only sent over HTTPS
        samesite="strict",  # Not sent on cross-site requests (CSRF protection)
        path="/",           # Available on all paths
    )


def clear_auth_cookie(response) -> None:
    """Delete the auth cookie."""
    response.delete_cookie(
        key=_COOKIE_NAME,
        httponly=True,
        secure=True,
        samesite="strict",
        path="/",
    )


async def require_admin(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    settings: Settings = Depends(get_settings),
) -> str:
    """Validate the admin token from cookie (preferred) or Authorization header.
    
    Returns the admin subject (email) or raises 401.
    """
    token = None
    
    # Try cookie first (preferred, more secure)
    token = request.cookies.get(_COOKIE_NAME)
    
    # Fallback to Authorization header for backward compatibility
    if not token and credentials and credentials.credentials:
        token = credentials.credentials
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        payload = decode_access_token(token, settings)
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if payload.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required"
        )
    
    sub = payload.get("sub", "")
    if not sub:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: missing subject",
        )
    return sub
