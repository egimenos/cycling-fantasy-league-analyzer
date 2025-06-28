import enum
from dataclasses import dataclass, field
from typing import List

from procycling_scraper.scraping.domain.entities.classification import Classification


class RaceType(enum.Enum):
    """
    An enumeration to represent the type of a race.
    """
    ONE_DAY = "One-Day"
    STAGE_RACE = "Stage-Race"


@dataclass(frozen=False)
class Race:
    """
    Represents a single Race event.

    This is the Aggregate Root for our scraping domain. It is identified by its
    unique ProCyclingStats ID. We set frozen=False because an aggregate root
    is a consistency boundary and needs to manage its internal state, such as
    adding child entities like Classifications after it has been created.

    Attributes:
        pcs_id (str): The unique identifier from ProCyclingStats.
        name (str): The name of the race.
        year (int): The year the race took place.
        race_type (RaceType): The type of the race.
        classifications (List[Classification]): A list of classifications for this race.
    """
    pcs_id: str
    name: str
    year: int
    race_type: RaceType
    classifications: List[Classification] = field(default_factory=list)

    def add_classification(self, classification: Classification):
        self.classifications.append(classification)
