"""Focused unit tests for the chatbot RAG wiring added in this package.

Scope: pure-logic pieces that don't require a live Postgres/pgvector
instance (scope classification parsing, similarity gate math, fallback
message formatting). DB-backed retrieval is exercised via integration/manual
testing against a running Postgres instance, not here.
"""
import asyncio
from collections.abc import AsyncIterator

from app.services.ai_provider.base import AIProvider, AIProviderError
from app.services.rag import (
    FALLBACK_NO_ANSWER,
    FALLBACK_UNRELATED,
    RetrievalSource,
    classify_scope,
    passes_similarity_gate,
)


class FakeAIProvider(AIProvider):
    def __init__(self, chat_reply: str | None = None, raise_error: bool = False):
        self._chat_reply = chat_reply
        self._raise_error = raise_error

    async def embed(self, text: str) -> list[float]:
        return [0.1] * 4

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        return [[0.1] * 4 for _ in texts]

    async def chat(self, messages: list[dict], context: str | None = None) -> str:
        if self._raise_error:
            raise AIProviderError("boom")
        return self._chat_reply or ""

    async def chat_stream(
        self, messages: list[dict], context: str | None = None
    ) -> AsyncIterator[str]:
        if False:
            yield ""


def _source(score: float) -> RetrievalSource:
    return RetrievalSource(
        source_type="project",
        source_id=1,
        score=score,
        chunk_text="some chunk",
        lang="en",
        extra_metadata=None,
    )


def test_classify_scope_yes():
    provider = FakeAIProvider(chat_reply="YES")
    result = asyncio.run(classify_scope(provider, "What are your skills?", "Shahin"))
    assert result is True


def test_classify_scope_no():
    provider = FakeAIProvider(chat_reply="NO")
    result = asyncio.run(classify_scope(provider, "What's the weather today?", "Shahin"))
    assert result is False


def test_classify_scope_fails_open_on_provider_error():
    provider = FakeAIProvider(raise_error=True)
    result = asyncio.run(classify_scope(provider, "Anything", "Shahin"))
    assert result is True


def test_similarity_gate_passes_on_close_match():
    # cosine distance 0.1 -> similarity 0.9, above default 0.65 threshold
    assert passes_similarity_gate([_source(0.1)], threshold=0.65) is True


def test_similarity_gate_fails_on_distant_match():
    # cosine distance 0.5 -> similarity 0.5, below threshold
    assert passes_similarity_gate([_source(0.5)], threshold=0.65) is False


def test_similarity_gate_fails_on_no_sources():
    assert passes_similarity_gate([], threshold=0.65) is False


def test_fallback_messages_format_owner_name():
    assert "Shahin" in FALLBACK_UNRELATED.format(name="Shahin")
    assert "Shahin" in FALLBACK_NO_ANSWER.format(name="Shahin")
