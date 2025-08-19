from typing import List, Tuple
from datetime import datetime
from procycling_scraper.analysis.application.dto.analysis_dtos import RiderResultDTO

class ValueScoreCalculator:
    # --- LA CORRECCIÓN ESTÁ AQUÍ ---
    # Especificamos los tipos DENTRO de la tupla
    def calculate(self, results: List[RiderResultDTO], price: int) -> Tuple[float, float]:
        """
        Calculates the weighted total points and the value score for a rider.
        Returns a tuple of (total_weighted_points, value_score).
        """
        current_year = datetime.now().year
        total_weighted_points = 0.0

        for result in results:
            year_diff = current_year - result.year
            
            weight = 1.0
            if year_diff == 1:
                weight = 0.75
            elif year_diff == 2:
                weight = 0.50
            elif year_diff > 2:
                weight = 0.25
            
            total_weighted_points += result.points * weight

        value_score = (total_weighted_points / price) if price > 0 else 0.0
        
        return total_weighted_points, value_score