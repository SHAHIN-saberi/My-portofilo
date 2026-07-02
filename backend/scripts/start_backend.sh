#!/bin/sh
# Backend container entrypoint: run migrations, then start uvicorn.
set -e

echo "[start_backend] Running database migrations..."
alembic upgrade head || echo "[start_backend] WARNING: alembic upgrade failed (no migrations yet?)"

echo "[start_backend] Starting FastAPI (uvicorn)..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
