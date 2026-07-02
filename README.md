# Personal AI Resume / Portfolio Platform

A professional, minimal, AI-augmented personal resume/portfolio website with a
DeepSeek-grounded chatbot, bilingual (English / Persian) content, and a single
admin panel. Built to run on a modest VPS.

> **Source of truth:** [`spec.md`](./spec.md). Implementation progress is tracked
> in [`agent_state.json`](./agent_state.json).

## Stack

| Layer     | Technology                                   |
|-----------|----------------------------------------------|
| Frontend  | Next.js 15 (App Router), Tailwind, next-themes |
| Backend   | FastAPI, SQLAlchemy (async), Alembic          |
| Database  | PostgreSQL + pgvector (1024-dim embeddings)   |
| AI        | DeepSeek API behind a swappable provider abstraction |
| Deploy    | Docker + docker-compose + nginx               |

## Repository layout

```
.
├── spec.md                 # Technical specification (source of truth)
├── agent_state.json        # Implementation memory / progress
├── docker-compose.yml      # postgres + backend + frontend + nginx
├── .env.example            # Environment template
├── backend/                # FastAPI app, migrations, tests
├── frontend/               # Next.js app
├── nginx/                  # Reverse proxy config
└── scripts/                # Dev / helper scripts
```

## Quick start (local, Docker)

```bash
# 1. Configure environment
cp .env.example .env
# edit .env: set POSTGRES_PASSWORD, DEEPSEEK_API_KEY, ADMIN_EMAIL, etc.

# 2. Generate an admin password hash and paste into ADMIN_PASSWORD_HASH
pip install bcrypt
python scripts/gen_password_hash.py 'your-admin-password'

# 3. Launch
sh scripts/dev.sh
```

- Frontend: http://localhost:3000
- API docs: http://localhost:8000/docs
- Admin: http://localhost:3000/admin

To stop: `sh scripts/down.sh`

## Development phases

Implementation follows the phased plan in `spec.md` / the agent prompt. Current
status lives in `agent_state.json`.

> Detailed backend/frontend setup and deployment notes are added as each phase
> is completed.
