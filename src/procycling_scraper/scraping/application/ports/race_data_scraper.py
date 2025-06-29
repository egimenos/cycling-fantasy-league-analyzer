from abc import ABC, abstractmethod
from typing import Tuple, List

from procycling_scraper.scraping.domain.entities.race import Race
from procycling_scraper.scraping.domain.entities.rider import Rider


class RaceDataScraper(ABC):
    """

    Interface for a service that scrapes all data from a single race URL.
    """
    @abstractmethod
    def scrape(self, race_url: str) -> Tuple[Race, List[Rider]]:
        """
        Scrapes a race URL and returns a tuple containing:
        - The fully constituted Race aggregate.
        - A list of all unique Rider entities found.
        """
        pass
