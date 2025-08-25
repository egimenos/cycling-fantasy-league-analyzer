import logging
from typing import Tuple

from procycling_scraper.scraping.application.dto.scraped_race_data import ScrapedRaceData
from procycling_scraper.scraping.application.ports.race_data_scraper import RaceDataScraper
from procycling_scraper.scraping.application.ports.race_list_scraper import RaceListScraper
from procycling_scraper.scraping.domain.entities.race import RaceType
from procycling_scraper.scraping.domain.repositories.race_repository import RaceRepository
from procycling_scraper.scraping.domain.repositories.rider_repository import RiderRepository

log = logging.getLogger(__name__)


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
        log.info(f"Executing use case: Scrape and Persist for year {year}...")

        races_info: list[Tuple[str, RaceType]
                         ] = self._race_list_scraper.scrape(year)
        log.info(f"Found {len(races_info)} races to scrape.")

        for race_info in races_info:
            try:
                log.info(
                    "Processing race info",
                    extra={"race_url": race_info[0],
                           "race_type": race_info[1].value}
                )

                scraped_data: ScrapedRaceData = self._race_data_scraper.scrape(
                    race_info)

                if "Scraping Failed" in scraped_data.race.name:
                    continue

                log.info(
                    f"  -> Found {len(scraped_data.riders)} riders with points in this race. Saving to DB...")
                for rider in scraped_data.riders:
                    self._rider_repository.save(rider)

                self._race_repository.save(scraped_data.race)

                log.info(f"Successfully processed race", extra={
                         "race_url": race_info[0], "race_type": race_info[1].value})

            except Exception as e:
                log.exception(
                    "Failed to process race",
                    extra={"race_url": race_info[0], "error": str(e)}
                )

        log.info(f"Finished use case for year {year}.")
