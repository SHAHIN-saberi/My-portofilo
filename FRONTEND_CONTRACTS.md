# FRONTEND_CONTRACTS.md
**Frontend Consumption Layer — Translated from SYSTEM_CONTRACTS.md**
**Purpose:** Define exactly how frontend must consume the backend without understanding internal logic.
**Source of Truth:** SYSTEM_CONTRACTS.md (frozen behavior)

---

## 1. Endpoint Consumption Table

| Endpoint                              | Method | Frontend Usage Pattern                                      | Expected Response Shape                          | Loading State | Error State | Retry Behavior          |
|---------------------------------------|--------|-------------------------------------------------------------|--------------------------------------------------|---------------|-------------|-------------------------|
| `/api/v1/chatbot/query`               | POST   | Send `{question, lang}` with rate limit awareness           | `{answer, status, sources}`                      | Show "Thinking..." | Show polite fallback message | Optional retry on "error" status |
| `/api/v1/profile?lang=en\|fa`         | GET    | Call on page load or lang change                            | `Envelope { data: Profile, meta: {lang} }`       | Skeleton      | Show error banner       | Auto-retry once         |
| `/api/v1/skills?lang=en\|fa&category` | GET    | Call on skills section load                                 | `Envelope { data: Skill[], meta }`               | Skeleton      | Show error banner       | Auto-retry once         |
| `/api/v1/experiences?lang=en\|fa`     | GET    | Call on experience section load                             | `Envelope { data: Experience[], meta }`          | Skeleton      | Show error banner       | Auto-retry once         |
| `/api/v1/education?lang=en\|fa`       | GET    | Call on education section load                              | `Envelope { data: Education[], meta }`           | Skeleton      | Show error banner       | Auto-retry once         |
| `/api/v1/projects?lang=en\|fa&featured` | GET  | Call on projects section load                               | `Envelope { data: Project[], meta }`             | Skeleton      | Show error banner       | Auto-retry once         |
| `/api/v1/courses?lang=en\|fa`         | GET    | Call on courses section load                                | `Envelope { data: Course[], meta }`              | Skeleton      | Show error banner       | Auto-retry once         |
| `/api/v1/certificates?lang=en\|fa`    | GET    | Call on certificates section load                           | `Envelope { data: Certificate[], meta }`         | Skeleton      | Show error banner       | Auto-retry once         |
| `/api/v1/social-links`                | GET    | Call on footer / contact area                               | `Envelope { data: SocialLink[] }`                | Skeleton      | Hide section or banner  | Auto-retry once         |
| `/health` or `/api/v1/health`         | GET    | Optional health ping (not required for normal flow)         | `HealthStatus`                                   | —             | —                       | —                       |

**Notes on Consumption:**
- All public endpoints return data inside `Envelope.data`
- `lang` parameter is always required for bilingual content
- Admin endpoints are **not** intended for frontend consumption

---

## 2. Error Handling Contract

**Frontend must treat these statuses exactly as defined:**

- `status: "answered"` → Normal successful response with `answer` + optional `sources`
- `status: "no_answer"` → Show polite message: “I don't have specific information about that...”
- `status: "error"` → Show polite fallback: “I'm sorry, I couldn't generate an answer right now...”

**General API Error Rules:**
- Any non-2xx response or network failure → Show generic error banner
- Never expose raw error messages to user
- All public content endpoints: on failure, show error banner + allow one automatic retry
- Chatbot endpoint: always degrades to one of the three fallback strings (never shows technical error)

**Rate Limit Behavior:**
- Chatbot endpoint is limited to 20 requests/minute
- On rate limit (429), frontend should show a temporary “Please wait a moment” message

---

## 3. Chatbot Rendering Contract

**Response Interpretation Rules:**

- `answer`: Always render as the main message (plain text)
- `status`:
  - `"answered"` → Show `answer` + render `sources` if present
  - `"no_answer"` → Show `FALLBACK_NO_ANSWER` text (no sources)
  - `"error"` → Show `FALLBACK_ERROR` text (no sources)
- `sources`: Array of objects with `source_type`, `source_id`, `score`
  - Only render when `status === "answered"` and `sources` is not null/empty
  - Frontend may display source_type + source_id as citation links (no further backend calls required)

**Rendering Constraints:**
- No streaming is implemented (responses are synchronous)
- Citations are **not** guaranteed to be present even on `"answered"`
- Never assume `sources` will contain human-readable titles

---

## 4. UI Failure States

**Required UI States Frontend Must Support:**

| Failure Type               | Required UI State                          | Allowed Message (from contract)                  |
|----------------------------|--------------------------------------------|--------------------------------------------------|
| Chatbot unrelated query    | Show `FALLBACK_UNRELATED`                  | “I'm the AI assistant for {name}'s professional profile...” |
| Chatbot no retrieval match | Show `FALLBACK_NO_ANSWER`                  | “I don't have specific information about that...” |
| Chatbot any error          | Show `FALLBACK_ERROR`                      | “I'm sorry, I couldn't generate an answer...”    |
| Public content load fail   | Error banner + retry button                | Generic: “Unable to load content”                |
| Network / timeout          | Error banner                               | “Connection issue. Please try again.”            |
| Rate limit hit             | Temporary message                          | “Please wait a moment before asking again.”      |

**Never show:**
- Raw exception messages
- Technical details
- Stack traces

---

## 5. Safe Assumptions List

**Frontend is allowed to assume:**

- All public endpoints return data wrapped in `Envelope`
- `lang` parameter always works with values `"en"` or `"fa"`
- Chatbot always returns one of three `status` values
- Fallback strings are stable and safe to display
- Sources (when present) contain only `source_type`, `source_id`, and `score`

**Frontend MUST NOT assume:**

- Any streaming capability exists
- `sources` will always be populated on successful answers
- Specific human-readable titles or metadata in sources
- Admin endpoints are accessible
- Reindex or knowledge-status endpoints are available to frontend
- Exact internal query rewriting or retrieval logic
- Behavior beyond what is explicitly listed in SYSTEM_CONTRACTS.md
- That `needs_clarification` path will ever return a question to the user

---

**END OF FRONTEND CONSUMPTION CONTRACTS**

This document translates the frozen backend behavior into safe, deterministic consumption rules for frontend implementation. No backend changes or assumptions beyond the contract layer are permitted.