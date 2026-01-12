# Django + Stripe Checkout Demo

Демонстрационное приложение на **Django**, реализующее интеграцию с **Stripe Checkout**.
Проект показывает полный цикл оплаты товаров и заказов, работу с HTML-страницами,
мультивалютность, скидки и налоги.

Проект развёрнут онлайн и доступен для быстрого тестирования.

---

## 🌐 Онлайн-демо

**Основной домен:**  
https://stripedjango.ru

**Админка:**  
https://stripedjango.ru/admin/

**Тестовые страницы товаров:**
- https://stripedjango.ru/item/2/
- https://stripedjango.ru/item/3/
- https://stripedjango.ru/item/4/
- https://stripedjango.ru/item/5/
- https://stripedjango.ru/item/6/

При переходе на главную страницу (`/`) отображается стартовая страница
с навигацией в админку и к тестовым товарам.

---

## 🔐 Доступ в админку

```
login: admin
password: <предоставляется отдельно>
```

Через Django Admin можно:
- управлять товарами (Item);
- формировать заказы (Order) из нескольких товаров;
- добавлять скидки (Discount) и налоги (Tax);
- тестировать оплату заказов через Stripe Checkout.

---

## 💳 Тестовые данные карты (Stripe Test Mode)

Для тестирования оплаты используйте стандартные данные Stripe:

```
Card number: 4242 4242 4242 4242
Expiry date: любая будущая (например 12/34)
CVC: 123
Name: любое
```

Денежные средства не списываются — используется тестовый режим Stripe.

---

## ⚙️ Реализованный функционал

### Обязательная часть
- Django модель **Item** (`name`, `description`, `price`, `currency`)
- `GET /item/{id}` — HTML-страница товара с кнопкой оплаты
- `GET /buy/{id}` — создание Stripe Checkout Session и возврат `session_id`
- Редирект на Stripe Checkout через `stripe.redirectToCheckout`

### Бонусные задачи
- Docker и Docker Compose
- Использование environment variables
- Django Admin для управления моделями
- Онлайн-деплой на удалённом сервере
- Модель **Order** для оплаты нескольких товаров одной сессией
- Модели **Discount** и **Tax**
- Мультивалюта (USD / EUR)
- Отдельные Stripe keypair для разных валют
- HTTPS-домен (Caddy + automatic TLS)

---

## 🧱 Технологический стек

- Python 3
- Django
- Stripe API
- PostgreSQL
- Docker / Docker Compose
- Caddy
- uv
- Make

---

## 🐳 Запуск проекта через Docker

### Требования
- Docker
- Docker Compose (v2)
- GNU Make (опционально)

### 📦 Переменные окружения (.env)

Перед запуском необходимо создать файл `.env` в корне проекта.

Пример `.env`:

```env
# Django
DJANGO_SECRET_KEY=change-me
DJANGO_DEBUG=0
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

# Domain for Stripe redirect URLs
# IMPORTANT: must include scheme (http:// or https://), no trailing slash
APP_DOMAIN=http://localhost:8000

# PostgreSQL
POSTGRES_DB=stripe_db
POSTGRES_USER=stripe_user
POSTGRES_PASSWORD=stripe_pass
POSTGRES_HOST=stripe-db
POSTGRES_PORT=5432

# Stripe (test mode)
STRIPE_PUBLIC_KEY_USD=pk_test_...
STRIPE_SECRET_KEY_USD=sk_test_...

STRIPE_PUBLIC_KEY_EUR=pk_test_...
STRIPE_SECRET_KEY_EUR=sk_test_...
```

---

## 🚀 Запуск через Docker Compose

```bash
docker compose up --build
```

После запуска:
- http://localhost:8000/
- http://localhost:8000/admin/
- http://localhost:8000/item/1/

### Миграции и суперпользователь
```bash
docker compose exec stripe-web uv run python manage.py migrate
docker compose exec stripe-web uv run python manage.py createsuperuser
```

---

## 🛠️ Управление через Makefile

Проект поддерживает запуск через `make`.

Основные команды:

```bash
make build
make up
make down
make logs
make migrate
make createsuperuser
```

Пример Makefile:

```makefile
build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f

migrate:
	docker compose exec stripe-web python manage.py migrate

createsuperuser:
	docker compose exec stripe-web python manage.py createsuperuser
```

---

## ⚡ Работа с uv

В проекте используется **uv** для управления Python-зависимостями.

### Установка зависимостей
```bash
uv sync
```

### Локальный запуск Django
```bash
uv run python manage.py runserver
```

### Выполнение management-команд
```bash
uv run python manage.py migrate
uv run python manage.py createsuperuser
```

В Docker-контейнере `uv` используется для ускоренной и воспроизводимой установки зависимостей.

---

## 🧱 Продакшн-архитектура (контейнеры)

### stripe-web
Django backend, обрабатывает:
- страницы товаров и заказов;
- Stripe Checkout Session;
- админку и redirect-страницы.

### stripe-db
PostgreSQL база данных для хранения всех моделей проекта.

### stripe-caddy
Reverse proxy (Caddy):
- принимает HTTP/HTTPS трафик (80/443);
- автоматически получает TLS-сертификаты;
- проксирует запросы в `stripe-web`.

### stripe-vpn (опционально)
Контейнер gluetun (VPN), используется при необходимости маршрутизации трафика через VPN.

---

## 🌐 Схема трафика

```
Internet
   ↓
Caddy (HTTPS)
   ↓
Django (stripe-web)
   ↓
PostgreSQL (stripe-db)
```

