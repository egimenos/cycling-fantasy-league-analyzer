from abc import ABC, abstractmethod
from typing import Optional

from procycling_scraper.scraping.domain.entities.race import Race


class RaceRepository(ABC):
    """
    Abstract interface for a Race repository.
    Defines the contract for persisting and retrieving Race aggregates.
    """

    @abstractmethod
    def save(self, race: Race) -> None:
        """
        Saves the entire Race aggregate, including all its Classifications
        and ResultLines. This handles both new and existing races.
        """
        pass

    @abstractmethod
    def find_by_pcs_id(self, pcs_id: str) -> Optional[Race]:
        """
        Finds a Race aggregate by its ProCyclingStats ID.

        The returned Race object should be fully constituted, containing all
        of its associated Classification and ResultLine objects.

        Returns:
            An optional Race, which will be None if no race is found.
        """
        pass
