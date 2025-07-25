FROM python:3.11-slim-bookworm

# Ensure all binaries are up to date
RUN apt update && apt upgrade -y

# Set-up non-root user to run the application
RUN adduser nonroot
RUN mkdir /code
RUN chown nonroot:nonroot /code
USER nonroot


# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/

WORKDIR /code

COPY pyproject.toml uv.lock README.md LICENSE /code/
COPY ./bigdata_briefs /code/bigdata_briefs

RUN uv sync

CMD ["uv", "run", "-m", "bigdata_briefs"]