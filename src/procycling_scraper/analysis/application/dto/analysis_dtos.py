from uuid import UUID
from procycling_scraper.analysis.application.dto.cyclist_dto import CyclistDTO
from procycling_scraper.scraping.domain.entities.rider import Rider

class RiderResultDTO:
    """
    DTO to carry a rider's result from persistence to the application layer.
    """
    def __init__(self, rider_id: UUID, points: int, year: int):
        self.rider_id = rider_id
        self.points = points
        self.year = year

class MatchedRiderDTO:
    """
    Intern DTO to carry API and DB rider data.
    """
    def __init__(self, api_data: CyclistDTO, db_rider: Rider):
        self.api_data = api_data
        self.db_rider = db_rider