# Базовый образ
FROM python:3.13-slim

# Переменные окружения
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# 1. Ставим uv (официальный бинарь)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# 2. Копируем только файлы зависимостей (для кеша)
COPY pyproject.toml uv.lock ./

# 3. Устанавливаем зависимости через uv
ENV UV_HTTP_TIMEOUT=180
ENV UV_HTTP_RETRIES=10
RUN uv sync

# 4. Копируем код проекта
COPY . .

# 5. Команда запуска (prod)
CMD ["uv", "run", "gunicorn", "stripe_demo.wsgi:application", "--bind", "0.0.0.0:8000"]
