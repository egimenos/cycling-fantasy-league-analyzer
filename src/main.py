import logging
from contextlib import redirect_stdout
from typing import Optional

import typer

from procycling_scraper.scraping.application.scrape_year_use_case import (
    ScrapeYearUseCase,
)
from procycling_scraper.scraping.infrastructure.database.schema import engine, metadata
from procycling_scraper.scraping.infrastructure.repositories.postgres_race_repository import (
    PostgresRaceRepository,
)
from procycling_scraper.scraping.infrastructure.repositories.postgres_rider_repository import (
    PostgresRiderRepository,
)
from procycling_scraper.scraping.infrastructure.scrapers.procyclingstats_race_data_scraper import (
    ProCyclingStatsRaceDataScraper,
)
from procycling_scraper.scraping.infrastructure.scrapers.procyclingstats_race_list_scraper import (
    ProCyclingStatsRaceListScraper,
)
from procycling_scraper.shared.logging_config import setup_logging

app = typer.Typer(help="ProCyclingStats Scraper CLI - A tool to scrape cycling data.")

setup_logging()

logger = logging.getLogger(__name__)


@app.command()
def scrape_year(
    year: int = typer.Argument(None, help="The year to scrape data for."),
    output_file: Optional[str] = typer.Option(
        None, "--output-file", "-o", help="Redirect output to a file."
    ),
):
    """
    Scrapes all race data for a specific YEAR and saves it to the database.
    """
    typer.echo(f"Initializing scraping process for the year {year}...")

    if output_file:
        typer.echo(f"Output will be redirected to: {output_file}")
        with open(output_file, "w", encoding="utf-8") as f:
            with redirect_stdout(f):
                _run_use_case(year)
    else:
        _run_use_case(year)

    typer.echo(f"Process for year {year} finished.")


def _run_use_case(year: int):
    """
    Sets up the application's dependencies (Composition Root) and runs the use case.
    """
    race_list_scraper = ProCyclingStatsRaceListScraper()
    race_data_scraper = ProCyclingStatsRaceDataScraper()

    rider_repo = PostgresRiderRepository(engine=engine)
    race_repo = PostgresRaceRepository(engine=engine)

    use_case = ScrapeYearUseCase(
        race_list_scraper=race_list_scraper,
        race_data_scraper=race_data_scraper,
        race_repository=race_repo,
        rider_repository=rider_repo,
    )

    use_case.execute(year)


@app.command()
def db_init():
    """
    (Re)Initializes the database by dropping and creating all tables.
    """
    typer.echo("Dropping all existing tables from the database...")
    metadata.drop_all(engine, checkfirst=True)

    typer.echo("Creating all tables...")
    metadata.create_all(engine)
    typer.echo("Database initialized successfully.")


if __name__ == "__main__":
    # Example: demonstrate loading DB engine and starting API
    logger.info("Database engine created: %s", engine)
    # To run API via uvicorn use Makefile target `make run-api`
    logger.info(
        "Start API with: make run-api (maps http://localhost:8001 to container 8000)"
    )
    app()
