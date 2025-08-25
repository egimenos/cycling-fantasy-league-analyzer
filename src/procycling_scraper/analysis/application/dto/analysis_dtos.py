from dataclasses import dataclass
from typing import List

from procycling_scraper.analysis.application.dto.cyclist_dto import CyclistDTO
from procycling_scraper.scraping.domain.entities.rider import Rider


@dataclass(frozen=True)
class RiderResultDTO:
    rider_id: str
    points: int
    year: int
    race_type: str


@dataclass(frozen=True)
class CyclistAnalysisDTO:
    name: str
    team: str
    price: int
    matched_rider_id: str
    value_score: float
    results: List[RiderResultDTO]


class MatchedRiderDTO:
    """
    Intern DTO to carry API and DB rider data.
    """

    def __init__(self, api_data: CyclistDTO, db_rider: Rider):
        self.api_data = api_data
        self.db_rider = db_rider
