# Fix Tracking - Production Readiness Checklist

**Created:** 2026-07-02  
**Baseline Tests:** Backend: 1 failed, 68 passed | Frontend: build SUCCESS (21 pages CSR)  
**Source:** Derived from AGENT_MASTER_PROMPT.md section 7 + AUDIT_REPORT.md

---

## 🔴 P0 — Critical (Must Fix All)

- [x] **P0-1**: Remove fake SHA-256 embedding fallback in `deepseek.py:58-66` — fail closed
  - **Status:** FIXED ✅
  - **Changes:**
    - Removed entire `if exc.response.status_code == 404` block that generated fake SHA-256 vectors
    - Now always raises `AIProviderError` on any HTTP error (fail-closed)
    - Removed unused `import hashlib`
  - **Files:** `backend/app/services/ai_provider/deepseek.py`
  - **Note:** If the knowledge_chunks index was previously built with fake embeddings, it MUST be reindexed after deployment (manual action for human)

- [x] **P0-4**: Fix `ChatQueryResponse.status` enum + frontend adapter handling
  - **Status:** FIXED ✅
  - **Changes:**
    - Backend: Changed `status: str` to `status: Literal["answered","unrelated","no_answer","error","needs_clarification"]` in Pydantic schema
    - Frontend types: Added `unrelated` and `needs_clarification` to `ChatStatusType` and `UIState`
    - Frontend adapter: Explicitly handles all 5 statuses (no longer coerces unknown to "answered")
    - Chat UI: Added distinct colors for `unrelated` (purple) and `needs_clarification` (sky blue)
    - Chat UI: Added "Rephrase & Retry" button for `needs_clarification` status
  - **Files:** `backend/app/schemas/chatbot.py`, `frontend/types/safe.ts`, `frontend/types/state.ts`, `frontend/types/index.ts`, `frontend/lib/adapters/chat.adapter.ts`, `frontend/app/chat/page.tsx`

- [ ] **P0-2**: Complete 5 missing admin pages (courses, certificates, social-links, ai-knowledge, profile)
  - **Status:** NOT FIXED
  - **Verification:** Only 4 admin domains implemented (skills, projects, experience, education)
  - **Files:** `frontend/app/(admin)/adshs/` — missing 5 page directories

- [x] **P0-3**: Delete duplicate `/admin` route tree, keep `/adshs`, fix auth guard
  - **Status:** FIXED ✅
  - **Changes:**
    - Deleted entire `frontend/app/(admin)/admin/` directory (6 files: dashboard, education, experience, login, projects, skills)
    - Created `frontend/middleware.ts` for server-side auth redirect (checks `admin_token` cookie on `/adshs/*` except `/adshs/login`)
    - Verified no remaining references to `/admin/*` routes in codebase
  - **Files deleted:** `frontend/app/(admin)/admin/*` (6 files, ~1,360 LOC)
  - **Files created:** `frontend/middleware.ts`
  - **Build verification:** 15 pages (down from 21), middleware active (26.5 kB)

- [ ] **P0-4**: Fix `ChatQueryResponse.status` enum + frontend adapter handling
  - **Status:** PARTIALLY FIXED (backend schema is `str`, not Literal)
  - **Verification:** Backend allows all 5 statuses via `str` type, but frontend adapter maps "unrelated"/"needs_clarification" to "answered"
  - **Files:** `backend/app/schemas/chatbot.py:25`, `frontend/lib/adapters/chat.adapter.ts:28-36`

- [x] **P0-5**: Security lockdown (JWT secret enforcement, login rate-limit, httpOnly cookie, error leakage, nginx headers)
  - **Status:** FIXED ✅
  - **Changes:**
    - AUTH_SECRET enforcement: Added validation in lifespan() to fail-fast if secret is default/short (<32 chars) in production mode (`backend/app/main.py:25-33`)
    - Rate-limit admin login: Added `@limiter.limit("5/minute")` to `/api/v1/admin/login` endpoint (`backend/app/api/admin.py:65`)
    - httpOnly cookie: JWT now set as HttpOnly Secure SameSite=Strict cookie via `set_auth_cookie()` helper (`backend/app/core/security.py:47-58`)
    - Cookie-based auth: `require_admin()` now reads from cookie first, falls back to Authorization header (`backend/app/core/security.py:73-106`)
    - Logout endpoint: Added `POST /api/v1/admin/logout` to clear cookie (`backend/app/api/admin.py:96-100`)
    - JWT jti: Added unique JWT ID (`jti`) claim for potential revocation (`backend/app/core/security.py:36-44`)
    - JWT sub validation: `require_admin()` now rejects empty `sub` claim (`backend/app/core/security.py:99-103`)
    - Error handler: Now logs full error server-side with `error_id`, returns only generic message + error_id to client (`backend/app/main.py:73-86`)
    - Nginx security headers: Added X-Frame-Options, X-Content-Type-Options, Referrer-Policy, X-XSS-Protection, Permissions-Policy, Content-Security-Policy (`nginx/nginx.conf:15-27`)
    - Frontend migration: Replaced localStorage token storage with `admin_logged_in` flag (UI state only), `credentials: "include"` for cookie-based auth (`frontend/lib/api.ts:34-47`, `frontend/app/(admin)/layout.tsx`, `frontend/components/AdminNavbar.tsx`, all `/adshs/*` pages)
  - **Files:** `backend/app/main.py`, `backend/app/api/admin.py`, `backend/app/core/security.py`, `nginx/nginx.conf`, `frontend/lib/api.ts`, `frontend/app/(admin)/layout.tsx`, `frontend/components/AdminNavbar.tsx`, `frontend/app/(admin)/adshs/*`

- [ ] **P0-6**: Convert public pages to Server Components + metadata + sitemap/robots
  - **Status:** NOT FIXED
  - **Verification:** All 5 public pages have `"use client"` on line 1 (page.tsx, projects, skills, experience, education)
  - **Files:** `frontend/app/(public)/*/page.tsx`

---

## 🟠 P1 — High (Backend Cluster)

- [ ] **P1-1**: Fix N+1 queries with `selectinload` on all list endpoints
  - **Status:** NOT FIXED
  - **Files:** `backend/app/services/content.py`, `backend/app/services/admin_service.py`

- [ ] **P1-2**: Add pagination (limit/offset) to all list endpoints
  - **Status:** NOT FIXED
  - **Files:** `backend/app/api/public.py`, `backend/app/api/admin.py`

- [ ] **P1-5**: Add `max_length` to chat input
  - **Status:** FIXED ✅
  - **Verification:** `ChatQueryRequest.question` has `max_length=2000` in Field definition
  - **Files:** `backend/app/schemas/chatbot.py:11`

- [ ] **P1-6**: Fix rate-limit config mismatch (20/min vs 20/5min)
  - **Status:** NOT FIXED
  - **Files:** `backend/app/core/limiter.py`, `backend/app/api/chatbot.py`

- [ ] **P1-7**: Fix JWT `sub` empty string issue, add `jti`
  - **Status:** NOT FIXED
  - **Files:** `backend/app/core/security.py`

- [ ] **P1-8**: Fix translation destructive replace bug (data loss on partial update)
  - **Status:** NOT FIXED
  - **Verification:** `admin_service._populate_translations()` does `parent.translations = translations` which cascades delete
  - **Files:** `backend/app/services/admin_service.py:12-18`

- [ ] **P1-14**: Replace `datetime.utcnow()` with `server_default=func.now()`
  - **Status:** NOT FIXED
  - **Files:** `backend/app/db/models.py` (15+ models)

---

## 🟠 P1 — High (RAG/Frontend/Security Cluster)

- [ ] **P1-4**: Document/tune similarity gate thresholds + add logging
  - **Status:** NOT FIXED
  - **Files:** `backend/app/services/rag.py`

- [ ] **P1-9**: Add `error.tsx`, `not-found.tsx`, `global-error.tsx`
  - **Status:** NOT FIXED
  - **Files:** `frontend/app/`

- [ ] **P1-10**: Prevent admin token on public API requests
  - **Status:** NOT FIXED
  - **Verification:** `api.ts:33` unconditionally adds Bearer token if localStorage has it
  - **Files:** `frontend/lib/api.ts`

- [ ] **P1-11**: Add prompt-injection delimiters around retrieved content
  - **Status:** NOT FIXED
  - **Files:** `backend/app/services/rag.py`

- [ ] **P1-12**: Add nginx security headers (if not completed in P0-5)
  - **Status:** NOT FIXED
  - **Files:** `nginx/nginx.conf`

- [ ] **P1-13**: Set up CI/CD (Phase 10)
  - **Status:** NOT FIXED

- [ ] **P1-3**: Docker hardening (Phase 8)
  - **Status:** NOT FIXED
  - **Files:** `backend/Dockerfile`, `frontend/Dockerfile`, `docker-compose.yml`

---

## 🟡 P2 Selected (Must Fix Before Launch)

- [ ] Remove hardcoded PII from `frontend/lib/identity.ts`
  - **Status:** NOT FIXED
  - **Verification:** Contains "SHAHIN Saberi", phone, Telegram links
  - **Files:** `frontend/lib/identity.ts`

- [ ] Add `.dockerignore` for backend and frontend
  - **Status:** NOT FIXED

- [ ] Fix `NEXT_PUBLIC_API_URL` build-arg in Docker
  - **Status:** NOT FIXED

- [ ] Decide on unused `AdminUser` table (delete or use)
  - **Status:** NOT FIXED

- [ ] Add minimal Privacy Notice (GDPR – NL hosting)
  - **Status:** NOT FIXED

---

## Essential Features (From AUDIT_REPORT.md "Missing Features")

- [ ] Error pages (404/500)
- [ ] Security headers + HTTPS
- [ ] Rate-limit on login
- [ ] Chat input validation → **ALREADY DONE** ✅
- [ ] Pagination
- [ ] Privacy notice

---

## Deployment Checklist (Phases 8 & 11)

- [ ] Nginx security headers
- [ ] HTTPS with Let's Encrypt/platform
- [ ] Remove unnecessary `ports:` from services
- [ ] Add `HEALTHCHECK` to backend and frontend
- [ ] Enforce strong `AUTH_SECRET`, `ADMIN_PASSWORD_HASH`, `POSTGRES_PASSWORD`
- [ ] Set `NEXT_PUBLIC_API_URL` correctly in build
- [ ] Postgres backup plan (at minimum `pg_dump` instructions)

---

## Discovered During Work

*(Agent adds items found during work that aren't in the checklist above)*

- ~~**Test baseline failure:** `test_db_lifecycle.py::test_public_endpoints_with_override` fails with `AttributeError: 'coroutine' object has no attribute 'all'` at `content.py:28`. Root cause: async mock not properly awaited in test.~~ **FIXED** — `session.execute` changed from `return_value` to `AsyncMock(return_value=...)` so that `await session.execute()` returns a sync `MagicMock` with proper `.scalars().all()` chain. All 69 tests now pass.

---

## Progress Log

### Phase 0 — Discovery & Reality-Sync
- **Date:** 2026-07-02
- **Status:** COMPLETE
- **Actions:**
  - Read all documentation (README, spec, agent_state, contracts, audit reports)
  - Created this FIX_TRACKING.md with full checklist
  - Created STATE_RECONCILIATION.md with discrepancies
  - Ran baseline tests: Backend 1 failed / 68 passed, Frontend build SUCCESS
  - Verified key claims from audit report against actual code
- **Next:** Awaiting human confirmation to proceed to Phase 1
