from typing import List
from pydantic import BaseModel, Field
from enum import Enum

class AnalysisRaceType(str, Enum):
    one_day = "one-day"
    stage_race = "stage-race"

class CyclistDTO(BaseModel):
    name: str
    team: str
    price: int = Field(gt=0)
    
class AnalysisRequestDTO(BaseModel):
    race_type: AnalysisRaceType
    cyclists: List[CyclistDTO]