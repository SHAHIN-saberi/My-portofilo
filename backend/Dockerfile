# ---- Backend: FastAPI ----
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# System deps (build tools kept minimal; slim + wheels where possible)
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# Entrypoint runs migrations then starts the server (see scripts/start_backend.sh)
CMD ["sh", "scripts/start_backend.sh"]
