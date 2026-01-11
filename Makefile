.PHONY: dev-up, dev-build, dev-down, dev-logs, dev-shell, dev-migrate, dev-admin, up, build, down, logs, clean, help

PROJECT_NAME := django-stripe-checkout
COMPOSE_DEV := docker compose -f docker-compose.dev.yml
COMPOSE_PROD := docker compose -f docker-compose.yml

.DEFAULT_GOAL := help

help:
	@echo "Available commands:"
	@echo ""
	@echo "DEV:"
	@echo "  make dev-up        Start dev environment"
	@echo "  make dev-build     Build dev images"
	@echo "  make dev-down      Stop dev environment"
	@echo "  make dev-logs      Show dev logs"
	@echo "  make dev-shell     Enter web container shell"
	@echo "  make dev-migrate   Run Django migrations"
	@echo "  make dev-admin     Create Django superuser"
	@echo ""
	@echo "PROD:"
	@echo "  make up            Start production environment"
	@echo "  make build         Build production images"
	@echo "  make down          Stop production environment"
	@echo "  make logs          Show production logs"
	@echo ""
	@echo "UTILS:"
	@echo "  make clean         Remove containers, volumes, images"

dev-up:
	$(COMPOSE_DEV) up --build

dev-build:
	$(COMPOSE_DEV) build

dev-down:
	$(COMPOSE_DEV) down

dev-logs:
	$(COMPOSE_DEV) logs -f --tail=200

dev-shell:
	$(COMPOSE_DEV) exec web bash

dev-migrate:
	$(COMPOSE_DEV) exec web uv run python manage.py migrate

dev-admin:
	$(COMPOSE_DEV) exec web uv run python manage.py createsuperuser


up:
	$(COMPOSE_PROD) up -d --build

build:
	$(COMPOSE_PROD) build

down:
	$(COMPOSE_PROD) down

logs:
	$(COMPOSE_PROD) logs -f --tail=200


clean:
	docker compose down -v --remove-orphans
	docker system prune -f
