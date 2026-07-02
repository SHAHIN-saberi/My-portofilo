# SYSTEM_CONTRACTS.md
**Strict Behavior Freeze — Generated from actual repository code only**
**Date:** 2026-07-01
**Source:** backend/app/api/*, backend/app/services/rag.py, backend/app/services/admin_service.py, backend/app/services/content.py, models, schemas

---

## 1. Contract Summary Table

| System Part              | Status    |
|--------------------------|-----------|
| API Contracts            | Defined   |
| RAG Core Pipeline        | Defined   |
| RAG Helper Functions     | Partial   |
| DB Behavior Contracts    | Defined   |
| Failure Mode Contracts   | Defined   |
| Admin CRUD Contracts     | Defined   |
| Public Read Contracts    | Defined   |
| Undefined Behaviors      | Listed    |

---

## 2. Fully Defined Contracts

### 2.1 API Contracts (Exact from code)

**Chatbot**
- `POST /api/v1/chatbot/query`
  - Request: `ChatQueryRequest` { question: str, lang: "en"|"fa" }
  - Response: `ChatQueryResponse` { answer: str, status: "answered"|"no_answer"|"error", sources: list[ChatSource] | null }
  - Service chain: `query()` → `build_question_answer()` (with rate limit 20/min)
  - DB: required (AsyncSession)
  - On any exception: returns `{answer: FALLBACK_ERROR, status: "error", sources: null}`

**Public API** (all endpoints)
- `GET /api/v1/profile?lang=en|fa`
- `GET /api/v1/skills?lang=en|fa&category=...`
- `GET /api/v1/experiences?lang=en|fa`
- `GET /api/v1/education?lang=en|fa`
- `GET /api/v1/projects?lang=en|fa&featured=...`
- `GET /api/v1/courses?lang=en|fa`
- `GET /api/v1/certificates?lang=en|fa`
- `GET /api/v1/social-links`
- All return `Envelope` { data: [...], meta?: {...} }
- Service chain: direct calls to `app.services.content.*`

**Admin API** (all under `/api/v1/admin/*`)
- Full CRUD for: profiles, skills, experiences, education, courses, certificates, projects, social-links, ai-knowledge
- Special: `POST /reindex` → calls `reindex_all()` for both languages
- `GET /knowledge-status`
- All protected by `require_admin`
- Response wrapper: `Envelope` or `Message`

**Health**
- `GET /health` and `GET /api/v1/health` → `HealthStatus`

### 2.2 RAG Contracts (Exact observed behavior)

**classify_scope**
- Signature: `async def classify_scope(ai_provider, question, owner_name) -> bool`
- Input: question + owner_name
- Output: `True` (in-scope) or `False`
- Control flow: LLM binary YES/NO prompt. On `AIProviderError` → returns `True` (fail-open)

**plan_query**
- Signature: `async def plan_query(ai_provider, question, owner_name) -> dict`
- Output keys (always present):
  - `rewritten_query`: str
  - `original_query`: str (original question)
  - `complexity`: "low" | "medium" | "high"
  - `needs_clarification`: bool
- On `AIProviderError`: falls back to `{rewritten_query: question, original_query: question, complexity: "medium", needs_clarification: False}`

**embed_query**
- Signature: `async def embed_query(question, ai_provider) -> list[float]`
- Output: embedding vector (1024-dim expected)

**hybrid_retrieve**
- Signature: `async def hybrid_retrieve(session, query_text, query_embedding, lang, top_k=6) -> list[RetrievalSource]`
- Behavior: runs `_vector_search_with_fallback` + `_bm25_search_with_fallback` in parallel → `_rrf_fuse` → returns top-k sorted by `rrf_score` descending
- Fallback: English results appended when lang != "en" and insufficient results

**_rrf_fuse**
- Uses constant `RRF_K = 60`
- Score formula: `1/(RRF_K + rank)` summed across methods that found the chunk

**build_question_answer** (main orchestration)
- Full observed flow:
  1. `get_owner_name()`
  2. `classify_scope()` — if False → `FALLBACK_UNRELATED`
  3. `plan_query()`
  4. Dynamic `effective_top_k` using `BUDGET_MULTIPLIER`
  5. `embed_query()` → `hybrid_retrieve()`
  6. `passes_similarity_gate()` — if fails → `FALLBACK_NO_ANSWER`
  7. High-confidence early exit check (RRF + ranks)
  8. `rerank_sources()` (or direct top_k)
  9. `assemble_context()`
  10. `generate_chat_response()`
  11. `validate_answer_citations()` — on failure triggers strict regeneration prompt
- On embedding failure: returns error fallback
- On generation failure: returns error fallback

**passes_similarity_gate**
- Uses dynamic threshold based on whether both retrieval methods contributed

---

## 3. Partial / Weak Contracts

- `rerank_sources`, `assemble_context`, `generate_chat_response`, `validate_answer_citations`, `validate_citations` — called in `build_question_answer` but implementation details not visible in primary source file (behavior assumed present but not frozen here).
- `reindex_all` and `knowledge_status` — referenced in admin router but implementation in `reindex.py` not audited in this freeze.

---

## 4. Undefined Behaviors (CRITICAL)

The following are **NOT explicitly implemented** in the scanned code:

- `needs_clarification=True` path (plan_query can return it, but no caller logic handles returning a clarification question to the user)
- Exact prompt templates for `generate_chat_response` and `rerank_sources`
- Exact behavior of `validate_citations` helper
- Handling when `top_k` after multiplier exceeds any hard limit
- Behavior when `KnowledgeChunk` table is empty
- Exact error messages returned by AI provider on rate limits / quota
- Frontend-visible behavior when `status="no_answer"` vs `"error"`

---

## 5. Failure Mode Contracts (Explicitly coded)

| Failure Scenario       | Observed Behavior in Code |
|------------------------|---------------------------|
| Empty / unrelated query | `classify_scope` returns False → `FALLBACK_UNRELATED` |
| No relevant retrieval   | `passes_similarity_gate` fails → `FALLBACK_NO_ANSWER` |
| Embedding failure       | `AIProviderError` in `embed_query` → `FALLBACK_ERROR` |
| LLM generation failure  | `result is None` or `AIProviderError` → `FALLBACK_ERROR` |
| Citation validation fail| Strict re-prompt attempt; still fails → `FALLBACK_NO_ANSWER` |
| Any unexpected error    | Chatbot endpoint catches → `FALLBACK_ERROR` (never 500) |
| DB connection issues    | Not explicitly handled in RAG path (will propagate) |

---

## 6. Explicit System Guarantees

- Every `/chatbot/query` call is rate-limited to 20/minute.
- All chatbot failures degrade gracefully to one of three polite fallback strings.
- Hybrid retrieval always attempts both vector + BM25 with English fallback.
- RRF fusion always uses `RRF_K=60`.
- Scope filter fails open (`True`) on provider errors.
- Query planner fails open to safe defaults on provider errors.
- Citation validation has a second-chance strict prompt path.
- Admin endpoints are protected; public endpoints are read-only.
- All public and admin responses are wrapped in `Envelope` or `Message`.

---

**END OF CONTRACT FREEZE**  
This document reflects **only** behavior that exists in the current codebase. No assumptions were made.