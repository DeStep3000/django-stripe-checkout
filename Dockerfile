FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY pyproject.toml uv.lock ./

ENV UV_HTTP_TIMEOUT=180
ENV UV_HTTP_RETRIES=10

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen

COPY . .

CMD ["uv", "run", "gunicorn", "stripe_demo.wsgi:application", "--bind", "0.0.0.0:8000"]
