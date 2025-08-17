.PHONY: help build up down logs cli scrape db-init db-test

ARGS = $(filter-out $@,$(MAKECMDGOALS))

help:
	@echo "Makefile for the ProCycling Scraper project"
	@echo "-------------------------------------------"
	@echo "Usage: make [command] [ARGS...]"
	@echo ""
	@echo "Docker Commands:"
	@echo "  build         Build or rebuild the docker images"
	@echo "  up            Start all services in detached mode"
	@echo "  down          Stop and remove all services and volumes"
	@echo "  logs          Follow the logs of the app container"
	@echo ""
	@echo "Application Commands:"
	@echo "  cli           Get a shell inside the running app container"
	@echo "  scrape        Run the scraper for a specific year. Usage: make scrape 2024"
	@echo "  db-init       Initialize the database and create tables"
	@echo "  db-test       Run a simple database connection test"

build:
	docker-compose build

up:
	docker-compose up -d

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