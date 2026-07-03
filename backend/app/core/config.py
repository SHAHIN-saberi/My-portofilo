"""Application configuration loaded from environment variables.

Uses pydantic-settings so values are validated once at startup and shared via a
cached `get_settings()` dependency.
"""
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # ---- App ----
    app_name: str = "Personal AI Resume/Portfolio API"
    api_v1_prefix: str = "/api/v1"
    debug: bool = False

    # ---- Database ----
    database_url: str = Field(
        default="postgresql+asyncpg://portfolio:portfolio@localhost:5432/portfolio"
    )

    # ---- AI provider ----
    ai_provider: str = "deepseek"
    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com/v1"
    deepseek_chat_model: str = "deepseek-chat"
    deepseek_embed_model: str = "deepseek-embed"
    embedding_dim: int = 1024
    gemini_api_key: str = ""

    # ---- Auth (single admin) ----
    admin_email: str = "owner@example.com"
    admin_password_hash: str = ""
    auth_secret: str = "change-me"
    auth_token_ttl_minutes: int = 720

    # ---- CORS ----
    cors_origins: str = "http://localhost:3000"

    # ---- Chatbot / RAG ----
    rag_top_k: int = 6
    rag_similarity_threshold: float = 0.65
    chat_rate_limit_per_5min: int = 20
    chat_max_turns: int = 10

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
