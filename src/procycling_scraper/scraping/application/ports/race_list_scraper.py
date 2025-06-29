from abc import ABC, abstractmethod
from typing import List


class RaceListScraper(ABC):
    """
    Interface for a service that scrapes the list of race URLs for a season.
    """
    @abstractmethod
    def scrape(self, year: int) -> List[str]:
        """Scrapes and returns a list of race URLs."""
        pass
