"""Provider factory + FastAPI dependency.

Selects the concrete AIProvider based on settings (`AI_PROVIDER`). Swapping
providers requires only a new class here — no changes to RAG/chatbot logic.
"""
from functools import lru_cache

from fastapi import Depends

from app.core.config import Settings, get_settings
from app.services.ai_provider.base import AIProvider
from app.services.ai_provider.deepseek import DeepSeekProvider
from app.services.ai_provider.gemini import GeminiProvider
_PROVIDERS = {
    "deepseek": DeepSeekProvider,
    "gemini": GeminiProvider,
}


@lru_cache
def _build_provider(provider_name: str) -> AIProvider:
    settings = get_settings()
    try:
        provider_cls = _PROVIDERS[provider_name]
    except KeyError as exc:
        raise ValueError(f"Unknown AI provider: {provider_name}") from exc
    return provider_cls(settings)


def get_ai_provider(
    settings: Settings = Depends(get_settings),
) -> AIProvider:
    return _build_provider(settings.ai_provider)
