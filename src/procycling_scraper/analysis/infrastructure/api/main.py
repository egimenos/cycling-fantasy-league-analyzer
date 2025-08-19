from typing import List, Any, Dict
from fastapi import FastAPI
from procycling_scraper.analysis.application.dto.cyclist_dto import CyclistDTO
from procycling_scraper.analysis.application.process_cyclists_use_case import ProcessCyclistsUseCase

from procycling_scraper.scraping.infrastructure.database.schema import engine
from procycling_scraper.scraping.infrastructure.repositories.postgres_rider_repository import PostgresRiderRepository

app = FastAPI(
    title="ProCycling Scraper & Analyzer API",
    description="API for processing and analyzing cyclist data.",
    version="0.1.0",
)

@app.post("/v1/cyclists/process", status_code=200)
def process_cyclists(cyclists_data: List[CyclistDTO]) -> Dict[str, Any]:
    """
    Receives a list of cyclists with prices, matches them against the database,
    calculates their value score based on past results, and returns the analysis.
    """
    rider_repo = PostgresRiderRepository(engine=engine)
    
    use_case = ProcessCyclistsUseCase(rider_repository=rider_repo)
    
    result = use_case.execute(cyclists=cyclists_data)
    return result