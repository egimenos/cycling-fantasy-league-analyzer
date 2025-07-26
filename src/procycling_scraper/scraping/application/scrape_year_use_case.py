from typing import Tuple

from procycling_scraper.scraping.application.dto.scraped_race_data import ScrapedRaceData
from procycling_scraper.scraping.application.ports.race_data_scraper import RaceDataScraper
from procycling_scraper.scraping.application.ports.race_list_scraper import RaceListScraper
from procycling_scraper.scraping.domain.entities.race import RaceType
from procycling_scraper.scraping.domain.repositories.race_repository import RaceRepository
from procycling_scraper.scraping.domain.repositories.rider_repository import RiderRepository


class ScrapeYearUseCase:
    """
    This class represents the "Scrape and Persist Race Data for a Year" use case.
    """

    def __init__(
        self,
        race_list_scraper: RaceListScraper,
        race_data_scraper: RaceDataScraper,
        race_repository: RaceRepository,
        rider_repository: RiderRepository,
    ):
        self._race_list_scraper = race_list_scraper
        self._race_data_scraper = race_data_scraper
        self._race_repository = race_repository
        self._rider_repository = rider_repository

    def execute(self, year: int) -> None:
        """
        Executes the primary use case: scrape all race data for a given year.
        """
        print(f"Executing use case: Scrape and Persist for year {year}...")

        races_info: list[Tuple[str, RaceType]
                         ] = self._race_list_scraper.scrape(year)
        print(f"Found {len(races_info)} races to scrape.")

        for race_info in races_info:
            try:
                print(f"Processing race info: {race_info}")

                scraped_data: ScrapedRaceData = self._race_data_scraper.scrape(
                    race_info)

                if "Scraping Failed" in scraped_data.race.name:
                    continue

                print(
                    f"  -> Found {len(scraped_data.riders)} riders with points in this race. Saving to DB...")
                for rider in scraped_data.riders:
                    self._rider_repository.save(rider)

                self._race_repository.save(scraped_data.race)

                print(f"Successfully processed race: {scraped_data.race.name}")

            except Exception as e:
                print(
                    f"ERROR: Failed to process race from {race_info[0]}. Reason: {e}")

        print(f"Finished use case for year {year}.")
