
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.engine import Engine

from procycling_scraper.scraping.domain.entities.rider import Rider
from procycling_scraper.scraping.domain.repositories.rider_repository import RiderRepository
from procycling_scraper.scraping.infrastructure.database.schema import riders_table


class PostgresRiderRepository(RiderRepository):
    def __init__(self, engine: Engine):
        self._engine = engine

    def save(self, rider: Rider) -> None:
        """Saves a rider, ignoring duplicates based on pcs_id."""
        stmt = insert(riders_table).values(
            pcs_id=rider.pcs_id,
            name=rider.name
        )
        stmt = stmt.on_conflict_do_nothing(index_elements=['pcs_id'])

        with self._engine.connect() as conn:
            conn.execute(stmt)

    def find_by_pcs_id(self, pcs_id: str):
        pass
