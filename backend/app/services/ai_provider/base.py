"""AI provider abstraction.

Any provider (DeepSeek now, others later) implements this interface. RAG and
chatbot logic depend only on this contract, never on a concrete provider — see
spec section 12 (AI Provider Abstraction).
"""
from abc import ABC, abstractmethod
from collections.abc import AsyncIterator


class AIProvider(ABC):
    @abstractmethod
    async def embed(self, text: str) -> list[float]:
        """Return the embedding vector for a single text."""

    @abstractmethod
    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Return embedding vectors for a batch of texts."""

    @abstractmethod
    async def chat(
        self, messages: list[dict], context: str | None = None
    ) -> str:
        """Return a full chat completion.

        `messages` is an OpenAI-style list of {"role", "content"}.
        `context` is optional retrieved RAG context injected by the caller.
        """

    @abstractmethod
    async def chat_stream(
        self, messages: list[dict], context: str | None = None
    ) -> AsyncIterator[str]:
        """Yield chat completion tokens/chunks as they arrive."""


class AIProviderError(RuntimeError):
    """Raised when the underlying provider call fails."""
