from dataclasses import dataclass


@dataclass(frozen=True)
class ResultLine:
    """
    Represents a single, point-scoring result in a race classification.

    This is a Value Object because its identity is defined by its attributes,
    and it is meaningless without the context of its parent Classification.
    It is immutable.

    An instance of this class is only created if uci_points > 0.

    Attributes:
        rider_pcs_id (str): The pcs_id of the rider, linking to the Rider entity.
        team_name (str): The name of the team the rider raced for in this event.
        uci_points (int): The number of UCI points awarded. Must be > 0.
    """
    rider_pcs_id: str
    team_name: str
    uci_points: int
