.DEFAULT_GOAL := help

# ── Help ────────────────────────────────────────────────────────────────────────
.PHONY: help
help: ## Show available commands
	@awk 'BEGIN { FS = ":.*##"; section = "" } \
	      /^## / { printf "\n\033[1m%s\033[0m\n", substr($$0, 4) } \
	      /^[a-zA-Z_\/-]+:.*##/ { printf "  \033[36m%-22s\033[0m %s\n", $$1, $$2 }' \
	     $(MAKEFILE_LIST)

## Docker
.PHONY: up up/d down restart clean ps
up: ## Build and start all services (attached)
	docker compose up --build

up/d: ## Build and start all services (detached)
	docker compose up --build -d

down: ## Stop all services, keep volumes
	docker compose down

restart: ## Restart all running services
	docker compose restart

clean: ## Stop all services and wipe volumes (fresh DB)
	docker compose down -v

ps: ## Show running container status
	docker compose ps

## Docker — logs
.PHONY: logs logs/web logs/db
logs: ## Stream logs from all services
	docker compose logs -f

logs/web: ## Stream web (Django) logs
	docker compose logs -f web

logs/db: ## Stream Postgres logs
	docker compose logs -f db

## Docker — shell access
.PHONY: shell/web shell/db
shell/web: ## Open a shell in the running web container
	docker compose exec web sh

shell/db: ## Open psql in the running Postgres container
	docker compose exec db psql -U $${POSTGRES_USER:-rides} -d $${POSTGRES_DB:-rides}

## Django
.PHONY: migrate makemigrations shell test superuser
migrate: ## Apply pending database migrations
	docker compose exec web python manage.py migrate

makemigrations: ## Generate new migration files
	docker compose exec web python manage.py makemigrations

shell: ## Open the Django interactive shell
	docker compose exec web python manage.py shell

test: ## Run the test suite
	docker compose exec web python manage.py test

superuser: ## Create a Django superuser
	docker compose exec web python manage.py createsuperuser

## WSL Permission - Quick fix for permission issues when running Docker in WSL
permission-override: ## Override permissions for WSL / Linux users
	@echo "Overriding permissions for WSL..."
	@sudo chown -R $(USER):$(USER) .
