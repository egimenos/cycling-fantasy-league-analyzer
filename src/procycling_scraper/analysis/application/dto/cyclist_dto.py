from pydantic import BaseModel, Field

class CyclistDTO(BaseModel):
    """
    Data Transfer Object for a cyclist's data received via API.
    Pydantic handles the validation automatically.
    """
    name: str
    team: str
    price: int = Field(gt=0)