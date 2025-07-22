FROM python:3.11-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/

WORKDIR /code

COPY pyproject.toml uv.lock README.md LICENSE /code/
COPY ./bigdata_briefs /code/bigdata_briefs

RUN uv sync

CMD ["uv", "run", "-m", "bigdata_briefs"]