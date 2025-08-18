from typing import List, Union, Dict
from procycling_scraper.analysis.application.dto.cyclist_dto import CyclistDTO
from procycling_scraper.scraping.domain.repositories.rider_repository import RiderRepository
from procycling_scraper.analysis.domain.rider_matching_service import RiderMatchingService

FoundCyclistPayload = Dict[str, Union[str, int]]
ApiResponsePayload = Dict[str, Union[str, int, List[FoundCyclistPayload]]]

class ProcessCyclistsUseCase:
    def __init__(self, rider_repository: RiderRepository):
        self._rider_repository = rider_repository

    def execute(self, cyclists: List[CyclistDTO]) -> ApiResponsePayload:
        print("--- Use Case 'ProcessCyclistsUseCase' Executed ---")
        
        all_riders_from_db = self._rider_repository.find_all()
        print(f"Loaded {len(all_riders_from_db)} riders from DB to perform matching.")
        
        matching_service = RiderMatchingService(all_riders_from_db)

        found_cyclists: List[FoundCyclistPayload] = []
        for cyclist_dto in cyclists:
            best_match = matching_service.find_best_match(cyclist_dto.name)
            
            if best_match:
                print(f"  -> MATCH FOUND: API name '{cyclist_dto.name}' matches DB rider '{best_match.name}'")
                found_cyclists.append({
                    "api_name": cyclist_dto.name,
                    "db_name": best_match.name,
                    "price": cyclist_dto.price,
                    "pcs_id": best_match.pcs_id
                })
            else:
                print(f"  -> NO MATCH: Could not find a rider in DB for API name '{cyclist_dto.name}'")

        return {
            "status": "success",
            "processed_cyclists": len(cyclists),
            "found_cyclists": found_cyclists
        }