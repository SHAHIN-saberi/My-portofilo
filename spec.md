# Personal AI-Powered Resume / Portfolio Website
## Technical Specification

**Version:** 1.0  
**Date:** 2026-07-01  
**Status:** Implementation-Ready  
**Owner:** Single professional user (admin)  
**Audience:** Recruiters, clients, collaborators, and visitors seeking professional information

---

## 1. Overview

This specification defines a professional, minimal, AI-augmented personal resume/portfolio website. The system presents the owner's professional identity clearly across English and Persian, supports quick browsing via a hybrid site structure, and provides an AI chatbot grounded exclusively in the owner's data.

**Core technologies (locked):**
- Frontend: Next.js (App Router)
- Backend: FastAPI
- Database: PostgreSQL + pgvector
- AI: DeepSeek API (chat + embeddings) — provider abstraction required for future swaps
- Deployment target: Single VPS

**Key constraints (locked):**
- Single admin only
- No contact form (contact details displayed statically)
- Chatbot strictly limited to owner's professional profile, work, skills, projects, and background
- Content updates propagate quickly to both website and chatbot
- Hybrid architecture: one primary homepage + dedicated subpages for detailed sections
- Minimal, professional, modern UI with subtle animations and system-preference light/dark theme

The site serves as a primary professional asset for job applications and freelance proposals. The chatbot augments discoverability without replacing human contact.

---

## 2. Product Goals

The system must enable visitors to answer the following questions quickly and accurately:

- Who is this person?
- What do they do professionally?
- What are their key skills and abilities?
- What professional experience do they have?
- What education, courses, and certificates do they hold?
- What projects have they built (with details, tech, impact)?
- How can I contact them?
- Can an AI chatbot answer detailed, accurate questions about the above?

Secondary goals:
- Professional polish suitable for high-stakes use (recruiters, clients)
- Fast content updates by the owner without code changes
- Reliable, grounded chatbot behavior (no hallucinations of personal facts)
- Multilingual support (English + Persian) with seamless switching
- High maintainability and low operational overhead on a VPS

---

## 3. Non-Goals

- Blog, news, or community features
- Contact form or messaging system
- Multi-admin / role-based permissions
- Social networking features
- Analytics dashboards beyond basic
- E-commerce or lead capture forms
- Complex animations or heavy motion design
- General-purpose AI assistant (chatbot is owner-specific only)
- Self-hosted LLM inference (use external DeepSeek API)
- Mobile app or native clients
- Real-time collaboration

---

## 4. Assumptions

- The owner is a technical or professional individual with experience in software, design, or related fields.
- Content volume is modest (dozens of entries across sections).
- The owner is comfortable with basic admin UI and will provide accurate content.
- Persian support uses proper RTL handling and professional typography.
- Initial deployment uses a single modest VPS (2-4 vCPU, 4-8 GB RAM).
- DeepSeek API key is provided by owner (cost is owner responsibility).
- Visitors primarily access via desktop and mobile browsers.
- No PII beyond public professional contact details will be stored.
- Content will be maintained in both languages by the owner (or translated professionally).
- Vector dimensions for DeepSeek embeddings are 1024.

---

## 5. Information Architecture

### 5.1 Site Structure

**Hybrid structure (locked):**
- **Homepage** (`/` or `/{lang}/`): High-level overview and entry points.
- **Dedicated subpages** for detailed browsing.

**URL structure (SEO-friendly, clean):**
- `/` — Homepage (defaults to English; language switcher available)
- `/en` — English homepage
- `/fa` — Persian homepage
- `/en/projects`
- `/fa/projects`
- `/en/experience`
- `/fa/experience`
- `/en/skills`
- `/fa/skills`
- `/en/education`
- `/fa/education`

Language routing uses Next.js internationalized routing (preferred) or path-based locale detection with cookie fallback. Language switcher persists across pages.

**Navigation (global):**
- Logo / Name (links to home)
- Projects | Experience | Skills | Education
- Language toggle (EN / FA)
- Theme toggle (auto / light / dark)
- Chatbot trigger (floating action button)

**Admin access:** `/admin` (protected route). No public admin links.

### 5.2 Content Domains

All content domains must support full multilingual storage:

- Profile / Personal introduction (bio, title, summary, location)
- Skills / Abilities
- Work experience / Previous roles
- Education
- Courses
- Certificates
- Projects (including tech stack, links, impact)
- Social links / Contact information (static display only)
- AI knowledge entries (free-form grounding text for chatbot)

---

## 6. Public Pages

### 6.1 Homepage (`/`)

**Purpose:** Deliver the most important information at a glance. Primary conversion path to chatbot and subpages.

**Layout (desktop-first, responsive):**
1. **Hero section**
   - Large name + professional title (both languages)
   - Short 2-3 sentence summary
   - Primary CTA buttons: "View Projects", "Chat with me", "Download CV" (PDF link)
   - Professional photo (optional, square, optimized)
   - Subtle scroll indicator

2. **Quick Profile / About**
   - Condensed bio (2-3 paragraphs)
   - Location, availability status (e.g., "Open to opportunities")

3. **Skills Snapshot**
   - Horizontal or grid of top 8-12 skills with proficiency levels (visual bars or tags)
   - Link to full /skills page

4. **Experience Highlights**
   - 2-3 most recent or prominent roles (company, role, short impact)
   - Link to full /experience page

5. **Featured Projects**
   - 3-4 project cards (title, one-line description, tech tags, links)
   - Link to full /projects page

6. **Education & Credentials Snapshot**
   - Degree + institution highlights
   - 2-3 key certificates/courses
   - Link to /education

7. **Contact**
   - Direct display of email, phone (if public), LinkedIn, GitHub, other profiles
   - No form. Clear "Reach out via email" messaging

8. **Chatbot Widget**
   - Persistent floating button (bottom-right)
   - On click: slide-in or modal chat interface
   - Welcome message: "Ask me anything about [Name]'s background, skills, or projects."

**Mobile:** Collapse sections into accordion or vertical stack. Sticky nav.

**Data sources:** All sections pull live from backend public APIs.

### 6.2 Projects Page (`/en/projects`, `/fa/projects`)

- Header + intro text
- Filterable grid (by tech, year, featured)
- Cards: title, short description, tech stack chips, date range, "View details"
- Click opens **modal** (or dedicated lightweight detail view) with:
  - Full description (translated)
  - Role / responsibilities
  - Technologies used (linked to skills if possible)
  - Links (live site, GitHub, demo)
  - Impact / metrics (if provided)
- Pagination or infinite scroll (small data → all visible initially)

### 6.3 Experience Page (`/en/experience`, `/fa/experience`)

- Chronological or reverse-chronological list
- Each entry: Company, Role, Dates, Location, 3-6 bullet points (description)
- Optional company logo placeholder
- Group by company if multiple roles
- Link to projects where relevant (cross-reference)

### 6.4 Skills Page (`/en/skills`, `/fa/skills`)

- Categorized or flat list (e.g., Languages, Frameworks, Tools, Soft Skills)
- Visual indicators: proficiency level (Beginner/Intermediate/Advanced/Expert) + years
- Search / filter
- Each skill links to related projects/experience where used (if data available)

### 6.5 Education Page (`/en/education`, `/fa/education`)

- Sections:
  - Formal Education (degrees)
  - Courses
  - Certificates
- List view with:
  - Institution / Provider
  - Title / Degree
  - Dates
  - Description / focus
  - Credential link (if available)
- Chronological or grouped

**Rendering strategy:** All pages use server-side rendering (Next.js Server Components) where possible for SEO and performance. Client hydration only for interactive elements (chat, filters, theme).

---

## 7. Admin Panel

**Access:** `/admin` — password-protected single-admin interface.  
**Auth:** Simple email + password (hashed in DB or env). Session via secure HTTP-only cookie or short-lived JWT. Logout explicit.

**Capabilities (required):**

- **Profile**
  - Edit name, title, photo URL, location, availability
  - Edit bio/summary (separate fields per language)

- **Skills**
  - CRUD: name (per lang), category, proficiency, order
  - Bulk reorder

- **Experience**
  - CRUD entries (company, role per lang, dates, location, description)
  - Reorder

- **Education**
  - CRUD formal education entries

- **Courses & Certificates**
  - Separate or combined CRUD with provider, title (per lang), dates, URL, description

- **Projects**
  - CRUD: title (per lang), description (per lang), dates, tech stack (multi-select from skills or free tags), URLs, featured flag, impact text
  - Upload or link assets (images) via URL only

- **Social / Contact**
  - Edit list of links: label, URL, icon (predefined set)
  - Email, phone (optional), location

- **AI Knowledge Entries** (dedicated)
  - Free-text entries for chatbot grounding
  - Title + content (per language)
  - Priority / weight
  - CRUD + search

- **Content Reindexing**
  - Prominent "Reindex Chatbot Knowledge" button
  - Status indicator (last indexed timestamp)
  - Optional: "Auto-reindex on save" toggle (default: on for small datasets)

**Admin UI style:** Same minimal/professional theme as public site. Use table + form patterns. Simple inline editing where possible. Confirmation modals for deletes.

**No multi-user features.** Single hardcoded or DB row admin account.

**Data flow:** All edits go through FastAPI admin endpoints → DB. Public pages and chatbot read from same DB.

---

## 8. Data Model

**Design philosophy:** Purely relational core for predictability, referential integrity, and efficient queries. Separate normalized translation tables for multilingual content (as required). JSONB used sparingly for flexible metadata only (e.g., tech stack arrays, links).

**Why relational + translation tables (not JSONB per language or single table):**
- Clean separation of translatable vs. structural data
- Efficient querying by language
- Easier admin forms and validation
- Better for pgvector indexing (source data stays clean)
- Future-proof for adding languages
- Avoids duplication of non-text fields

### Core Tables (PostgreSQL)

```sql
-- Extensions
CREATE EXTENSION IF NOT EXISTS vector;

-- Profiles (single row expected)
CREATE TABLE profiles (
    id SERIAL PRIMARY KEY,
    photo_url TEXT,
    email TEXT,
    phone TEXT,
    location TEXT,
    availability_status TEXT,
    github_url TEXT,
    linkedin_url TEXT,
    website_url TEXT,
    cv_pdf_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE profile_translations (
    id SERIAL PRIMARY KEY,
    profile_id INTEGER REFERENCES profiles(id) ON DELETE CASCADE,
    lang VARCHAR(2) NOT NULL CHECK (lang IN ('en', 'fa')),
    title TEXT,
    summary TEXT,
    bio TEXT,
    UNIQUE (profile_id, lang)
);

-- Skills
CREATE TABLE skills (
    id SERIAL PRIMARY KEY,
    category TEXT,           -- e.g. 'Languages', 'Frameworks'
    proficiency TEXT CHECK (proficiency IN ('beginner','intermediate','advanced','expert')),
    years_experience NUMERIC(4,1),
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE skill_translations (
    id SERIAL PRIMARY KEY,
    skill_id INTEGER REFERENCES skills(id) ON DELETE CASCADE,
    lang VARCHAR(2) NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    UNIQUE (skill_id, lang)
);

-- Experiences
CREATE TABLE experiences (
    id SERIAL PRIMARY KEY,
    company TEXT NOT NULL,
    start_date DATE,
    end_date DATE,
    is_current BOOLEAN DEFAULT FALSE,
    location TEXT,
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE experience_translations (
    id SERIAL PRIMARY KEY,
    experience_id INTEGER REFERENCES experiences(id) ON DELETE CASCADE,
    lang VARCHAR(2) NOT NULL,
    role TEXT NOT NULL,
    description TEXT,
    UNIQUE (experience_id, lang)
);

-- Education
CREATE TABLE educations (
    id SERIAL PRIMARY KEY,
    institution TEXT NOT NULL,
    start_date DATE,
    end_date DATE,
    location TEXT,
    display_order INTEGER DEFAULT 0
);

CREATE TABLE education_translations (
    id SERIAL PRIMARY KEY,
    education_id INTEGER REFERENCES educations(id) ON DELETE CASCADE,
    lang VARCHAR(2) NOT NULL,
    degree TEXT NOT NULL,
    field_of_study TEXT,
    description TEXT,
    UNIQUE (education_id, lang)
);

-- Courses
CREATE TABLE courses (
    id SERIAL PRIMARY KEY,
    provider TEXT,
    completion_date DATE,
    credential_url TEXT,
    display_order INTEGER DEFAULT 0
);

CREATE TABLE course_translations (
    id SERIAL PRIMARY KEY,
    course_id INTEGER REFERENCES courses(id) ON DELETE CASCADE,
    lang VARCHAR(2) NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    UNIQUE (course_id, lang)
);

-- Certificates
CREATE TABLE certificates (
    id SERIAL PRIMARY KEY,
    issuer TEXT,
    issue_date DATE,
    credential_url TEXT,
    display_order INTEGER DEFAULT 0
);

CREATE TABLE certificate_translations (
    id SERIAL PRIMARY KEY,
    certificate_id INTEGER REFERENCES certificates(id) ON DELETE CASCADE,
    lang VARCHAR(2) NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    UNIQUE (certificate_id, lang)
);

-- Projects
CREATE TABLE projects (
    id SERIAL PRIMARY KEY,
    start_date DATE,
    end_date DATE,
    live_url TEXT,
    github_url TEXT,
    featured BOOLEAN DEFAULT FALSE,
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE project_translations (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
    lang VARCHAR(2) NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    role TEXT,
    impact TEXT,
    UNIQUE (project_id, lang)
);

-- Project skills (many-to-many)
CREATE TABLE project_skills (
    project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
    skill_id INTEGER REFERENCES skills(id) ON DELETE CASCADE,
    PRIMARY KEY (project_id, skill_id)
);

-- Social / Contact links
CREATE TABLE social_links (
    id SERIAL PRIMARY KEY,
    platform TEXT NOT NULL,   -- e.g. 'linkedin', 'github', 'twitter'
    url TEXT NOT NULL,
    display_order INTEGER DEFAULT 0,
    is_visible BOOLEAN DEFAULT TRUE
);

-- AI Knowledge Entries (free-form grounding)
CREATE TABLE ai_knowledge_entries (
    id SERIAL PRIMARY KEY,
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE ai_knowledge_translations (
    id SERIAL PRIMARY KEY,
    entry_id INTEGER REFERENCES ai_knowledge_entries(id) ON DELETE CASCADE,
    lang VARCHAR(2) NOT NULL,
    title TEXT,
    content TEXT NOT NULL,
    UNIQUE (entry_id, lang)
);

-- Vector store for RAG (chatbot knowledge)
CREATE TABLE knowledge_chunks (
    id BIGSERIAL PRIMARY KEY,
    source_type TEXT NOT NULL,      -- 'profile', 'experience', 'project', 'skill', 'education', 'course', 'certificate', 'ai_knowledge'
    source_id INTEGER NOT NULL,
    lang VARCHAR(2) NOT NULL,
    chunk_text TEXT NOT NULL,
    embedding VECTOR(1024) NOT NULL,
    metadata JSONB DEFAULT '{}',    -- e.g. {"title": "...", "company": "..."}
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_knowledge_chunks_embedding ON knowledge_chunks USING hnsw (embedding vector_cosine_ops);
CREATE INDEX idx_knowledge_chunks_source ON knowledge_chunks (source_type, source_id, lang);
CREATE INDEX idx_knowledge_chunks_lang ON knowledge_chunks (lang);

-- Single admin account (simple)
CREATE TABLE admin_users (
    id SERIAL PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

**Relationships:**
- Projects ↔ Skills via junction table
- All major entities link to translations (1:many)
- knowledge_chunks references source entities for traceability and reindexing
- No circular references

**Admin writes to source tables.** RAG index is derived.

---

## 9. Multilingual Strategy

- **Languages:** `en` (English), `fa` (Persian)
- **Storage:** Dedicated translation tables (see Data Model)
- **Frontend:** Next.js `next-intl` or custom locale context + dictionaries. Use `app/[lang]/` route groups.
- **RTL handling:** Tailwind `dir="rtl"` on `<html>` or body for `fa`. Separate font stacks (e.g. Inter + Vazirmatn or system Persian fonts).
- **Fallback:** Missing translations fall back to English.
- **Chatbot:** Accepts `lang` parameter. Retrieves chunks for that language + English as fallback. Generates response in requested language.
- **Admin:** Bilingual fields shown side-by-side or tabbed.
- **SEO:** `<html lang="...">`, `hreflang` links, translated meta titles/descriptions per page.

---

## 10. Chatbot Behavior

**Strict scope:** Questions about the owner only (identity, skills, experience, education, courses, certificates, projects, technologies, work details, contact).

### Decision Flow (server-side)

1. **Relevance Gate**
   - Embed user question.
   - Retrieve top-5 chunks using cosine similarity (pgvector `<=>`).
   - If no chunks or max similarity < 0.65 → treat as "no relevant info".
   - Optional lightweight LLM classification: "Is this question about [Owner Name]'s professional profile? Answer YES or NO only."

2. **If relevant and context found**
   - Pass top chunks + user question to LLM.
   - System prompt enforces:
     - Use retrieved context as primary source.
     - May use general knowledge only to explain technical concepts naturally (e.g. "React is a JavaScript library...").
     - Never invent personal facts, dates, projects, or achievements.
     - Be concise, professional, friendly.

3. **If relevant but incomplete / no exact match**
   - Answer from available data.
   - Clearly indicate limitations if needed.
   - Offer to contact for more details.

4. **If unrelated**
   - "I'm the AI assistant for [Name]'s professional profile. I can only answer questions about their background, skills, experience, and projects. How can I help with that?"

5. **If no relevant answer**
   - "I don't have specific information about that in [Name]'s profile. Please reach out directly using the contact details on the site."

**Tone requirements (enforced in system prompt):**
- Natural, professional, concise
- Friendly but not overly casual
- Light, controlled humor only when appropriate
- Never careless or misleading

**Safety:** All answers must be traceable to retrieved chunks. Include optional "Sources" in admin debug mode only (not shown to users).

**UI:** Clean chat interface with typing indicator, message history (session only), copy button, clear conversation.

**Limits:** Max 8-10 turns per session. Rate limit per IP (e.g., 20 messages / 5 min).

---

## 11. RAG Architecture

**Vector store:** PostgreSQL + pgvector (HNSW index on cosine similarity). No external vector DB.

**Embedding model (DeepSeek):** `deepseek-embed` (1024 dimensions).

**Ingestion / Reindex Flow (simplest VPS-friendly):**

1. Admin clicks "Reindex" (or auto on save for small data).
2. FastAPI background task (or synchronous for <500 chunks):
   - Delete all existing `knowledge_chunks`.
   - For every translatable entity (profile, experiences, projects, etc.):
     - Fetch all translations (en + fa).
     - For each language:
       - Extract text fields (title + description + impact + etc.).
       - Simple chunking strategy:
         - Split on paragraphs or sentences.
         - Target chunk size: 300–500 characters.
         - Overlap: 50 characters.
         - Preserve metadata (source_type, source_id, title, company, etc.).
   - Batch embed all chunks (DeepSeek /embeddings endpoint).
   - Bulk INSERT into `knowledge_chunks`.
3. Record `last_indexed_at` timestamp.

**Retrieval Flow:**
- User question + lang → embed question.
- `SELECT ... FROM knowledge_chunks WHERE lang = ? ORDER BY embedding <=> query_embedding LIMIT 6`
- Optional metadata filter (e.g. only recent projects).
- Return chunks + metadata to LLM context.

**Chunking strategy:** Fixed-size paragraph-aware (no complex recursive). Keep simple.

**Update speed:** Reindex completes in <10 seconds for typical personal portfolio content.

**Fallback:** If embedding or retrieval fails, chatbot falls back to polite redirect to contact details.

**Preventing unrelated answers:** 
- Relevance threshold on similarity
- Explicit system prompt guardrails
- Post-generation validation prompt (optional lightweight)

---

## 12. AI Provider Abstraction

**Interface (FastAPI):**

```python
from abc import ABC, abstractmethod

class AIProvider(ABC):
    @abstractmethod
    def embed(self, text: str) -> list[float]: ...
    
    @abstractmethod
    def chat(self, messages: list[dict], context: str | None = None) -> str: ...
    
    @abstractmethod
    def chat_stream(self, ...): ...
```

**Current implementation:** `DeepSeekProvider`
- Base URL: `https://api.deepseek.com/v1`
- Models:
  - Embeddings: `deepseek-embed`
  - Chat: `deepseek-chat-v3` (or `deepseek-chat`)
- Uses `httpx` (or official OpenAI-compatible SDK).
- API key from env `DEEPSEEK_API_KEY`.

**Swappability:**
- New provider implements the same abstract class.
- Dependency injection in FastAPI (e.g., `get_ai_provider()`).
- Config via environment variable `AI_PROVIDER=deepseek`.
- No changes to RAG or chatbot logic required.

**Rate limiting / error handling:** Built into provider + FastAPI middleware.

---

## 13. API Design

**Base:** FastAPI at `/api/v1`

**Public (no auth):**
- `GET /api/v1/profile?lang=en`
- `GET /api/v1/skills?lang=en&category=...`
- `GET /api/v1/experiences?lang=en`
- `GET /api/v1/projects?lang=en&featured=true`
- `GET /api/v1/education?lang=en`
- `GET /api/v1/courses?lang=en`
- `GET /api/v1/certificates?lang=en`
- `GET /api/v1/social-links`
- `POST /api/v1/chatbot/query` — `{ "question": "...", "lang": "en" }`

**Admin (auth required — header `Authorization: Bearer <token>`):**
- Full CRUD for all entities (`POST /api/v1/admin/projects`, `PUT /...`, `DELETE`)
- `POST /api/v1/admin/reindex`
- `GET /api/v1/admin/knowledge-status`

**Response format:** Consistent JSON with `data`, optional `meta`.

**Validation:** Pydantic models for all requests/responses.

**Error handling:** Standard HTTP codes + structured errors.

**OpenAPI:** Auto-generated docs at `/docs`.

---

## 14. Frontend Architecture

**Framework:** Next.js 15+ (App Router)

**Directory structure:**
```
app/
  [lang]/
    layout.tsx
    page.tsx                 # homepage
    projects/
      page.tsx
    experience/
      page.tsx
    skills/
      page.tsx
    education/
      page.tsx
  admin/
    layout.tsx
    page.tsx
  api/                       # optional proxy if needed
  components/
    ui/ (minimal shadcn or custom)
    Chatbot.tsx
    ProjectCard.tsx
    ...
  lib/
    api.ts
    i18n.ts
```

**Key libraries:**
- `next-intl` or custom i18n
- `framer-motion` (subtle only)
- `tailwindcss`
- `react-hook-form` + zod (admin)
- `swr` or TanStack Query (client data)
- Lucide icons

**Rendering:**
- Public pages: Server Components + streaming where beneficial
- Chatbot: Client component
- Admin: Client-heavy with optimistic updates

**Theme:** `next-themes` + system preference detection. CSS variables for light/dark.

**Animations:** Framer-motion for:
- Page transitions (fade)
- Chat message entry
- Card hover lift (subtle)
- Modal open/close

**Performance:**
- Image optimization (`next/image`)
- Static generation where content rarely changes
- Revalidate on demand via webhook or manual
- Code splitting

**Content mapping:** Public pages fetch from FastAPI on server (or use ISR). Pass data as props.

---

## 15. Backend Architecture

**Framework:** FastAPI

**Structure:**
```
backend/
  app/
    main.py
    api/
      public.py
      admin.py
      chatbot.py
    core/
      config.py
      security.py
    db/
      models.py
      session.py
    services/
      rag.py
      reindex.py
      ai_provider/
        base.py
        deepseek.py
    schemas/
      ...
  alembic/
  tests/
```

**Key components:**
- SQLAlchemy + async (or sync for simplicity)
- Pydantic v2
- Alembic for migrations
- Background tasks via `BackgroundTasks` (FastAPI built-in)
- CORS configured for Next.js origin

**Auth:** Simple bearer token. Password hashed with bcrypt. Admin token issued on login.

**Chatbot endpoint flow:**
1. Validate question
2. Relevance + retrieval (services/rag.py)
3. Call AI provider
4. Return answer + optional sources (internal)

**Reindex:** Isolated service that can be called synchronously or in background.

---

## 16. Deployment on VPS

**Recommended stack:**
- Docker + docker-compose (strongly preferred for maintainability)
- Or native: Nginx + uvicorn + pm2 (Next.js) + PostgreSQL

**docker-compose.yml outline:**
- `postgres` (with pgvector)
- `backend` (FastAPI)
- `frontend` (Next.js standalone)
- `nginx` (reverse proxy, SSL)

**Environment variables (example):**
```
DATABASE_URL=postgresql+asyncpg://...
DEEPSEEK_API_KEY=...
ADMIN_EMAIL=...
ADMIN_PASSWORD_HASH=...
NEXT_PUBLIC_API_URL=...
```

**Migration & startup:**
- `alembic upgrade head` on backend start
- `CREATE EXTENSION vector;` handled in migration

**Process management:** systemd or Docker restart policies.

**Backups:** Daily `pg_dump` to local or S3-compatible.

**SSL:** Let's Encrypt via nginx or Caddy.

**Monitoring (minimal):** 
- Basic health endpoints
- Log aggregation (journald or simple file)
- Uptime check via external service (optional)

**CI/CD (optional for MVP):** Git push → simple deploy script on VPS (pull + rebuild).

---

## 17. SEO and Performance

**SEO:**
- Next.js Metadata API per page (title, description, open graph)
- Dynamic `hreflang` alternate links
- JSON-LD structured data (Person + Resume-like)
- Sitemap + robots.txt generated
- Clean semantic HTML
- Fast-loading hero images (WebP)

**Performance:**
- Lighthouse targets: 90+ Performance, 95+ Accessibility, 90+ SEO
- Server-side rendering + selective client hydration
- Image optimization + lazy loading
- Minimal JS bundle
- Font subsetting
- Caching: public API responses (60s), static assets (long)
- pgvector query < 50ms target

---

## 18. Security Considerations

- All admin routes protected by token
- Passwords hashed (bcrypt)
- Input validation + sanitization (Pydantic + SQLAlchemy)
- CORS restricted to frontend domain
- Rate limiting on chatbot (IP + token)
- No secrets in client bundle
- HTTPS enforced
- SQL injection prevented by ORM
- Content Security Policy headers
- Regular dependency updates
- Vector store isolated from public write paths
- Chatbot guardrails prevent prompt injection via strict system prompts + retrieval-only context

**Data minimization:** Only professional public information stored.

---

## 19. Acceptance Criteria

The implemented system must satisfy:

1. **Public site** renders correctly in both languages with accurate content.
2. All required sections (profile, skills, experience, education, courses, certificates, projects, contact) are present and editable.
3. Homepage provides quick answers to "who / what / skills / experience / projects / contact".
4. Subpages load detailed information.
5. Chatbot:
   - Refuses unrelated questions politely.
   - Answers only using retrieved knowledge.
   - Never hallucinates personal facts.
   - Uses limited general knowledge only for phrasing.
   - Redirects to contact details when appropriate.
6. Admin panel allows full CRUD of all content domains.
7. Reindexing updates chatbot knowledge within 30 seconds of trigger.
8. Theme follows system preference; subtle animations present.
9. Site is responsive and loads quickly.
10. Deployment succeeds on VPS with docker-compose (or documented equivalent).
11. Multilingual content displays correctly (including RTL for Persian).
12. No contact form exists.
13. API is documented and versioned.

---

## 20. Open Questions

- Exact DeepSeek model names at implementation time (use latest stable `deepseek-chat` / `deepseek-embed`).
- Whether to support PDF resume generation from profile data (out of scope for v1).
- Specific visual examples or brand assets (owner to provide).
- Target chunk size / similarity threshold tuning (to be validated during implementation).

---

**End of Specification**

This document is the single source of truth. Any deviation requires explicit update to this spec. All implementation decisions should favor the simplest maintainable approach that satisfies the locked constraints.