# make help          # list commands
# make dev           # development mode
# make up            # production stack
# make down
# make logs
# make migrate
# make migration msg="add index to events"
# make test          # run locally
# make shell-db


.PHONY: help up dev down restart logs ps build clean \
        migrate migration shell-api shell-db test test-docker \
        lint format

COMPOSE      = docker compose
COMPOSE_DEV  = $(COMPOSE) -f docker-compose.yml -f docker-compose.dev.yml
API_CONTAINER = event_hub_api
DB_CONTAINER  = event_hub_postgres

help: ## Show available commands
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

# --- Docker ---

up: ## Production stack (nginx + api + worker + db + redis)
	$(COMPOSE) up -d --build

dev: ## Dev mode: hot reload, pgAdmin, port 8000
	$(COMPOSE_DEV) up -d --build

down: ## Stop containers
	$(COMPOSE) down

restart: ## Restart api and worker
	$(COMPOSE) restart api worker

logs: ## Follow API logs
	$(COMPOSE) logs -f api

logs-all: ## Follow logs for all services
	$(COMPOSE) logs -f

ps: ## Show container status
	$(COMPOSE) ps

build: ## Rebuild images without starting
	$(COMPOSE) build

clean: ## Stop containers and remove volumes (database will be wiped!)
	$(COMPOSE) down -v

# --- Migrations ---

migrate: ## Apply Alembic migrations
	$(COMPOSE) exec api alembic upgrade head

migration: ## Create migration: make migration msg="add users table"
	$(COMPOSE) exec api alembic revision --autogenerate -m "$(msg)"

# --- Shell ---

shell-api: ## Open shell inside api container
	$(COMPOSE) exec api sh

shell-db: ## Open psql in postgres
	$(COMPOSE) exec db psql -U $${POSTGRES_USER:-auth_user} -d $${POSTGRES_DB:-auth_db}

# --- Tests ---

test: ## Run pytest locally (requires postgres + api/tests/.env.test)
	cd api && pytest -v

test-docker: ## Run pytest inside api container
	$(COMPOSE) exec api pytest -v

# --- Ruff ---
lint:
	cd api && ruff check .
	
format:
	cd api && ruff format .
