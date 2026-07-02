"""Unit tests for hybrid retrieval, BM25, and RRF fusion logic.

Scope: pure-logic pieces (RRF formula, similarity gate with RRF scores,
BM25 query construction) that don't require a live Postgres/pgvector
instance. Session-backed retrieval functions are exercised via
integration/manual testing against a running Postgres instance, not here.
"""
import asyncio
from collections.abc import AsyncIterator

from app.services.ai_provider.base import AIProvider, AIProviderError
from app.services.rag import (
    RetrievalSource,
    _rrf_fuse,
    passes_similarity_gate,
    RRF_K,
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


def _make_vector_source(rank: int) -> RetrievalSource:
    """Source found by vector search at the given rank."""
    return RetrievalSource(
        source_type="project",
        source_id=rank,
        score=0.9 - rank * 0.05,
        chunk_text=f"vector chunk {rank}",
        lang="en",
        extra_metadata=None,
        vector_rank=rank,
        bm25_rank=None,
    )


def _make_bm25_source(rank: int) -> RetrievalSource:
    """Source found by BM25 search at the given rank."""
    return RetrievalSource(
        source_type="project",
        source_id=rank + 10,  # different IDs to avoid collision with vector
        score=0.5 + rank * 0.1,
        chunk_text=f"bm25 chunk {rank}",
        lang="en",
        extra_metadata=None,
        vector_rank=None,
        bm25_rank=rank,
    )


def test_rrf_k_is_reasonable():
    assert RRF_K == 60


def test_rrf_fuse_single_method():
    """RRF with only vector results."""
    vector_results = [_make_vector_source(1), _make_vector_source(2)]
    fused = _rrf_fuse(vector_results, [])
    assert len(fused) == 2
    # Both results have vector_rank set and no bm25_rank.
    for src in fused:
        assert src.vector_rank is not None
        assert src.bm25_rank is None
        assert src.rrf_score is not None


def test_rrf_fuse_both_methods_all_ranks():
    """Both methods find the same chunks at different ranks."""
    # Chunk #1: rank 1 in vector, rank 2 in BM25
    v1 = RetrievalSource(
        source_type="project", source_id=1, score=0.9,
        chunk_text="chunk 1", lang="en", extra_metadata=None,
        vector_rank=1, bm25_rank=None,
    )
    b1 = RetrievalSource(
        source_type="project", source_id=1, score=0.6,
        chunk_text="chunk 1", lang="en", extra_metadata=None,
        vector_rank=None, bm25_rank=2,
    )
    # Chunk #2: rank 3 in vector only
    v2 = RetrievalSource(
        source_type="skill", source_id=2, score=0.85,
        chunk_text="chunk 2", lang="en", extra_metadata=None,
        vector_rank=3, bm25_rank=None,
    )

    fused = _rrf_fuse([v1, v2], [b1])
    assert len(fused) == 2

    chunk1 = next(s for s in fused if s.source_id == 1)
    chunk2 = next(s for s in fused if s.source_id == 2)

    # chunk1 has both ranks → higher RRF
    assert chunk1.rrf_score is not None
    assert chunk2.rrf_score is not None
    assert chunk1.rrf_score > chunk2.rrf_score


def test_rrf_fuse_no_duplicates():
    """Same chunk found by both methods is deduplicated."""
    v1 = RetrievalSource(
        source_type="project", source_id=5, score=0.9,
        chunk_text="shared chunk", lang="en", extra_metadata=None,
        vector_rank=1, bm25_rank=None,
    )
    b1 = RetrievalSource(
        source_type="project", source_id=5, score=0.8,
        chunk_text="shared chunk", lang="en", extra_metadata=None,
        vector_rank=None, bm25_rank=1,
    )
    fused = _rrf_fuse([v1], [b1])
    assert len(fused) == 1
    assert fused[0].source_id == 5
    assert fused[0].vector_rank == 1
    assert fused[0].bm25_rank == 1


def test_rrf_fuse_empty_inputs():
    assert _rrf_fuse([], []) == []
    assert _rrf_fuse([_make_vector_source(1)], []) != []


def test_rrf_score_formula():
    """Verify RRF score = 1/(k+rank) + 1/(k+rank) for dual-method at rank 1."""
    v1 = RetrievalSource(
        source_type="x", source_id=1, score=0.9,
        chunk_text="x", lang="en", extra_metadata=None,
        vector_rank=1, bm25_rank=None,
    )
    b1 = RetrievalSource(
        source_type="x", source_id=1, score=0.9,
        chunk_text="x", lang="en", extra_metadata=None,
        vector_rank=None, bm25_rank=1,
    )
    fused = _rrf_fuse([v1], [b1])
    expected = 1 / (RRF_K + 1) + 1 / (RRF_K + 1)
    assert abs(fused[0].rrf_score - expected) < 1e-9


def test_rrf_score_single_method():
    """RRF score for single-method chunk at rank 1."""
    v1 = RetrievalSource(
        source_type="x", source_id=1, score=0.9,
        chunk_text="x", lang="en", extra_metadata=None,
        vector_rank=1, bm25_rank=None,
    )
    fused = _rrf_fuse([v1], [])
    expected = 1 / (RRF_K + 1)
    assert abs(fused[0].rrf_score - expected) < 1e-9


def test_similarity_gate_no_chunks():
    assert passes_similarity_gate([], threshold=0.65) is False


def test_similarity_gate_with_rrf_score_both_methods():
    """RRF score with both methods contributing: lower effective threshold."""
    # rrf_score for rank 1 in both methods
    rrf_val = 2 / (RRF_K + 1)
    sources = [
        RetrievalSource(
            source_type="project", source_id=1, score=0.9,
            chunk_text="x", lang="en", extra_metadata=None,
            vector_rank=1, bm25_rank=1, rrf_score=rrf_val,
        )
    ]
    # With both methods, effective threshold = 0.65/80 ≈ 0.008; rrf ≈ 0.0328 > threshold
    assert passes_similarity_gate(sources, threshold=0.65) is True


def test_similarity_gate_with_rrf_score_single_method():
    """RRF score with only one method: higher effective threshold."""
    rrf_val = 1 / (RRF_K + 1)  # rank 1 in one method only
    sources = [
        RetrievalSource(
            source_type="project", source_id=1, score=0.9,
            chunk_text="x", lang="en", extra_metadata=None,
            vector_rank=1, bm25_rank=None, rrf_score=rrf_val,
        )
    ]
    # With single method, effective threshold = 0.65/50 = 0.013; rrf ≈ 0.0164 > threshold
    assert passes_similarity_gate(sources, threshold=0.65) is True


def test_similarity_gate_with_rrf_score_too_low():
    """Low RRF score fails the gate with both methods."""
    # Rank 118 in both methods: rrf = 2/(60+118) ≈ 0.0112
    # With both methods and threshold=0.9: effective = 0.9/80 ≈ 0.01125
    # 0.0112 < 0.01125 → fails
    rrf_val = 2 / (RRF_K + 118)
    sources = [
        RetrievalSource(
            source_type="project", source_id=1, score=0.9,
            chunk_text="x", lang="en", extra_metadata=None,
            vector_rank=118, bm25_rank=118, rrf_score=rrf_val,
        )
    ]
    assert passes_similarity_gate(sources, threshold=0.9) is False