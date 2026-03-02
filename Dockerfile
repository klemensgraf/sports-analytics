# -- Use builder image from Astral
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
ENV UV_PYTHON_DOWNLOADS=0

WORKDIR /app
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

COPY . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --package sports_analytics

# Install dbt dependencies and parse the project
ENV DBT_TARGET=ci \
    PATH="/app/.venv/bin:$PATH"

RUN --mount=type=cache,target=/root/.cache \
    dagster-dbt project prepare-and-package --file src/sports_analytics/defs/project.py

# -- Use a final image without uv
FROM python:3.13-slim-bookworm

# Copy the application from the builder
COPY --from=builder /app /app

# Create non-root user
# RUN useradd -m -u 10001 appuser && chown -R appuser:appuser /app
# USER appuser

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

WORKDIR /app

EXPOSE 80
