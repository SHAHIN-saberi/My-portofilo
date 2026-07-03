import json
from collections.abc import AsyncIterator

from google import genai

from app.core.config import Settings
from app.services.ai_provider.base import AIProvider, AIProviderError


class GeminiProvider(AIProvider):
    def __init__(self, settings: Settings):
        self._api_key = settings.gemini_api_key
        self._chat_model = "gemini-2.5-flash"
        self._embed_model = "text-embedding-004"

        self._client = genai.Client(api_key=self._api_key)

    # ---------- EMBEDDING ----------
    async def embed(self, text: str) -> list[float]:
        return (await self.embed_batch([text]))[0]

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        try:
            result = self._client.models.embed_content(
                model=self._embed_model,
                contents=texts
            )
            return [e.values for e in result.embeddings]
        except Exception as e:
            raise AIProviderError(f"Gemini embed failed: {e}")

    # ---------- CHAT ----------
    async def chat(self, messages: list[dict], context: str | None = None) -> str:
        try:
            full_prompt = self._build_prompt(messages, context)

            response = self._client.models.generate_content(
                model=self._chat_model,
                contents=full_prompt
            )

            return response.text
        except Exception as e:
            raise AIProviderError(f"Gemini chat failed: {e}")

    async def chat_stream(
        self, messages: list[dict], context: str | None = None
    ) -> AsyncIterator[str]:

        full_prompt = self._build_prompt(messages, context)

        try:
            stream = self._client.models.generate_content_stream(
                model=self._chat_model,
                contents=full_prompt
            )

            for chunk in stream:
                if chunk.text:
                    yield chunk.text

        except Exception as e:
            raise AIProviderError(f"Gemini stream failed: {e}")

    def _build_prompt(self, messages: list[dict], context: str | None) -> str:
        parts = []

        if context:
            parts.append(f"Context:\n{context}\n")

        for m in messages:
            parts.append(f"{m['role']}: {m['content']}")

        return "\n".join(parts)