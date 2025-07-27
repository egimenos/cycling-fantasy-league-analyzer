from dataclasses import dataclass


@dataclass(frozen=True)
class ResultLine:
    """
    Represents a single, point-scoring result in a race classification.
    """
    rider_pcs_id: str
    team_name: str
    points: int
