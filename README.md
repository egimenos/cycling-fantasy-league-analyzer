# ProCyclingStats Scraper & Analyzer

A Python application that scrapes race data from `procyclingstats.com` and provides an API for cycling data analysis to be used in fantasy leagues.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start Guide](#quick-start-guide)
- [API Documentation](#api-documentation)
- [Available Commands](#available-commands)
- [Project Structure](#project-structure)
- [Common Workflows](#common-workflows)

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

### Step 2: Initialize Database

Start with a clean database and create the necessary tables:

```bash
# Reset database (deletes all existing data)
make db-reset

# Create database schema
make db-init
```

### Step 3: Scrape Data

Collect race and rider data for a specific year (this may take several minutes):

```bash
make scrape year=2023
```

### Step 4: Start API Server

In a **new terminal window**, start the FastAPI server:

```bash
make run-api
```

Keep this terminal running. The API will be available at `http://localhost:8000`

### Step 5: Analyze Cyclists

In **another terminal**, send a request to analyze specific cyclists:

```bash
curl -X POST "http://localhost:8000/v1/cyclists/process" \
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

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## Available Commands

Run `make help` to see all available commands. Here are the most important ones:

### 🐳 Docker Environment

| Command      | Description                         |
| ------------ | ----------------------------------- |
| `make up`    | Start all services in background    |
| `make down`  | Stop services (keeps database data) |
| `make build` | Rebuild Docker images               |
| `make logs`  | Follow application logs             |
| `make cli`   | Interactive shell in app container  |

### 🗄️ Database Management

| Command         | Description                                        |
| --------------- | -------------------------------------------------- |
| `make db-init`  | Initialize database schema (drops existing tables) |
| `make db-reset` | **⚠️ Reset entire database (deletes all data)**    |
| `make db-test`  | Test database connection                           |

### 🔄 Database Migrations

| Command                          | Description                   |
| -------------------------------- | ----------------------------- |
| `make migrate-new "description"` | Create new migration          |
| `make migrate-up`                | Apply pending migrations      |
| `make migrate-down -1`           | Rollback last migration       |
| `make migrate-history`           | Show migration history        |
| `make migrate-current`           | Show current migration status |

### 🚀 Application Tasks

| Command                 | Description                          |
| ----------------------- | ------------------------------------ |
| `make scrape year=YYYY` | Scrape data for specific year        |
| `make run-api`          | Start FastAPI server with hot reload |

## Project Structure

```
├── src/                    # Application source code
├── migrations/             # Database migrations
├── docker-compose.yml      # Docker services configuration
├── Dockerfile             # Application container definition
├── Makefile               # Development commands
├── .env.example           # Environment template
└── README.md              # This file
```

## Common Workflows

### 🔄 Daily Development

```bash
# Start services
make up

# Check logs
make logs

# Access container shell for debugging
make cli
```

### 📊 Adding New Data

```bash
# Scrape additional year
make scrape year=2024

# Or reset and scrape fresh data
make db-reset
make db-init
make scrape year=2023
```

### 🐛 Troubleshooting

```bash
# Rebuild if dependencies changed
make build

# Reset everything if issues persist
make down
make db-reset
make db-init
```

### 💾 Database Updates

```bash
# Create migration after model changes
make migrate-new "add new column to riders table"

# Apply migrations
make migrate-up

# Check migration status
make migrate-current
```

---

**⚠️ Important Notes:**

- `make db-reset` **permanently deletes all data**
- Keep the API server running in a separate terminal
- Scraping large datasets can take significant time
- Check API documentation at `/docs` for detailed endpoint information
