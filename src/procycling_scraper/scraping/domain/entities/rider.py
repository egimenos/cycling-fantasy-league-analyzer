from dataclasses import dataclass, field
from typing import Optional
from uuid import UUID

@dataclass
class Rider:
    """
    Represents a unique cyclist.

    This is an Entity identified by its ProCyclingStats ID (pcs_id), which serves
    as a Natural Key from the source system.

    Attributes:
        pcs_id (str): The unique identifier for the rider from ProCyclingStats,
        e.g., "tadej-pogacar".
        name (str): The full name of the rider.
        id (Optional[UUID]): The unique identifier for the rider in the local
    """
    pcs_id: str
    name: str
    id: Optional[UUID] = field(default=None)