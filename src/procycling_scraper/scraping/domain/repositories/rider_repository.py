from abc import ABC, abstractmethod
from typing import Optional

from procycling_scraper.scraping.domain.entities.rider import Rider


class RiderRepository(ABC):
    """
    Abstract interface for a Rider repository.
    Defines the contract for persisting and retrieving Rider entities.
    """

    @abstractmethod
    def save(self, rider: Rider) -> None:
        """
        Saves a Rider entity. This can be either a new rider (insert)
        or an existing one (update).
        """
        pass

    @abstractmethod
    def find_by_pcs_id(self, pcs_id: str) -> Optional[Rider]:
        """
        Finds a Rider entity by its ProCyclingStats ID.

        Returns:
            An optional Rider, which will be None if no rider is found.
        """
        pass
