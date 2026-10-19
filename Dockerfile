ARG PYTHON_IMAGE=python:3.13-alpine3.24

# ---- Build stage: install the project and its dependencies into a virtualenv ----
FROM ${PYTHON_IMAGE} AS builder

# Build tools are only needed to compile packages without prebuilt wheels
RUN apk add --no-cache build-base libffi-dev openssl-dev

COPY --from=ghcr.io/astral-sh/uv:0.13.1 /uv /bin/uv

# Use the image's Python so the virtualenv also works in the runtime stage
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=0

WORKDIR /code

# Install dependencies first so this layer is cached when only the code changes
COPY pyproject.toml uv.lock README.md LICENSE /code/
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev --no-install-project

COPY ./bigdata_briefs /code/bigdata_briefs
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev --no-editable

# ---- Runtime stage: only the Python runtime and the virtualenv ----
FROM ${PYTHON_IMAGE}

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/code/.venv/bin:$PATH"

# Apply the latest Alpine security patches and remove pip, which is not
# needed at runtime and ships its own vendored packages
RUN apk upgrade --no-cache && \
    python -m pip uninstall -y pip && \
    rm -rf /root/.cache

# Create non-root user 'bigdata' and necessary directories
RUN adduser -D bigdata && \
    mkdir /data && \
    chown bigdata:bigdata /data

# Remove setuid and setgid permissions for extra security
RUN find / -xdev -perm +6000 -type f -exec chmod a-s {} \; || true

COPY --from=builder --chown=bigdata:bigdata /code/.venv /code/.venv

# Switch to non-root user
USER bigdata
WORKDIR /code

# Expose service port
EXPOSE 8000

# Healthcheck to monitor container health (uses Python, so curl is not needed)
HEALTHCHECK --interval=30s --timeout=3s CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/health', timeout=2)"]

# Set database connection string
ENV DB_STRING="sqlite:////data/bigdata_briefs.db"

# Launch application
CMD ["python", "-m", "bigdata_briefs"]
