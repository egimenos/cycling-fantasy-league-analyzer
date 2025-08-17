# ProCyclingStats Scraper

This project is a Python application designed to scrape race data from `procyclingstats.com`. It is built following Domain-Driven Design (DDD) principles and runs entirely on Docker.

## 🚀 Quickstart

### Prerequisites

- Docker & Docker Compose
- `make` (usually pre-installed on Linux/WSL)

### 1. Setup Environment

This project uses a `.env` file for database configuration. Copy the example file to create your own local configuration. The default values are ready for local development.

```bash
cp .env.example .env
```

### 2. Build and Start Services

This command will build the Docker images and start the application and database containers in the background.

```bash
make up
```

### 3. Initialize the Database

The first time you run the project, you need to create the database tables.

```bash
make db-init
```

### 4. Run the Scraper

Execute the main use case to scrape all data for a specific year. You can pass the year as an argument.

```bash
# Scrape data for the year 2024
make scrape 2024
```

### 5. Access the Database

You can connect to the PostgreSQL database using your favorite client with the credentials found in the .env file. The default connection details are:

- **Host**: localhost
- **Port**: 5432
- **Database**: procyclingdb
- **User**: user
- **Password**: password

## Makefile Commands

A Makefile is provided for convenience. Run `make help` to see all available commands.

- **make up**: Starts all services in detached mode.
- **make down**: Stops and removes all services and data volumes.
- **make build**: Rebuilds the docker images if you change the code or dependencies.
- **make logs**: Follows the logs from the application container.
- **make cli**: Gets an interactive shell (bash) inside the application container, useful for debugging.
- **make db-init**: Initializes the database schema by creating all tables.
- **make scrape [YEAR]**: Runs the scraper for the specified year (e.g., `make scrape 2023`).
- **make run-api: Starts the FastAPI server with live reloading.

