# syntax=docker/dockerfile:1
FROM python:3.13-alpine AS builder

WORKDIR /app

# Install build dependencies
RUN apk add --no-cache build-base

# Copy only dependency files
COPY pyproject.toml uv.lock ./

# Install uv and dependencies
RUN pip install uv && uv sync --frozen --no-dev

# ----------------- Runtime Stage -----------------
FROM python:3.13-alpine AS runner

WORKDIR /app

# Non-root user and OS upgrade
RUN apk upgrade --no-cache && \
    pip uninstall -y setuptools msgpack || true && \
    addgroup -S appgroup && adduser -S appuser -G appgroup

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy application code
COPY app/ ./app/
COPY alembic.ini ./
COPY migrations/ ./migrations/

ENV PATH="/app/.venv/bin:$PATH"
ENV ENVIRONMENT="production"
ENV PYTHONUNBUFFERED=1

USER appuser

EXPOSE 8000

# We will run uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
