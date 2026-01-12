FROM python:3.12-bookworm

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates curl \
    && update-ca-certificates \
    && rm -rf /var/lib/apt/lists/*


COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY pyproject.toml uv.lock ./

ENV UV_HTTP_TIMEOUT=180
ENV UV_HTTP_RETRIES=10

RUN uv sync --frozen

COPY . .

CMD ["uv", "run", "gunicorn", "stripe_demo.wsgi:application", "--bind", "0.0.0.0:8000"]
