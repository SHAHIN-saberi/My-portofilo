"""DeepSeek implementation of the AIProvider interface.

Uses the OpenAI-compatible REST endpoints via httpx. API key and model names
come from settings. Network/error handling raises AIProviderError so callers can
apply the spec's safe fallback behavior.

NOTE (open question tracked in agent_state.json): DeepSeek's public API may not
currently expose an embeddings endpoint / `deepseek-embed` model. This provider
implements `embed`/`embed_batch` against the documented /embeddings path; if that
proves unavailable at implementation time (Phase 4), a fallback embedding
provider will be introduced behind the same interface without touching RAG code.
"""
import json
from collections.abc import AsyncIterator

import httpx

from app.core.config import Settings
from app.services.ai_provider.base import AIProvider, AIProviderError


class DeepSeekProvider(AIProvider):
    def __init__(self, settings: Settings):
        self._api_key = settings.deepseek_api_key
        self._base_url = settings.deepseek_base_url.rstrip("/")
        self._chat_model = settings.deepseek_chat_model
        self._embed_model = settings.deepseek_embed_model
        self._embedding_dim = settings.embedding_dim
        self._timeout = httpx.Timeout(60.0, connect=10.0)

    @property
    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

    # ---- Embeddings ----
    async def embed(self, text: str) -> list[float]:
        vectors = await self.embed_batch([text])
        return vectors[0]

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        payload = {"model": self._embed_model, "input": texts}
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                resp = await client.post(
                    f"{self._base_url}/embeddings",
                    headers=self._headers,
                    json=payload,
                )
                resp.raise_for_status()
                data = resp.json()
            # OpenAI-compatible shape: {"data": [{"embedding": [...]}, ...]}
            items = sorted(data["data"], key=lambda d: d.get("index", 0))
            return [item["embedding"] for item in items]
        except httpx.HTTPStatusError as exc:
            # Fail closed: never generate fake embeddings, always raise error
            # This prevents silent corruption of the knowledge_chunks index
            raise AIProviderError(
                f"DeepSeek embeddings failed with HTTP {exc.response.status_code}: {exc}"
            ) from exc
        except (httpx.HTTPError, KeyError, json.JSONDecodeError) as exc:
            raise AIProviderError(f"DeepSeek embeddings failed: {exc}") from exc

    # ---- Chat ----
    async def chat(
        self, messages: list[dict], context: str | None = None
    ) -> str:
        payload = {
            "model": self._chat_model,
            "messages": self._with_context(messages, context),
            "stream": False,
        }
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                resp = await client.post(
                    f"{self._base_url}/chat/completions",
                    headers=self._headers,
                    json=payload,
                )
                resp.raise_for_status()
                data = resp.json()
            return data["choices"][0]["message"]["content"]
        except (httpx.HTTPError, KeyError, json.JSONDecodeError) as exc:
            raise AIProviderError(f"DeepSeek chat failed: {exc}") from exc

    async def chat_stream(
        self, messages: list[dict], context: str | None = None
    ) -> AsyncIterator[str]:
        payload = {
            "model": self._chat_model,
            "messages": self._with_context(messages, context),
            "stream": True,
        }
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                async with client.stream(
                    "POST",
                    f"{self._base_url}/chat/completions",
                    headers=self._headers,
                    json=payload,
                ) as resp:
                    resp.raise_for_status()
                    async for line in resp.aiter_lines():
                        if not line or not line.startswith("data: "):
                            continue
                        chunk = line.removeprefix("data: ").strip()
                        if chunk == "[DONE]":
                            break
                        try:
                            delta = json.loads(chunk)["choices"][0]["delta"]
                        except (KeyError, json.JSONDecodeError):
                            continue
                        if content := delta.get("content"):
                            yield content
        except httpx.HTTPError as exc:
            raise AIProviderError(f"DeepSeek chat stream failed: {exc}") from exc

    @staticmethod
    def _with_context(
        messages: list[dict], context: str | None
    ) -> list[dict]:
        """Prepend retrieved context as a system message if provided."""
        if not context:
            return messages
        return [{"role": "system", "content": context}, *messages]
