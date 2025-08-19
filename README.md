# ProCyclingStats Scraper & Analyzer

This project is a Python application designed to scrape race data from `procyclingstats.com` and provide an API for data analysis. It is built following Domain-Driven Design (DDD) principles and runs entirely on Docker.

## 🚀 Quickstart: Full Workflow Example

This example shows the end-to-end process: from a clean slate to getting a rider analysis via the API.

### Prerequisites

- Docker & Docker Compose
- `make` (usually pre-installed on Linux/WSL)

### 1. Setup Environment

First, create your local configuration file from the provided template.

```bash
cp .env.example .env
```

### 2. Reset and Initialize the Database

To start from a completely clean state, this command will stop any running services, **delete all existing data**, and restart the services with a fresh, empty database.

```bash
make db-reset
```

Now, create the necessary tables in the new database.

```bash
make db-init
```

### 3. Populate the Database with Data

Run the scraper for a specific year to collect race and rider data. This process can take several minutes.

```bash
make scrape year=2023
```

### 4. Start the API Server

In a **separate terminal window**, start the FastAPI server. Leave this terminal running.

```bash
make run-api
```

### 5. Get a Rider Analysis

In **another terminal window**, send a POST request to the analysis endpoint with the cyclists you want to evaluate.

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

The API will return a JSON response with the matched riders from your database.

## API Documentation

Once the API server is running (`make run-api`), the interactive documentation is automatically available at the following URLs:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## Makefile Commands

A Makefile is provided for convenience. Run `make help` to see all available commands.

### Docker Environment

- **make up**: Starts all services (app & db containers) in the background.
- **make down**: Stops services but **keeps the database data**.
- **make build**: Rebuilds the docker images if you change the code or dependencies.
- **make logs**: Follows the logs from the application container.
- **make cli**: Gets an interactive shell (bash) inside the application container.

### Database Management

- **make db-init**: (Re)Initializes the database schema. It will drop all existing tables before creating them again.
- **make db-reset**: Resets the entire database. It stops the services, **deletes all data permanently**, and restarts the services.

### Application Tasks

- **make scrape year=[YEAR]**: Runs the scraper for the specified year.
- **make run-api**: Starts the FastAPI server with live reloading on localhost:8000.
- **make db-test**: Runs a simple test to verify the database connection.
# ProCyclingStats Scraper & Analyzer

This project is a Python application designed to scrape race data from `procyclingstats.com` and provide an API for data analysis. It is built following Domain-Driven Design (DDD) principles and runs entirely on Docker.

## 🚀 Quickstart: Full Workflow Example

This example shows the end-to-end process: from a clean slate to getting a rider analysis via the API.

### Prerequisites

- Docker & Docker Compose
- `make` (usually pre-installed on Linux/WSL)

### 1. Setup Environment

First, create your local configuration file from the provided template.

```bash
cp .env.example .env
```

### 2. Reset and Initialize the Database

To start from a completely clean state, this command will stop any running services, **delete all existing data**, and restart the services with a fresh, empty database.

```bash
make db-reset
```

Now, create the necessary tables in the new database.

```bash
make db-init
```

### 3. Populate the Database with Data

Run the scraper for a specific year to collect race and rider data. This process can take several minutes.

```bash
make scrape year=2023
```

### 4. Start the API Server

In a **separate terminal window**, start the FastAPI server. Leave this terminal running.

```bash
make run-api
```

### 5. Get a Rider Analysis

In **another terminal window**, send a POST request to the analysis endpoint with the cyclists you want to evaluate.

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

The API will return a JSON response with the matched riders from your database.

## API Documentation

Once the API server is running (`make run-api`), the interactive documentation is automatically available at the following URLs:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## Makefile Commands

A Makefile is provided for convenience. Run `make help` to see all available commands.

### Docker Environment

- **make up**: Starts all services (app & db containers) in the background.
- **make down**: Stops services but **keeps the database data**.
- **make build**: Rebuilds the docker images if you change the code or dependencies.
- **make logs**: Follows the logs from the application container.
- **make cli**: Gets an interactive shell (bash) inside the application container.

### Database Management

- **make db-init**: (Re)Initializes the database schema. It will drop all existing tables before creating them again.
- **make db-reset**: Resets the entire database. It stops the services, **deletes all data permanently**, and restarts the services.

### Application Tasks

- **make scrape year=[YEAR]**: Runs the scraper for the specified year.
- **make run-api**: Starts the FastAPI server with live reloading on localhost:8000.
- **make db-test**: Runs a simple test to verify the database connection.