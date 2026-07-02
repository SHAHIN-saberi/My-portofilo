"""Focused unit tests for the chatbot RAG wiring added in this package.

Scope: pure-logic pieces that don't require a live Postgres/pgvector
instance (scope classification parsing, similarity gate math, fallback
message formatting, plan complexity, citation validation). DB-backed
retrieval is exercised via integration/manual testing against a running
Postgres instance, not here.
"""
import asyncio
from collections.abc import AsyncIterator

from app.services.ai_provider.base import AIProvider, AIProviderError
from app.services.rag import (
    BUDGET_MULTIPLIER,
    HIGH_CONFIDENCE_RRF,
    FALLBACK_NO_ANSWER,
    FALLBACK_UNRELATED,
    RetrievalSource,
    classify_scope,
    passes_similarity_gate,
    plan_query,
    validate_answer_citations,
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


def test_plan_query_returns_rewritten_query():
    provider = FakeAIProvider(chat_reply="Shahin's Python and FastAPI experience")
    result = asyncio.run(plan_query(provider, "what about his python skills?", "Shahin"))
    assert result["original_query"] == "what about his python skills?"
    assert result["rewritten_query"] == "Shahin's Python and FastAPI experience"


def test_plan_query_uses_only_first_line_of_reply():
    provider = FakeAIProvider(chat_reply="Shahin's Python experience\nextra commentary line")
    result = asyncio.run(plan_query(provider, "python skills?", "Shahin"))
    assert result["rewritten_query"] == "Shahin's Python experience"


def test_plan_query_falls_back_to_original_on_empty_reply():
    provider = FakeAIProvider(chat_reply="")
    result = asyncio.run(plan_query(provider, "python skills?", "Shahin"))
    assert result["rewritten_query"] == "python skills?"


def test_plan_query_fails_open_on_provider_error():
    provider = FakeAIProvider(raise_error=True)
    result = asyncio.run(plan_query(provider, "python skills?", "Shahin"))
    assert result["rewritten_query"] == "python skills?"
    assert result["original_query"] == "python skills?"


def test_plan_query_returns_complexity_field():
    """plan_query should return a complexity field (low/medium/high)."""
    provider = FakeAIProvider(chat_reply="Shahin's Python skills\nMEDIUM\nNO")
    result = asyncio.run(plan_query(provider, "what python skills?", "Shahin"))
    assert result["complexity"] == "medium"
    assert result["needs_clarification"] is False


def test_plan_query_complexity_high():
    provider = FakeAIProvider(chat_reply="Shahin's experience at Acme Corp in 2023\nHIGH\nNO")
    result = asyncio.run(plan_query(provider, "what did Shahin do at Acme?", "Shahin"))
    assert result["complexity"] == "high"


def test_plan_query_complexity_low():
    provider = FakeAIProvider(chat_reply="FastAPI web framework expertise\nLOW\nNO")
    result = asyncio.run(plan_query(provider, "Does Shahin know FastAPI?", "Shahin"))
    assert result["complexity"] == "low"


def test_plan_query_needs_clarification_yes():
    provider = FakeAIProvider(chat_reply="Shahin's work experience\nMEDIUM\nYES")
    result = asyncio.run(plan_query(provider, "tell me about your work", "Shahin"))
    assert result["needs_clarification"] is True


def test_plan_query_needs_clarification_no():
    provider = FakeAIProvider(chat_reply="Shahin's Python skills\nMEDIUM\nNO")
    result = asyncio.run(plan_query(provider, "What Python frameworks does Shahin use?", "Shahin"))
    assert result["needs_clarification"] is False


def test_plan_query_fails_open_complexity_medium():
    provider = FakeAIProvider(raise_error=True)
    result = asyncio.run(plan_query(provider, "any question", "Shahin"))
    assert result["complexity"] == "medium"
    assert result["needs_clarification"] is False


def test_budget_multiplier_present():
    assert BUDGET_MULTIPLIER["low"] < 1.0
    assert BUDGET_MULTIPLIER["medium"] == 1.0
    assert BUDGET_MULTIPLIER["high"] > 1.0


def test_high_confidence_rrf_threshold():
    assert HIGH_CONFIDENCE_RRF > 0


def test_validate_answer_citations_valid():
    provider = FakeAIProvider(chat_reply="VALID")
    sources = [
        RetrievalSource(
            source_type="skill", source_id=1, score=0.9,
            chunk_text="Python expert with 5 years of experience", lang="en",
            extra_metadata=None,
        )
    ]
    result = asyncio.run(validate_answer_citations(provider, "Shahin is a Python expert", sources))
    assert result is True


def test_validate_answer_citations_invalid():
    provider = FakeAIProvider(chat_reply="INVALID")
    sources = [
        RetrievalSource(
            source_type="skill", source_id=1, score=0.9,
            chunk_text="Python expert", lang="en", extra_metadata=None,
        )
    ]
    result = asyncio.run(validate_answer_citations(provider, "Shahin won a Nobel prize in physics", sources))
    assert result is False


def test_validate_answer_citations_fails_open():
    provider = FakeAIProvider(raise_error=True)
    sources = [
        RetrievalSource(
            source_type="skill", source_id=1, score=0.9,
            chunk_text="Python expert", lang="en", extra_metadata=None,
        )
    ]
    result = asyncio.run(validate_answer_citations(provider, "Any answer", sources))
    assert result is True  # Fails open


def test_validate_answer_citations_empty_sources():
    provider = FakeAIProvider(chat_reply="VALID")
    result = asyncio.run(validate_answer_citations(provider, "Any answer", []))
    assert result is True  # Nothing to validate against → pass
