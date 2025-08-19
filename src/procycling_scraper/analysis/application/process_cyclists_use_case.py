from typing import List, Union, Dict, Any
from uuid import UUID

from procycling_scraper.analysis.application.dto.cyclist_dto import CyclistDTO
from procycling_scraper.analysis.application.dto.analysis_dtos import MatchedRiderDTO
from procycling_scraper.scraping.domain.repositories.rider_repository import RiderRepository
from procycling_scraper.analysis.domain.rider_matching_service import RiderMatchingService
from procycling_scraper.analysis.domain.value_score_calculator import ValueScoreCalculator

AnalyzedCyclistPayload = Dict[str, Any]
ApiResponsePayload = Dict[str, Union[str, List[AnalyzedCyclistPayload]]]

class ProcessCyclistsUseCase:
    def __init__(self, rider_repository: RiderRepository):
        self._rider_repository = rider_repository
        self._score_calculator = ValueScoreCalculator()

    def execute(self, cyclists: List[CyclistDTO]) -> ApiResponsePayload:
        all_riders_from_db = self._rider_repository.find_all()
        matching_service = RiderMatchingService(all_riders_from_db)
        
        matched_riders: List[MatchedRiderDTO] = []
        for cyclist_dto in cyclists:
            best_match = matching_service.find_best_match(cyclist_dto.name)
            if best_match and best_match.id:
                matched_riders.append(MatchedRiderDTO(api_data=cyclist_dto, db_rider=best_match))
            else:
                 print(f"  -> NO MATCH: Could not find a rider in DB for API name '{cyclist_dto.name}'")
        
        rider_ids_to_fetch: List[UUID] = [rider.db_rider.id for rider in matched_riders if rider.db_rider.id is not None]
        
        all_results_map = self._rider_repository.find_all_results_by_rider_ids(rider_ids_to_fetch)
        
        analyzed_cyclists: List[AnalyzedCyclistPayload] = []
        for rider_data in matched_riders:
            db_rider = rider_data.db_rider
            api_data = rider_data.api_data
            
            if db_rider.id:
                rider_results = all_results_map.get(db_rider.id, [])
                total_points, value_score = self._score_calculator.calculate(rider_results, api_data.price)

                analyzed_cyclists.append({
                    "name": api_data.name,
                    "price": api_data.price,
                    "pcs_url": f"https://www.procyclingstats.com/{db_rider.pcs_id}",
                    "total_weighted_points": round(total_points, 2),
                    "value_score": round(value_score, 2)
                })

        analyzed_cyclists.sort(key=lambda x: x['value_score'], reverse=True)

        return {"status": "success", "analyzed_cyclists": analyzed_cyclists}