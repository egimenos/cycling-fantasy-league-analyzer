# ProCyclingStats Scraper & Analyzer

[![Tests](https://github.com/egimenos/cycling-fantasy-league-analyzer/actions/workflows/tests.yml/badge.svg)](https://github.com/egimenos/cycling-fantasy-league-analyzer/actions/workflows/tests.yml)
[![Lint](https://github.com/egimenos/cycling-fantasy-league-analyzer/actions/workflows/lint.yml/badge.svg)](https://github.com/egimenos/cycling-fantasy-league-analyzer/actions/workflows/lint.yml)
[![Type Check](https://github.com/egimenos/cycling-fantasy-league-analyzer/actions/workflows/type-check.yml/badge.svg)](https://github.com/egimenos/cycling-fantasy-league-analyzer/actions/workflows/type-check.yml)
[![Security](https://github.com/egimenos/cycling-fantasy-league-analyzer/actions/workflows/security.yml/badge.svg)](https://github.com/egimenos/cycling-fantasy-league-analyzer/actions/workflows/security.yml)
[![Docker Build](https://github.com/egimenos/cycling-fantasy-league-analyzer/actions/workflows/docker-build.yml/badge.svg)](https://github.com/egimenos/cycling-fantasy-league-analyzer/actions/workflows/docker-build.yml)

A Python application that scrapes race data from `procyclingstats.com` and provides an API for cycling data analysis to be used in fantasy leagues.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start Guide](#quick-start-guide)
- [API Documentation](#api-documentation)
- [Available Commands](#available-commands)
- [Project Structure](#project-structure)
- [Common Workflows](#common-workflows)
- [Observability](#observability-loki--grafana)
- [Testing](#testing)

## Prerequisites

- Docker & Docker Compose
- `make` (usually pre-installed on Linux/WSL)

## Quick Start Guide

This guide takes you from zero to a working cyclist analysis in 5 steps.

### Step 1: Environment Setup

Create your local configuration from the template:

```bash
cp .env.example .env
```

### Step 2: Start services

```bash
make up
```

### Step 3: Initialize Database

Initialize the schema (requires services running):

```bash
make db-init
```

### Step 4: Scrape Data

Collect race and rider data for a specific year (this may take several minutes):

```bash
make scrape 2023
```

### Step 5: Start API Server

In a new terminal window, start the FastAPI server:

```bash
make run-api
```

Keep this terminal running. The API will be available at `http://localhost:8001`.

### Step 6: Analyze Cyclists

In another terminal, send a request to analyze specific cyclists:

```bash
curl -X POST "http://localhost:8001/v1/cyclists/process" \
-H "Content-Type: application/json" \
-d '[
  {
    "name": "Pogacar Tadej",
    "team": "UAE Team Emirates",
    "price": 700
  },
  {
    "name": "Vingegaard",
    "team": "Team Visma | Lease a Bike",
    "price": 650
  },
  {
    "name": "M Van der Poel",
    "team": "Alpecin-Deceuninck",
    "price": 500
  }
]'
```

The API will return detailed analysis data for the matched riders.

## API Documentation

Once the API server is running, interactive documentation is available at:

- Swagger UI: http://localhost:8001/docs
- ReDoc: http://localhost:8001/redoc

## Available Commands

Run `make help` to see all available commands. Here are the most important ones:

### Docker Environment

| Command      | Description                                        |
| ------------ | -------------------------------------------------- |
| `make up`    | Start all services in background (build if needed) |
| `make stop`  | Stop services (keeps data)                         |
| `make down`  | Stop services and delete all data (volumes)        |
| `make build` | Force a rebuild of the docker images               |
| `make logs`  | Follow the logs of the app container               |
| `make cli`   | Get an interactive shell inside the app container  |

### Database Management

| Command           | Description                                    |
| ----------------- | ---------------------------------------------- |
| `make db-init`    | Initialize database schema                     |
| `make db-migrate` | Apply all migrations (alias of `upgrade head`) |

### Database Migrations

| Command                      | Description                             |
| ---------------------------- | --------------------------------------- |
| `make migrate-new "message"` | Create a new migration from models      |
| `make migrate-up`            | Upgrade DB to latest (or target)        |
| `make migrate-down -1`       | Downgrade last migration (or to target) |
| `make migrate-history`       | Show migration history                  |
| `make migrate-current`       | Show current DB revision                |

### Application Tasks

| Command            | Description                                 |
| ------------------ | ------------------------------------------- |
| `make scrape YYYY` | Scrape data for specific year               |
| `make run-api`     | Start FastAPI server with hot reload (8001) |

### Testing

| Command         | Description                       |
| --------------- | --------------------------------- |
| `make test`     | Run unit tests with pytest        |
| `make test-cov` | Run tests with coverage reporting |

- Tests run inside the Docker app container.
- Coverage report in terminal; XML report is generated for CI tools.

## Project Structure

```
├── src/                             # Application source code
├── alembic/                         # Alembic migrations (versions/)
├── grafana/
│   └── provisioning/                # Grafana provisioning (Loki datasource)
├── docker-compose.yml               # Docker services configuration
├── Dockerfile                       # Application container definition
├── Makefile                         # Development commands
├── pyproject.toml                   # Project configuration
├── requirements.txt                 # Python dependencies (optional)
├── tests/                           # Unit tests
└── README.md                        # This file
```

## Common Workflows

### Daily Development

```bash
# Start services
make up

# Check logs
make logs

# Access container shell for debugging
make cli
```

### Adding New Data

```bash
# Scrape additional year
make scrape 2024

# Or reset and scrape fresh data
make down        # deletes DB volume/data
make up
make db-init
make scrape 2023
```

### Troubleshooting

```bash
# Rebuild if dependencies changed
make build

# Reset everything if issues persist
make down
make up
make db-init
```

### Database Updates

```bash
# Create migration after model changes
make migrate-new "add new column to riders table"

# Apply migrations
make migrate-up

# Check migration status
make migrate-current
```

## Observability (Loki + Grafana)

This project ships container logs to Grafana Loki and lets you explore them in Grafana.

### Prerequisites

- Docker Loki logging driver installed on the host:
  - Install: `docker plugin install grafana/loki-docker-driver:latest --alias loki --grant-all-permissions`
  - Verify: `docker plugin ls` (should show `loki:latest ENABLED=true`)

### Stack startup

- Start services (Loki, Grafana, DB, App):
  - `docker compose up -d loki grafana db app`
- Check Loki is ready: `curl http://127.0.0.1:3100/ready` → `ready`
- Grafana UI: `http://localhost:3001`

### Docker logging driver

- The service `app` is configured to use the Loki logging driver in `docker-compose.yml`:
  - `logging.driver: loki`
  - `logging.options.loki-url: http://127.0.0.1:3100/loki/api/v1/push` (Linux host)
- Important: The driver only ships stdout/stderr of the container's main process (PID 1).
  - Commands run with `docker-compose exec` are NOT shipped to Loki.

### Emit logs

- Scraper (goes to Loki): `make scrape 2024`
- API (goes to Loki): `make run-api`
  - By default, the Makefile publishes API on `http://localhost:8001` (8001→8000).

### Grafana provisioning (optional, auto-setup)

To auto-provision the Loki datasource in Grafana:

- The repository includes `grafana/provisioning/datasources/loki.yml` which sets a default Loki datasource at `http://loki:3100`.
- `docker-compose.yml` mounts this folder into Grafana:
  - `./grafana/provisioning:/etc/grafana/provisioning`
- After `docker compose up -d grafana loki`, open Grafana and the datasource should already exist.

### Grafana data source

- In Grafana → Connections → Data sources → Add data source → Loki
  - URL: `http://loki:3100`
  - Save & Test should succeed

### Explore logs (examples)

- In Grafana Explore, run queries like:
  - `{compose_service="app"}`
  - `{container_name=~"procycling-scraper-app-run-.*"}`
- Since application logs are JSON (see `src/procycling_scraper/shared/logging_config.py`), you can parse them:
  - `{compose_service="app"} | json`
  - `{compose_service="app"} | json | line_format "{{.message}}"`
  - `{compose_service="app"} | json | level="INFO"`

### Troubleshooting

- No logs in Grafana:
  - Ensure you used `make scrape` or `make run-api` (not `docker-compose exec`).
  - Confirm Loki plugin installed/enabled: `docker plugin ls`.
  - Verify Loki URL in compose uses host IP (Linux: `127.0.0.1`).
  - Loki ready: `curl http://127.0.0.1:3100/ready` → `ready`.
  - In Grafana, check the Loki data source points to `http://loki:3100`.
- Port conflict when running API:
  - `run-api` maps `8001:8000` to avoid conflicts with the long-running app service.

## Testing

- Run unit tests: `make test`
- Run with coverage: `make test-cov`

Pytest runs inside the Docker app container. Tests live under the `tests/` folder.

---

⚠️ Important Notes:

- `make down` deletes all data volumes
- Keep the API server running in a separate terminal
- Scraping large datasets can take significant time
- Check API documentation at `/docs` for detailed endpoint information
