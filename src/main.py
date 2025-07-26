from contextlib import redirect_stdout
from sqlalchemy import MetaData
from typing import Optional

import typer

from procycling_scraper.scraping.application.scrape_year_use_case import ScrapeYearUseCase
from procycling_scraper.scraping.domain.entities.race import Race
from procycling_scraper.scraping.domain.entities.rider import Rider
from procycling_scraper.scraping.domain.repositories.race_repository import RaceRepository
from procycling_scraper.scraping.domain.repositories.rider_repository import RiderRepository
from procycling_scraper.scraping.infrastructure.repositories.postgres_rider_repository import PostgresRiderRepository
from procycling_scraper.scraping.infrastructure.scrapers.procyclingstats_race_data_scraper import ProCyclingStatsRaceDataScraper
from procycling_scraper.scraping.infrastructure.scrapers.procyclingstats_race_list_scraper import ProCyclingStatsRaceListScraper
from procycling_scraper.scraping.infrastructure.database.schema import engine, metadata


class FakeRaceRepository(RaceRepository):
    def save(self, race: Race) -> None:
        print(f"    [DB-Race-Fake] 'Saving' race: {race.name}")
        for classification in race.classifications:
            print(
                f"      -> with classification '{classification.classification_type.value}' containing {len(classification.results)} results.")

    def find_by_pcs_id(self, pcs_id: str): return None


app = typer.Typer(
    help="ProCyclingStats Scraper CLI - A tool to scrape cycling data."
)


@app.command()
def scrape_year(
    year: int = typer.Argument(..., help="The year to scrape data for."),

    output_file: Optional[str] = typer.Option(
        None, "--output-file", "-o", help="Redirect output to a file."
    )
):
    """
    Scrapes all race data for a specific YEAR and 'saves' it.
    """
    typer.echo(f"Initializing scraping process for the year {year}...")

    if output_file:
        typer.echo(f"Output will be redirected to: {output_file}")
        with open(output_file, 'w', encoding='utf-8') as f:
            with redirect_stdout(f):
                _run_use_case(year)
    else:
        _run_use_case(year)

    typer.echo(f"Process for year {year} finished.")


def _run_use_case(year: int):
    race_list_scraper = ProCyclingStatsRaceListScraper()
    race_data_scraper = ProCyclingStatsRaceDataScraper()
    rider_repo = PostgresRiderRepository(engine=engine)
    race_repo = FakeRaceRepository()

    use_case = ScrapeYearUseCase(
        race_list_scraper=race_list_scraper,
        race_data_scraper=race_data_scraper,
        race_repository=race_repo,
        rider_repository=rider_repo,
    )
    use_case.execute(year)


@app.command()
def db_init():
    """Initializes the database by creating all tables."""
    typer.echo("Initializing database and creating tables...")
    metadata.create_all(engine)
    typer.echo("Database initialized successfully.")


if __name__ == "__main__":
    app()
