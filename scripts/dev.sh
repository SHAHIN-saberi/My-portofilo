#!/bin/sh
# Bring up the full stack in the background (build on first run).
set -e
if [ ! -f .env ]; then
  echo "No .env found. Copy .env.example -> .env and fill in values first."
  exit 1
fi
docker compose up --build -d
echo "Stack starting. Frontend: http://localhost:3000  API docs: http://localhost:8000/docs"
