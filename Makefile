.PHONY: help build up stop down logs cli scrape db-migrate db-test

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
	@echo "  db-migrate    Apply database migrations. Creates/updates tables"
	@echo "  db-test       Run a simple database connection test"

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
	docker-compose exec app python -m src.main scrape-year $(YEAR)

db-init:
	docker-compose exec app python -m src.main db-init

run-api:
	docker-compose exec app uvicorn src.procycling_scraper.analysis.infrastructure.api.main:app --host 0.0.0.0 --port 8000 --reload