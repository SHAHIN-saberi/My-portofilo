# SYSTEM_RUNTIME_FREEZE.md
**Strict Runtime Drift Control & Execution Freeze**
**Date:** 2026-07-01
**Status:** FROZEN — NO FURTHER ARCHITECTURAL OR LOGICAL ABSTRACTIONS PERMITTED

---

## 1. Final Allowed Runtime Paths

The execution of data requests across the entire application must follow strictly deterministic single-path execution flows. No branching, guessing, or multi-source merging engines are permitted.

### Standard Public Content Flow
```text
Server Component (page.tsx) ──► serverApi.ts (fetch with ISR revalidate:60) ──► Backend API (:8000)
     │                                                                                                  │
     │                            [Server-side: Props passed to Client Component]                       │
     └──────────────────────────────────────────────────────────────────────────────────────────────────┘
     │
     ▼
Client Component (*Client.tsx) ──► Service Layer (public.service.ts) ──► API Gateway (api.ts) ──► Adapter Firewall (*.adapter.ts) ──► Backend API (:8000)
     ▲                                                                                                                                   │
     │                                     [Success: SafeAPIResponse<T>]                                                                │
     └───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
     │                                     [Failure / Null: Field-Level Coalescing ONLY]                                                 │
     └──────────────────────────────────── identity.ts (EMERGENCY FALLBACK ONLY) ────────────────────────────────────────────────────────┘
```
**Note:** Initial data is fetched server-side (SSR/ISR) for SEO and performance. Client-side re-fetch only occurs on language change or user interaction (e.g., filtering).

### Interactive RAG Chat Flow
```text
Chat UI (/chat) ──► Chat Service (chat.service.ts) ──► API Gateway (api.ts) ──► Chat Adapter (chat.adapter.ts) ──► POST /chatbot/query
     ▲                                                                                                                   │
     │                            [Deterministic Output: ChatStateModel (answered | no_answer | error)]                  │
     └───────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### Admin Portal Flow
```text
Admin UI (/admin/*) ──► Admin Service (admin.service.ts) ──► API Gateway (api.ts) [w/ Bearer Token] ──► Admin Adapter ──► Backend API (:8000)
```

---

## 2. Forbidden Runtime Paths

Any runtime execution matching the following patterns is strictly classified as **Architectural & Data Drift** and is prohibited:
1. **Direct UI Fetch:** Components calling `fetch()` or accessing browser APIs directly bypassing `services/`.
2. **Adapter Bypass:** Services returning raw backend payloads directly to UI components without adapter normalization.
3. **Identity Logic Overreach:** Using `identity.ts` for anything other than field-level null/undefined coalescing (`backendValue ?? IDENTITY_FALLBACK.field`).
4. **Chat Context Pollution:** Injecting static fallback data from `identity.ts` into RAG chatbot prompts or query payloads.
5. **Schema Guessing:** Adapters or components inventing synthetic data when JSON response shapes deviate from contracts.
6. **Implicit Transformation:** Silent type casting or fallback overriding without explicit state flag transitions.

---

## 3. Drift Definitions & Handling Rules

A **Runtime Drift** occurs when the execution state diverges from the locked deterministic contract.

| Drift Type | Strict Handling Rule |
| :--- | :--- |
| **Missing Backend Field (`null`/`undefined`)** | Coalesce strictly at field level (`backendField ?? IDENTITY_FALLBACK.field`). |
| **Missing API Response / Network Failure** | Surface UI error banner + enable field-level fallback display if applicable. |
| **Invalid / Malformed JSON** | Reject raw payload; route through `error.adapter.ts` (`MALFORMED_JSON`, 502 status). |
| **Unexpected Response Wrapper** | Route through `baseEnvelopeAdapter`; if envelope is missing, wrap safe data and flag `isValid: false`. |
| **Unauthorized Token (HTTP 401)** | Purge `localStorage("admin_token")` immediately and redirect route to `/admin/login`. |
| **Rate Limit Exceeded (HTTP 429)** | Abort retry attempts immediately; display temporary rate limit notice. |

---

## 4. UI State Guarantees

Every route and UI component guarantees deterministic rendering bound to specific state flags:

| Route / Component | Guaranteed UI States | State Mapping Logic |
| :--- | :--- | :--- |
| `/` (Home / Profile) | `loading`, `success`, `error` | Skeleton during fetch → Success renders Backend API runtime data with field-level coalescing against `IDENTITY_FALLBACK` → Error surfaces banner. |
| `/projects` | `loading`, `success`, `empty`, `error` | Skeleton during fetch → Empty if returned array length is 0 → Success renders card grid. |
| `/skills` | `loading`, `success`, `empty`, `error` | Skeleton during fetch → Category filter applied deterministically over adapter-processed items. |
| `/experience` | `loading`, `success`, `empty`, `error` | Skeleton during fetch → Renders bilingual timeline strictly ordered by `display_order`. |
| `/education` | `loading`, `success`, `empty`, `error` | Skeleton during fetch → Renders academic records without fallback interpolation. |
| `/chat` | `idle`, `loading`, `answered`, `no_answer`, `error` | Renders `res.state` explicitly. Renders `sources` array ONLY when `state === "answered"`. Displays Retry button on `error`. |
| `/admin/login` | `idle`, `loading`, `success`, `error` | Validates JWT token receipt; stores strictly under `admin_token`. |
| `/admin/dashboard` | `loading`, `success`, `error`, `unauthorized` | Validates token presence prior to mount; executes CRUD updates strictly against runtime backend. |

---

## 5. API Stability Guarantees

1. **Timeout Enforcement:** All requests going through `apiFetch` are bound by an immutable `AbortController` timeout (30 seconds default).
2. **Single-Attempt Retry:** Public content endpoints (`GET`) attempt exactly one automatic retry upon non-2xx network failure (excluding 401 and 429).
3. **No Retry on Mutation/Chat:** `POST`, `PUT`, `DELETE`, and `/chatbot/query` endpoints execute zero automatic retries to prevent duplicate side effects or token exhaustion.
4. **Structured Error Envelope:** All network exceptions and non-2xx responses normalize into `SafeError` (`{ message, status, code, isNormalized: true }`).

---

## 6. Fallback Policy (ONLY `identity.ts`)

1. **Sole Fallback File:** `frontend/lib/identity.ts` (`IDENTITY_FALLBACK`) is the only permitted fallback source in the entire frontend codebase.
2. **Field-Level Coalescing Only:** Fallback values may only be applied when a specific scalar field returned by the backend is `null` or `undefined`.
3. **No Object Merging Engines:** Deep object merging or recursive defaults outside simple nullish coalescing (`??`) are prohibited.
4. **No Admin Role:** `IDENTITY_FALLBACK` is strictly excluded from Admin CRUD mutation logic.

---

## 7. Failure Mode Matrix

| Scenario | API Layer Behavior | Adapter Layer Behavior | UI Rendering Output |
| :--- | :--- | :--- | :--- |
| **Backend Offline / Connection Refused** | Throws network error after attempt/retry | `errorAdapter` maps to `UNKNOWN_ERROR` (500) | Displays `ErrorBanner` ("Unable to load content") + renders emergency field-level static fallbacks. |
| **Request Timeout (>30s)** | `AbortController` signals cancellation | `errorAdapter` maps to `TIMEOUT` (408) | Displays `ErrorBanner` ("Request timed out. Please try again."). |
| **Chat Query Returns `status: "no_answer"`**| Returns 200 OK with payload | `chatAdapter` sets `state: "no_answer"` | Displays polite fallback string ("No relevant answer found..."). Hides citations. |
| **Chat Query Returns 429 Rate Limit** | Catches 429 status response | `errorAdapter` maps to `RATE_LIMIT` (429) | Displays temporary warning ("Please wait a moment before asking again."). |
| **Expired JWT Token on Admin Action** | Catches 401 Unauthorized response | `errorAdapter` maps to `UNAUTHORIZED` (401) | Intercepted by Admin layout/page; forces logout and redirects to `/admin/login`. |

---

**END OF SYSTEM RUNTIME FREEZE**
This document locks the runtime behavior of the frontend system. No architectural expansion or logic alterations are permitted beyond this boundary.
