from typing import List, Dict, Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.engine import Engine

from procycling_scraper.analysis.application.dto.analysis_dtos import RiderResultDTO
from procycling_scraper.scraping.domain.entities.rider import Rider
from procycling_scraper.scraping.domain.repositories.rider_repository import RiderRepository
from procycling_scraper.scraping.infrastructure.database.schema import (
    classifications_table, pcs_points_results_table, races_table, riders_table
)

class PostgresRiderRepository(RiderRepository):
    def __init__(self, engine: Engine):
        self._engine = engine

    def save(self, rider: Rider) -> None:
        stmt = insert(riders_table).values(pcs_id=rider.pcs_id, name=rider.name)
        stmt = stmt.on_conflict_do_nothing(index_elements=['pcs_id'])
        with self._engine.connect() as conn:
            conn.execute(stmt)

    def find_all(self) -> List[Rider]:
        stmt = select(riders_table)
        with self._engine.connect() as conn:
            results: List[Any] = list(conn.execute(stmt).fetchall())
        
        riders: List[Rider] = []
        for row in results:
            if not getattr(row, 'pcs_id', None) or not getattr(row, 'name', None):
                continue
            riders.append(Rider(pcs_id=row.pcs_id, name=row.name, id=row.id))
        return riders

    def find_all_results_by_rider_ids(self, rider_ids: List[UUID]) -> Dict[UUID, List[RiderResultDTO]]:
        if not rider_ids:
            return {}

        stmt = select(
            pcs_points_results_table.c.rider_id,
            pcs_points_results_table.c.points,
            races_table.c.year,
            races_table.c.type.label("race_type")
        ).select_from(
            pcs_points_results_table
        ).join(
            classifications_table,
            pcs_points_results_table.c.classification_id == classifications_table.c.id
        ).join(
            races_table,
            classifications_table.c.race_id == races_table.c.id
        ).where(pcs_points_results_table.c.rider_id.in_(rider_ids))

        with self._engine.connect() as conn:
            db_results: List[Any] = list(conn.execute(stmt).fetchall())

        grouped_results: Dict[UUID, List[RiderResultDTO]] = {rider_id: [] for rider_id in rider_ids}
        for row in db_results:
            result = RiderResultDTO(
                rider_id=row.rider_id,
                points=row.points,
                year=row.year,
                race_type=row.race_type 
            )
            grouped_results[row.rider_id].append(result)
            
        return grouped_results

    def find_by_pcs_id(self, pcs_id: str):
        pass