import enum
from dataclasses import dataclass, field
from typing import Optional, List

from procycling_scraper.scraping.domain.value_objects.result_line import ResultLine


class ClassificationType(enum.Enum):
    """Enumeration for the different types of race classifications."""
    GENERAL = "General"
    STAGE = "Stage"
    POINTS = "Points"  # Green Jersey
    KOM = "KOM"        # King of the Mountain


@dataclass(frozen=True)
class Classification:
    """
    Represents a specific classification within a race (e.g., General, Stage 5).

    This is a child Entity within the Race Aggregate. It is identified locally
    by its type and optional stage number. It is created as a frozen object
    because once scraped, a classification's definition and results are final.

    Attributes:
        classification_type (ClassificationType): The type of this classification.
        results (List[ResultLine]): The list of point-scoring results.
        stage_number (Optional[int]): The stage number, if type is STAGE.
    """
    classification_type: ClassificationType
    results: List[ResultLine]
    stage_number: Optional[int] = None
