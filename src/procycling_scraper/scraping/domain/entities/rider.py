from dataclasses import dataclass


@dataclass(frozen=True)
class Rider:
    """
    Represents a unique cyclist.

    This is an Entity identified by its ProCyclingStats ID (pcs_id), which serves
    as a Natural Key from the source system.

    Attributes:
        pcs_id (str): The unique identifier for the rider from ProCyclingStats,
        e.g., "tadej-pogacar".
        name (str): The full name of the rider.
    """
    pcs_id: str
    name: str
