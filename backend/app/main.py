"""FastAPI application entrypoint.

Wires configuration, CORS, routers, health check, and a consistent error
envelope. Product logic lives in the routers/services and is filled in across
later phases.

DB engine initialization is now deferred to lifespan to prevent import-time
connection attempts (critical for TestClient stability).
"""
import logging
import secrets
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.api import admin, chatbot, public
from app.core.config import get_settings
from app.core.limiter import limiter
from app.db.session import init_db
from app.schemas.common import HealthStatus

settings = get_settings()

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.debug else logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: initialize DB engine at startup (not import)."""
    # Security validation: fail-fast if AUTH_SECRET is weak/default
    if not settings.debug and (
        settings.auth_secret == "change-me" 
        or settings.auth_secret == "change-me-to-a-long-random-string-in-production"
        or len(settings.auth_secret) < 32
    ):
        raise ValueError(
            "SECURITY ERROR: AUTH_SECRET must be at least 32 characters and not the default value. "
            "Generate a secure random string for production."
        )
    
    init_db()
    yield
    # (no explicit shutdown required for current scope)


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    debug=settings.debug,
    lifespan=lifespan,
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- Routers ----
prefix = settings.api_v1_prefix
app.include_router(public.router, prefix=prefix)
app.include_router(admin.router, prefix=f"{prefix}/admin")
app.include_router(chatbot.router, prefix=f"{prefix}/chatbot")


@app.get("/health", response_model=HealthStatus, tags=["meta"])
async def health() -> HealthStatus:
    return HealthStatus(service=settings.app_name, version=app.version)


@app.get(f"{prefix}/health", response_model=HealthStatus, tags=["meta"])
async def health_v1() -> HealthStatus:
    return HealthStatus(service=settings.app_name, version=app.version)


@app.exception_handler(Exception)
async def unhandled_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    # Log full error server-side, return only error_id to client
    error_id = secrets.token_urlsafe(16)
    logger.error(
        f"Unhandled exception [{error_id}]: {type(exc).__name__}: {exc}",
        exc_info=True
    )
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "type": "internal_error",
                "error_id": error_id,
                "message": "An unexpected error occurred. Please try again later."
            }
        },
    )
