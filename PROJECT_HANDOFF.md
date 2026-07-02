# PROJECT_HANDOFF

## 1. Project Overview

- Purpose: Personal AI resume / portfolio platform with a backend-managed content catalog, a single-admin panel, and an AI-driven chatbot for owner-specific questions.
- Architecture: FastAPI backend, PostgreSQL database with pgvector, DeepSeek AI provider abstraction, Next.js frontend placeholder, nginx reverse proxy, Docker Compose orchestration.
- Technologies: Python, FastAPI, SQLAlchemy async, Alembic, PostgreSQL, pgvector, DeepSeek, httpx, JWT, bcrypt, Next.js, Docker, nginx.
- Design decisions: fixed stack with Next.js frontend, FastAPI backend, PostgreSQL + pgvector, DeepSeek provider, translation tables for bilingual content, single admin authentication, lightweight agentic RAG, hybrid retrieval architecture.
- Current implementation philosophy: implement minimum required backend functionality first, keep provider and retrieval abstractions separate, use environment-configured admin auth, keep frontend scope minimal until backend is stable.

## 2. Current Repository Status

- Completion percentage: ~20% (per `agent_state.json`).
- Completed packages: Phase 0/1/2/3 scaffolding and backend schema + basic service wiring.
- Current package: Package 1 - Backend Implementation.
- Completed backend modules:
  - `backend/app/main.py`
  - `backend/app/api/public.py`
  - `backend/app/api/admin.py`
  - `backend/app/api/chatbot.py` (endpoint stub)
  - `backend/app/core/config.py`
  - `backend/app/core/security.py`
  - `backend/app/db/session.py`
  - `backend/app/db/models.py`
  - `backend/app/schemas/common.py`
  - `backend/app/schemas/content.py`
  - `backend/app/schemas/chatbot.py`
  - `backend/app/services/content.py`
  - `backend/app/services/admin_service.py`
  - `backend/app/services/ai_provider/base.py`
  - `backend/app/services/ai_provider/deepseek.py`
  - `backend/app/services/ai_provider/factory.py`
  - `backend/app/services/rag.py`
  - `backend/app/services/reindex.py`
- Completed frontend modules: none beyond `frontend/Dockerfile`.
- Completed RAG modules: partial retrieval, reranking, context assembly, citation stub, reindex pipeline, embedding pipeline.
- Completed infrastructure: `docker-compose.yml`, `nginx/nginx.conf`, `.env.example`, backend Dockerfile, PostgreSQL + pgvector compose setup.

## 3. Current Architecture

- Frontend: placeholder container build only. No functional Next.js app source is present in the repository.
- Backend: FastAPI app with API routers for public content, admin CRUD, and chatbot; configuration via Pydantic settings; async SQLAlchemy session management; JWT admin auth; content and admin service layers; AI provider abstraction; RAG and reindex services.
- Database: PostgreSQL with pgvector extension. Declarative SQLAlchemy models and Alembic migration define translation tables, content tables, knowledge chunks, and admin user table.
- AI Provider: provider abstraction via `AIProvider` base class, DeepSeek implementation, provider factory selecting by `AI_PROVIDER` config.
- Agentic RAG: retrieval service in `backend/app/services/rag.py` can embed queries, search `knowledge_chunks`, rerank retrieved sources, build context, and generate answers. Chat endpoint is currently only a stub.
- Retrieval pipeline: uses `retrieve_chunks` with pgvector cosine similarity search, language fallback to English if needed, `embed_batch` via DeepSeek, and chunk assembly.
- Translation system: per-domain translation tables (`*_translations`) with language preference and fallback logic in content services.
- Admin system: single admin authentication through JWT and env-configured credentials; admin router exposes login/me, profile update, content CRUD, reindex trigger, and knowledge status.

## 4. Repository Structure

- `agent_state.json`: implementation progress tracker and current package state.
- `README.md`: project summary and quick start information.
- `spec.md`: source-of-truth specification.
- `.env.example`: environment variables template for database, AI provider, admin, CORS, and RAG tuning.
- `docker-compose.yml`: orchestrates `postgres`, `backend`, `frontend`, and `nginx` services.
- `nginx/nginx.conf`: reverse proxy configuration routing `/api`, docs, and frontend.
- `scripts/`: helper scripts for dev, teardown, and password hash generation.
- `backend/`: backend FastAPI application and database migrations.
  - `backend/app/main.py`: FastAPI app entrypoint.
  - `backend/app/api/`: API routers for public, admin, and chatbot.
  - `backend/app/core/`: config and security utilities.
  - `backend/app/db/`: SQLAlchemy base, async session, and ORM models.
  - `backend/app/schemas/`: Pydantic request/response payloads and response envelope.
  - `backend/app/services/`: business logic for content, admin CRUD, AI provider, RAG, and reindexing.
  - `backend/alembic/`: Alembic migration configuration and initial schema migration.
- `frontend/`: only contains `Dockerfile`; actual frontend source is absent.

## 5. Database

- Tables:
  - `profiles`
  - `profile_translations`
  - `skills`
  - `skill_translations`
  - `experiences`
  - `experience_translations`
  - `educations`
  - `education_translations`
  - `courses`
  - `course_translations`
  - `certificates`
  - `certificate_translations`
  - `projects`
  - `project_translations`
  - `project_skills`
  - `social_links`
  - `ai_knowledge_entries`
  - `ai_knowledge_translations`
  - `knowledge_chunks`
  - `admin_users`
- Relationships:
  - One-to-many: each content entity has translations in a corresponding `*_translations` table.
  - Many-to-many: `project_skills` links `projects` to `skills`.
  - AI knowledge entries link to `ai_knowledge_translations`.
  - `knowledge_chunks` stores embedding-based retrieval data with no enforced foreign key to source tables.
- Translation tables:
  - Each domain uses a dedicated translation table keyed by source ID and `lang`.
  - Unique constraints enforce one translation row per source-language pair.
  - Language fallback logic prefers requested language then English.
- Knowledge tables:
  - `ai_knowledge_entries` and `ai_knowledge_translations` store additional owner-specific AI content.
  - `knowledge_chunks` stores chunked source text, metadata, language, and pgvector embeddings.
- Vector storage:
  - `knowledge_chunks.embedding` is `Vector(1024)`.
  - Indexes: `idx_knowledge_chunks_embedding` (hnsw + vector_cosine_ops), `idx_knowledge_chunks_source`, `idx_knowledge_chunks_lang`.

## 6. API Status

- Public API (`backend/app/api/public.py`): implemented.
  - `/api/v1/profile`: implemented.
  - `/api/v1/skills`: implemented.
  - `/api/v1/experiences`: implemented.
  - `/api/v1/projects`: implemented.
  - `/api/v1/education`: implemented.
  - `/api/v1/courses`: implemented.
  - `/api/v1/certificates`: implemented.
  - `/api/v1/social-links`: implemented.
- Admin API (`backend/app/api/admin.py`): fully implemented.
  - `/api/v1/admin/login`: implemented.
  - `/api/v1/admin/me`: implemented.
  - `/api/v1/admin/profile` GET and PUT: implemented.
  - `/api/v1/admin/skills` GET/POST/PUT/DELETE: implemented.
  - `/api/v1/admin/experiences` GET/POST/PUT/DELETE: implemented.
  - `/api/v1/admin/education` GET/POST/PUT/DELETE: implemented.
  - `/api/v1/admin/courses` GET/POST/PUT/DELETE: implemented.
  - `/api/v1/admin/certificates` GET/POST/PUT/DELETE: implemented.
  - `/api/v1/admin/projects` GET/POST/PUT/DELETE: implemented.
  - `/api/v1/admin/social-links` GET/POST/PUT/DELETE: implemented.
  - `/api/v1/admin/ai-knowledge` GET/POST/PUT/DELETE: implemented.
  - `/api/v1/admin/reindex`: implemented.
  - `/api/v1/admin/knowledge-status`: implemented.
- Chatbot API (`backend/app/api/chatbot.py`): implemented. `/api/v1/chatbot/query` is wired to `services/rag.build_question_answer`, returning `answered` / `unrelated` / `no_answer` / `error` status with the spec-locked fallback copy for each non-answered case.

## 7. Backend Status

Completed:
- Core FastAPI app setup and error handling.
- Config and async DB session management.
- Database schema models and initial Alembic migration.
- Content retrieval services with translation selection.
- Admin CRUD service implementations for create/update/delete.
- Provider abstraction and DeepSeek integration.
- RAG helper methods: embedding query, retrieval, reranking, context assembly, answer generation, citation formatting.
- Chatbot endpoint fully wired to the RAG decision flow: LLM-based professional scope filter (`classify_scope`), cosine-similarity relevance gate (`passes_similarity_gate`, using `rag_similarity_threshold`), retrieval, rerank, context assembly, generation with an owner-name-aware system prompt, and citation formatting. Spec-locked fallback copy is returned for `unrelated` and `no_answer` statuses; unexpected failures return an `error` status instead of a 500.
- Reindex pipeline with source gathering and chunk creation.
- Basic backend tests for model metadata and schema presence, plus unit tests for scope classification, the similarity gate, and admin list-endpoint route wiring/auth enforcement.
- Full admin CRUD coverage: list endpoints added for experiences, education, courses, certificates, projects, social-links, and ai-knowledge (all return every stored translation per item, matching the existing `list_skills` convention, unlike public endpoints which resolve a single language).

Partially completed:
- RAG is only partially implemented; BM25, RRF, and a Query Planner stage are absent (pgvector-only retrieval).
- Database model vs migration inconsistency exists for `courses`.
- Admin auth model/table exists but is unused by current auth flow.
- Chatbot flow and the new admin list endpoints are validated by provider-independent/route-wiring unit tests and an app-boot smoke test only; no live Postgres+pgvector/DeepSeek integration test has been run yet.

Missing:
- Backend tests for admin auth and create/update/delete service logic (only list endpoints and route wiring are tested so far).
- Frontend application implementation.
- Complete hybrid retrieval pipeline features (BM25, RRF fusion, Query Planner/Rewrite stage, explicit stop conditions).
- Live integration test of chatbot + admin CRUD against a running Postgres+pgvector instance and real/mocked DeepSeek responses.

## 8. Frontend Status

Completed:
- `frontend/Dockerfile` exists for container build.

Missing:
- No Next.js application source code or React pages/components.
- No frontend implementation for public pages or admin panel.

## 9. RAG Status

- Planner: missing as a separate planner component; retrieval helper exists.
- Scope Filter: implemented via `classify_scope()` — an LLM YES/NO classification gate on whether the question concerns the owner's professional profile. Fails open (treated as in-scope) on provider error, since the similarity gate and generation prompt still guard against hallucination.
- Relevance Gate: implemented via `passes_similarity_gate()` — converts pgvector cosine *distance* to similarity and compares against `settings.rag_similarity_threshold` (default 0.65, per spec).
- Hybrid Retrieval: partial. pgvector-based retrieval exists, but no BM25 or actual multimodal fusion.
- pgvector: implemented and indexed.
- BM25: missing.
- RRF: missing.
- Reranker: partial. `rerank_sources` uses AIProvider chat ranking but is not yet validated with a real endpoint.
- Context Builder: implemented via `assemble_context`.
- Citation Validation: partial. citations are formatted per retrieved source, but real answer-source validation (checking the generated answer actually cites/matches the sources) is not enforced.
- Chatbot wiring: `build_question_answer()` now implements the full locked decision flow (scope filter -> embed -> retrieve -> similarity gate -> rerank -> context -> generate -> citations) and is called directly from `POST /api/v1/chatbot/query`.
- Reindex Pipeline: implemented in `backend/app/services/reindex.py` and exposed via admin route.
- Embedding Pipeline: implemented through DeepSeek provider `embed_batch` and chunk creation.

## 10. AI Provider

- Abstraction: `backend/app/services/ai_provider/base.py` defines `AIProvider` and `AIProviderError`.
- DeepSeek integration: `backend/app/services/ai_provider/deepseek.py` implements embeddings, chat, and streaming chat calls using OpenAI-compatible REST semantics.
- Provider factory: `backend/app/services/ai_provider/factory.py` selects the provider based on `settings.ai_provider`.
- Provider switching: configuration-based. Only `deepseek` is registered, but the factory supports adding new provider classes.

## 11. Remaining Work

1. Fix database schema mismatch for `Course` model vs Alembic migration.
   - files: `backend/app/db/models.py`, `backend/alembic/versions/0001_initial.py`.
2. Resolve admin auth implementation vs `AdminUser` table inconsistency.
   - files: `backend/app/db/models.py`, `backend/app/core/security.py`, `backend/app/api/admin.py`.
3. Implement the remaining locked RAG pipeline stages: Query Planner/Query Rewrite, BM25 lexical retrieval, RRF fusion of pgvector + BM25 results, and explicit stop conditions.
   - files: `backend/app/services/rag.py`, `backend/app/services/reindex.py`.
4. Expand RAG reliability: real answer-source citation validation (current `validate_citations` just formats source refs, it doesn't check the answer actually used them).
   - files: `backend/app/services/rag.py`.
5. Add backend tests for admin auth and create/update/delete service logic, plus a live-DB integration test for chatbot and admin CRUD (current tests cover scope/similarity logic, admin list route wiring/auth, and metadata only — not real database reads/writes).
   - files: `backend/tests/*.py`.
6. Implement frontend application source and connect to backend.
   - files: `frontend/`.

## 12. Known Issues

- Chatbot flow has not been exercised against a live Postgres+pgvector instance or the real DeepSeek API in this environment (no credentials/DB available here); validated via unit tests + app-boot smoke test only.
- `ChatSource`/citations are only meaningful for `status: answered`; the endpoint always omits `sources` for `unrelated`/`no_answer`/`error`, but there is no separate admin-only debug flag yet to distinguish visitor vs. admin views per spec section 10.
- `AdminUser` table exists but current admin auth is environment-based and does not use the DB table.
- `Course` model fields differ from the Alembic migration schema.
- New admin list endpoints (experiences, education, courses, certificates, projects, social-links, ai-knowledge) are validated by route-wiring/auth tests only, not against a live database — their query/serialization logic (mirrors the existing, working `list_skills`) has not been run against real rows.
- The frontend directory contains only a `Dockerfile`; no functional frontend code is available.
- RAG features like BM25, RRF, and professional scope fusion are not implemented.

## 13. Suggested Continuation Order

1. ~~Complete backend chatbot wiring first, because backend functionality is the core package goal.~~ Done.
2. ~~Close admin CRUD coverage and add missing list endpoints, then verify admin API consistency.~~ Done.
3. Fix DB migration/model mismatches and confirm schema integrity.
4. Implement missing RAG retrieval features (Query Planner, BM25, RRF fusion, stop conditions) per the locked pipeline in `NEXT_AGENT.md`.
5. Add backend tests for auth, admin CRUD service logic, reindex, and a live-DB chatbot integration test.
6. Implement frontend application and connect it to the existing backend API.

## 14. Files Modified During This Project

- `PROJECT_HANDOFF.md`
- `agent_state.json`
- `backend/app/api/public.py`
- `backend/app/api/admin.py`
- `backend/app/api/chatbot.py`
- `backend/app/core/config.py`
- `backend/app/core/security.py`
- `backend/app/db/models.py`
- `backend/app/db/session.py`
- `backend/app/schemas/common.py`
- `backend/app/schemas/content.py`
- `backend/app/schemas/chatbot.py`
- `backend/app/services/content.py`
- `backend/app/services/admin_service.py`
- `backend/app/services/ai_provider/base.py`
- `backend/app/services/ai_provider/deepseek.py`
- `backend/app/services/ai_provider/factory.py`
- `backend/app/services/rag.py`
- `backend/app/services/reindex.py`
- `backend/alembic/versions/0001_initial.py`
- `backend/tests/test_chatbot_rag.py`
- `backend/tests/test_admin_list_endpoints.py`
- `docker-compose.yml`
- `nginx/nginx.conf`
- `.env.example`

## 15. Final Repository Health

- Backend: 55%
- Frontend: 5%
- Database: 70%
- RAG: 40%
- Infrastructure: 70%
- Overall Completion: 41%
