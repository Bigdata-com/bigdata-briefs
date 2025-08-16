FROM python:3.13.7-alpine

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Install system dependencies for uv and Python packages
RUN apk update && apk add --no-cache \
    curl \
    ca-certificates \
    build-base \
    libffi-dev \
    openssl-dev \
    sqlite-dev \
    gcc \
    musl-dev \
    git

# Create non-root user 'bigdata' and necessary directories
RUN adduser -D bigdata && \
    mkdir /code /data && \
    chown bigdata:bigdata /code /data

# Remove setuid and setgid permissions for extra security
RUN find / -perm +6000 -type f -exec chmod a-s {} \; || true

# Copy uv binary from external image before switching to non-root user
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
RUN chmod +x /bin/uv

# Switch to non-root user
USER bigdata
WORKDIR /code

# Copy project files
COPY pyproject.toml uv.lock README.md LICENSE /code/
COPY ./bigdata_briefs /code/bigdata_briefs

# Install project dependencies
RUN uv sync

# Expose service port
EXPOSE 8000

# Healthcheck to monitor container health
HEALTHCHECK --interval=30s --timeout=3s CMD curl http://localhost:8000/health || exit 1

# Set database connection string
ENV DB_STRING="sqlite:////data/bigdata_briefs.db"

# Launch application with uv
CMD ["uv", "run", "-m", "bigdata_briefs"]
