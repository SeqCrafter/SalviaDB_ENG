ARG PORT=8080

FROM python:3.12-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:0.12 /uv /bin/uv
COPY --from=oven/bun:1 /usr/local/bin/bun /usr/local/bin/bun

ENV UV_COMPILE_BYTECODE=1 \
    UV_PYTHON_DOWNLOADS=never \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

# ---------- Python dependencies ----------
COPY pyproject.toml uv.lock ./

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --python /usr/local/bin/python3.12 --frozen --no-install-project

# ---------- Application ----------
COPY . .

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --python /usr/local/bin/python3.12 --locked

# ---------- Reflex frontend ----------
ARG PORT
ARG API_URL

RUN --mount=type=cache,target=/root/.bun/install/cache \
    REFLEX_API_URL=${API_URL:-http\://localhost:$PORT} \
    reflex export --frontend-only --no-zip


# ============================================================
# Runtime
# ============================================================

FROM python:3.12-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        redis-server \
        ncbi-blast+ \
    && rm -rf /var/lib/apt/lists/*

COPY --from=caddy:2 /usr/bin/caddy /usr/bin/caddy

ARG PORT

ENV PATH="/app/.venv/bin:$PATH" \
    PORT=$PORT \
    REFLEX_REDIS_URL=redis://localhost \
    PYTHONUNBUFFERED=1 \
    SALVIADB_BLASTN_BIN=/usr/bin/blastn \
    SALVIADB_BLAST_DB=/data/blast/Salvia \
    BLASTDB=/data/blast

WORKDIR /app

RUN adduser \
        --disabled-password \
        --gecos "" \
        --home /app \
        reflex \
    && chown reflex /app \
    && mkdir -p /data/blast \
    && chown reflex:reflex /data/blast

COPY --chown=reflex --from=builder /app/.venv .venv
COPY --chown=reflex --from=builder /app/.web/backend .web/backend
COPY --from=builder /app/.web/build/client /srv
COPY --chown=reflex . .

USER reflex

RUN command -v reflex && ls -l /app/.venv/bin/reflex /app/.venv/bin/python && reflex --version

EXPOSE $PORT

CMD if [ -d alembic ]; then reflex db migrate; fi && \
    caddy start && \
    redis-server --daemonize yes && \
    exec reflex run --env prod --backend-only
