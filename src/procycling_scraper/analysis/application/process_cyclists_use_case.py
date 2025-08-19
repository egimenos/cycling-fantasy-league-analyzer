from typing import List, Union, Dict, Any
from uuid import UUID

from procycling_scraper.analysis.application.dto.cyclist_dto import AnalysisRequestDTO
from procycling_scraper.analysis.application.dto.analysis_dtos import MatchedRiderDTO
from procycling_scraper.scraping.domain.entities.race import RaceType
from procycling_scraper.scraping.domain.repositories.rider_repository import RiderRepository
from procycling_scraper.analysis.domain.rider_matching_service import RiderMatchingService
from procycling_scraper.analysis.domain.value_score_calculator import ValueScoreCalculator

AnalyzedCyclistPayload = Dict[str, Any]
ApiResponsePayload = Dict[str, Union[str, List[AnalyzedCyclistPayload]]]

class ProcessCyclistsUseCase:
    def __init__(self, rider_repository: RiderRepository):
        self._rider_repository = rider_repository
        self._score_calculator = ValueScoreCalculator()

    def execute(self, request_data: AnalysisRequestDTO) -> ApiResponsePayload:
        all_riders_from_db = self._rider_repository.find_all()
        matching_service = RiderMatchingService(all_riders_from_db)
        
        target_race_type = RaceType.ONE_DAY if request_data.race_type.value == "one-day" else RaceType.STAGE_RACE

        matched_riders: List[MatchedRiderDTO] = []
        for cyclist_dto in request_data.cyclists:
            best_match = matching_service.find_best_match(cyclist_dto.name)
            if best_match and best_match.id:
                matched_riders.append(MatchedRiderDTO(api_data=cyclist_dto, db_rider=best_match))
        
        rider_ids_to_fetch: List[UUID] = [rider.db_rider.id for rider in matched_riders if rider.db_rider.id is not None]
        all_results_map = self._rider_repository.find_all_results_by_rider_ids(rider_ids_to_fetch)
        
        analyzed_cyclists: List[AnalyzedCyclistPayload] = []
        for rider_data in matched_riders:
            db_rider = rider_data.db_rider
            api_data = rider_data.api_data
            
            if db_rider.id:
                rider_results = all_results_map.get(db_rider.id, [])
                
                one_day_points = sum(r.points for r in rider_results if r.race_type == RaceType.ONE_DAY)
                stage_race_points = sum(r.points for r in rider_results if r.race_type == RaceType.STAGE_RACE)
                
                total_points, value_score = self._score_calculator.calculate(
                    rider_results, api_data.price, target_race_type
                )

                print("\n--- DEBUGGING RIDER ---")
                print(f"Name: {api_data.name}")
                print(f"Target Analysis Type: {target_race_type.value}")
                print(f"Raw Points Found (DB): One-Day -> {one_day_points}, Stage-Race -> {stage_race_points}")
                print(f"Total Weighted Points Calculated: {round(total_points, 2)}")
                print(f"Price: {api_data.price}")
                print(f"Final Value Score: {round(value_score, 2)}")

                analyzed_cyclists.append({
                    "name": api_data.name,
                    "price": api_data.price,
                    "pcs_url": f"https://www.procyclingstats.com/{db_rider.pcs_id}",
                    "total_weighted_points": round(total_points, 2),
                    "value_score": round(value_score, 2),
                    "raw_points_breakdown": {
                        "one_day": one_day_points,
                        "stage_race": stage_race_points
                    }
                })

        analyzed_cyclists.sort(key=lambda x: x['value_score'], reverse=True)

        return {"status": "success", "analyzed_cyclists": analyzed_cyclists}