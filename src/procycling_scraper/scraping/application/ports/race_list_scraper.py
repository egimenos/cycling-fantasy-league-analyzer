from abc import ABC, abstractmethod
from typing import List, Tuple

from procycling_scraper.scraping.domain.entities.race import RaceType


class RaceListScraper(ABC):
    """
    Interface for a service that scrapes the list of races for a season.
    """

    @abstractmethod
    def scrape(self, year: int) -> List[Tuple[str, RaceType]]:
        """
        Scrapes and returns a list of tuples, where each tuple contains:
        - The base URL of the race (e.g., "race/tour-de-france/2024").
        - The type of the race (RaceType.ONE_DAY or RaceType.STAGE_RACE).
        """
        pass
