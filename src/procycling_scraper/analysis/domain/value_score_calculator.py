from typing import List, Tuple
from datetime import datetime
from procycling_scraper.analysis.application.dto.analysis_dtos import RiderResultDTO
from procycling_scraper.scraping.domain.entities.race import RaceType

class ValueScoreCalculator:
    def calculate(self, results: List[RiderResultDTO], price: int, target_race_type: RaceType) -> Tuple[float, float]:
        """
        Calculates the weighted total points and the value score for a rider.
        """
        current_year = datetime.now().year
        total_weighted_points = 0.0

        for result in results:
            year_diff = current_year - result.year
            
            year_weight = 1.0
            if year_diff == 1:
                year_weight = 0.5
            elif year_diff == 2:
                year_weight = 0.25
            elif year_diff > 2:
                year_weight = 0.1
            
            type_weight = 1.0 if result.race_type == target_race_type else 0.5
            
            final_weight = year_weight * type_weight
            
            total_weighted_points += result.points * final_weight

        value_score = (total_weighted_points / price) if price > 0 else 0.0
        
        return total_weighted_points, value_score