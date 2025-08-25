.PHONY: help build up stop down logs cli scrape db-migrate db-init run-api migrate-new migrate-up migrate-down migrate-history migrate-current

ARGS = $(filter-out $@,$(MAKECMDGOALS))

help:
	@echo "Makefile for the ProCycling Scraper project"
	@echo "-------------------------------------------"
	@echo "Usage: make [command] [ARGS...]"
	@echo ""
	@echo "Docker Environment:"
	@echo "  up            Builds images if needed and starts all services"
	@echo "  stop          Stops all running services (keeps data)"
	@echo "  down          Stops services AND DELETES ALL DATA (volumes)"
	@echo "  build         Force a rebuild of the docker images"
	@echo "  logs          Follow the logs of the app container"
	@echo ""
	@echo "Application Tasks:"
	@echo "  cli           Get an interactive shell inside the app container"
	@echo "  scrape        Run the scraper. Usage: make scrape 2024"
	@echo "  db-migrate    Apply database migrations (alias of migrate-up head)"
	@echo "  migrate-new   Create a new migration from models. Usage: make migrate-new \"message text\""
	@echo "  migrate-up    Upgrade DB to latest (or target). Usage: make migrate-up [head|<rev>]"
	@echo "  migrate-down  Downgrade DB one or to target. Usage: make migrate-down [-1|<rev>]"
	@echo "  migrate-history Show migration history"
	@echo "  migrate-current Show current DB revision"

build:
	docker-compose build

up:
	docker-compose up -d --build

stop:
	docker-compose stop

down:
	docker-compose down --volumes

logs:
	docker-compose logs -f app

cli:
	docker-compose exec app /bin/bash

scrape:
	@$(eval YEAR := $(filter-out $@,$(MAKECMDGOALS)))
	@if [ -z "$(YEAR)" ]; then \
		echo "ERROR: Please provide a year. Usage: make scrape 2024"; \
		exit 1; \
	fi
	@echo "--- Running scraper for year $(YEAR) ---"
	docker-compose run --rm app python -m src.main scrape-year $(YEAR)

db-init:
	docker-compose exec app python -m src.main db-init

run-api:
	docker-compose run --rm -p 8001:8000 app uvicorn src.procycling_scraper.analysis.infrastructure.api.main:app --host 0.0.0.0 --port 8000 --reload

# --- Migration helpers (agnostic names) ---
migrate-new:
	@$(eval MSG := $(filter-out $@,$(MAKECMDGOALS)))
	@if [ -z "$(MSG)" ]; then \
		echo "ERROR: Please provide a revision message. Usage: make migrate-new \"add riders table\""; \
		exit 1; \
	fi
	docker-compose exec app alembic revision --autogenerate -m "$(MSG)"

migrate-up:
	@$(eval TARGET := $(filter-out $@,$(MAKECMDGOALS)))
	@if [ -z "$(TARGET)" ]; then \
		TARGET=head; \
	fi; \
	docker-compose exec app alembic upgrade $$TARGET

migrate-down:
	@$(eval TARGET := $(filter-out $@,$(MAKECMDGOALS)))
	@if [ -z "$(TARGET)" ]; then \
		TARGET=-1; \
	fi; \
	docker-compose exec app alembic downgrade $$TARGET

migrate-history:
	docker-compose exec app alembic history

migrate-current:
	docker-compose exec app alembic current

# Apply all migrations (alias)
db-migrate:
	docker-compose exec app alembic upgrade head

# Swallow extra args as no-op targets to avoid
# 'No rule to make target' when passing arguments like messages or years
%:
	@: