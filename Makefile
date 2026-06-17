# make help          # список команд
# make dev           # разработка
# make up            # прод-стек
# make down
# make logs
# make migrate
# make migration msg="add index to events"
# make test          # локально
# make shell-db



.PHONY: help up dev down restart logs ps build clean \
        migrate migration shell-api shell-db test test-docker \
        lint format

COMPOSE      = docker compose
COMPOSE_DEV  = $(COMPOSE) -f docker-compose.yml -f docker-compose.dev.yml
API_CONTAINER = event_hub_api
DB_CONTAINER  = event_hub_postgres

help: ## Показать доступные команды
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

# --- Docker ---

up: ## Прод-стек (nginx + api + worker + db + redis)
	$(COMPOSE) up -d --build

dev: ## Dev-режим: hot reload, pgAdmin, порт 8000
	$(COMPOSE_DEV) up -d --build

down: ## Остановить контейнеры
	$(COMPOSE) down

restart: ## Перезапустить api и worker
	$(COMPOSE) restart api worker

logs: ## Логи API (follow)
	$(COMPOSE) logs -f api

logs-all: ## Логи всех сервисов
	$(COMPOSE) logs -f

ps: ## Статус контейнеров
	$(COMPOSE) ps

build: ## Пересобрать образы без запуска
	$(COMPOSE) build

clean: ## Остановить и удалить volumes (БД будет очищена!)
	$(COMPOSE) down -v

# --- Миграции ---

migrate: ## Применить миграции Alembic
	$(COMPOSE) exec api alembic upgrade head

migration: ## Создать миграцию: make migration msg="add users table"
	$(COMPOSE) exec api alembic revision --autogenerate -m "$(msg)"

# --- Shell ---

shell-api: ## Bash внутри api-контейнера
	$(COMPOSE) exec api sh

shell-db: ## psql в postgres
	$(COMPOSE) exec db psql -U $${POSTGRES_USER:-auth_user} -d $${POSTGRES_DB:-auth_db}

# --- Тесты ---

test: ## pytest локально (нужны postgres + api/tests/.env.test)
	cd api && pytest -v

test-docker: ## pytest внутри контейнера api
	$(COMPOSE) exec api pytest -v