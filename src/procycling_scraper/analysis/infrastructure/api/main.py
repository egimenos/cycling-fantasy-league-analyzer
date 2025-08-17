from typing import List
from fastapi import FastAPI
from procycling_scraper.analysis.application.dto.cyclist_dto import CyclistDTO
from procycling_scraper.analysis.application.process_cyclists_use_case import ProcessCyclistsUseCase

app = FastAPI(
    title="ProCycling Scraper & Analyzer API",
    description="API for processing and analyzing cyclist data.",
    version="0.1.0",
)

# --- Endpoint POST ---
@app.post("/v1/cyclists/process", status_code=200)
def process_cyclists(cyclists_data: List[CyclistDTO]):
    """
    Receives a list of cyclists with their prices, validates them,
    and forwards them for processing.
    """
    use_case = ProcessCyclistsUseCase()
    result = use_case.execute(cyclists=cyclists_data)
    return result