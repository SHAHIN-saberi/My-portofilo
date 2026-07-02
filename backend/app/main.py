"""FastAPI application entrypoint.

Wires configuration, CORS, routers, health check, and a consistent error
envelope. Product logic lives in the routers/services and is filled in across
later phases.
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.api import admin, chatbot, public
from app.core.config import get_settings
from app.core.limiter import limiter
from app.schemas.common import HealthStatus

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    debug=settings.debug,
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
    # Consistent structured error envelope.
    return JSONResponse(
        status_code=500,
        content={"error": {"type": "internal_error", "message": str(exc)}},
    )
