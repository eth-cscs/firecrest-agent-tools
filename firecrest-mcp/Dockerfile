# ── Build stage ────────────────────────────────────────────────────────────────
FROM python:3.13-slim

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY pyproject.toml ./

COPY src/ ./src/                          

WORKDIR /app

COPY --chown=appuser:appgroup src/ ./src/

ENV PATH="/app/.venv/bin:/app/src:$PATH" \
    PYTHONPATH="/app" \             
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

EXPOSE 8888


CMD ["uv", "run", "src/server.py"]
