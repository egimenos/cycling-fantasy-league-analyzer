from typing import List, Union, Dict
from procycling_scraper.analysis.application.dto.cyclist_dto import CyclistDTO

class ProcessCyclistsUseCase:
    def execute(self, cyclists: List[CyclistDTO]) -> Dict[str, Union[str, int]]:
        print("--- Use Case 'ProcessCyclistsUseCase' Executed ---")
        print(f"Received {len(cyclists)} cyclists to process.")
        for cyclist in cyclists:
            print(f"  -> Name: {cyclist.name}, Team: {cyclist.team}, Price: {cyclist.price}")
        
        # En el futuro, aquí iría la lógica de análisis.
        # Por ahora, devolvemos una simple confirmación.
        return {"status": "success", "processed_cyclists": len(cyclists)}