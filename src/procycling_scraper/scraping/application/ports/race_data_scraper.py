from abc import ABC, abstractmethod
from typing import Tuple

from procycling_scraper.scraping.application.dto.scraped_race_data import (
    ScrapedRaceData,
)
from procycling_scraper.scraping.domain.entities.race import RaceType


class RaceDataScraper(ABC):
    """
    Interface for a service that scrapes all data from a single race URL.
    """

    @abstractmethod
    def scrape(self, race_info: Tuple[str, RaceType]) -> ScrapedRaceData:
        """
        Scrapes a race URL and returns a ScrapedRaceData DTO containing:
        - The fully constituted Race aggregate.
        - A list of all unique Rider entities found.
        """
        pass
