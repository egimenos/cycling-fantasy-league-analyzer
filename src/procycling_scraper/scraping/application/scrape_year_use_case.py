from procycling_scraper.scraping.application.dto.scraped_race_data import ScrapedRaceData  # Import the DTO
from procycling_scraper.scraping.application.ports.race_data_scraper import RaceDataScraper
from procycling_scraper.scraping.application.ports.race_list_scraper import RaceListScraper
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
        Args:
            year: The year to scrape.
        """
        print(f"Executing use case: Scrape and Persist for year {year}...")

        race_urls = self._race_list_scraper.scrape(year)
        print(f"Found {len(race_urls)} races to scrape.")

        for url in race_urls:
            try:
                print(f"Scraping race from URL: {url}")

                scraped_data: ScrapedRaceData = self._race_data_scraper.scrape(
                    url)

                for rider in scraped_data.riders:
                    self._rider_repository.save(rider)

                self._race_repository.save(scraped_data.race)

                print(
                    f"Successfully scraped and saved race: {scraped_data.race.name}")

            except Exception as e:
                print(f"ERROR: Failed to process race from {url}. Reason: {e}")

        print(f"Finished use case for year {year}.")
