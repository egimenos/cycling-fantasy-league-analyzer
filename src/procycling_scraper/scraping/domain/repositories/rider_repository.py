from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from uuid import UUID

from procycling_scraper.analysis.application.dto.analysis_dtos import RiderResultDTO
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

    @abstractmethod
    def find_all(self) -> "List[Rider]":
        """Fetches all riders from the database."""
        pass

    @abstractmethod
    def find_all_results_by_rider_ids(
        self, rider_ids: List[UUID]
    ) -> Dict[UUID, List[RiderResultDTO]]:
        """
        Fetches all point-scoring results for a given list of rider database IDs.
        Returns a dictionary mapping each rider_id to a list of their results.
        """
        pass
