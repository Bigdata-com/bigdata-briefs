FROM python:3.11-slim-bookworm

# Ensure all binaries are up to date
RUN apt update && apt upgrade -y

# Remove setuid and setgid on all binaries
RUN RUN find / -perm +6000 -type f -exec chmod a-s {} \; || true

# Set-up non-root user to run the application
RUN adduser nonroot
RUN mkdir /code /data
RUN chown nonroot:nonroot /code /data
USER nonroot


# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/

WORKDIR /code

COPY pyproject.toml uv.lock README.md LICENSE /code/
COPY ./bigdata_briefs /code/bigdata_briefs

RUN uv sync

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s CMD curl http://localhost:8000/health || exit 1

ENV DB_STRING="sqlite:////data/bigdata_briefs.db"

CMD ["uv", "run", "-m", "bigdata_briefs"]