from typing import Dict, List, Any, Union
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.engine import Engine, Connection

from procycling_scraper.scraping.domain.entities.race import Race
from procycling_scraper.scraping.domain.entities.classification import Classification
from procycling_scraper.scraping.domain.value_objects.result_line import ResultLine
from procycling_scraper.scraping.domain.repositories.race_repository import RaceRepository
from procycling_scraper.analysis.application.dto.analysis_dtos import RiderResultDTO
from procycling_scraper.scraping.infrastructure.database.schema import (
    classifications_table, pcs_points_results_table, races_table, riders_table
)

class PostgresRaceRepository(RaceRepository):
    def __init__(self, engine: Engine):
        self._engine = engine

    def save(self, race: Race) -> None:
        with self._engine.connect() as conn:
            with conn.begin() as transaction:
                try:
                    race_db_id = self._save_race_and_get_id(conn, race)
                    rider_id_map = self._get_rider_id_map(conn, race)
                    
                    for classification in race.classifications:
                        classification_db_id = self._save_classification_and_get_id(
                            conn, classification, race_db_id
                        )
                        self._save_results(conn, classification.results,
                                           classification_db_id, rider_id_map)
                except Exception:
                    transaction.rollback()
                    raise

    def find_all_results_by_rider_ids(self, rider_ids: List[UUID]) -> Dict[UUID, List[RiderResultDTO]]:
        if not rider_ids: return {}
        stmt = select(
            pcs_points_results_table.c.rider_id,
            pcs_points_results_table.c.points,
            races_table.c.year,
            races_table.c.type.label("race_type")
        ).select_from(pcs_points_results_table).join(
            classifications_table, pcs_points_results_table.c.classification_id == classifications_table.c.id
        ).join(
            races_table, classifications_table.c.race_id == races_table.c.id
        ).where(pcs_points_results_table.c.rider_id.in_(rider_ids))
        with self._engine.connect() as conn:
            db_results: List[Any] = list(conn.execute(stmt).fetchall())
        grouped_results: Dict[UUID, List[RiderResultDTO]] = {rider_id: [] for rider_id in rider_ids}
        for row in db_results:
            result = RiderResultDTO(rider_id=row.rider_id, points=row.points, year=row.year, race_type=row.race_type)
            grouped_results[row.rider_id].append(result)
        return grouped_results

    def find_by_pcs_id(self, pcs_id: str):
        pass

    def _save_race_and_get_id(self, conn: Connection, race: Race) -> UUID:
        stmt = insert(races_table).values(
            pcs_id=race.pcs_id, name=race.name, year=race.year, type=race.race_type
        )
        stmt = stmt.on_conflict_do_update(
            index_elements=['pcs_id'], set_={'name': stmt.excluded.name},
        ).returning(races_table.c.id)
        result = conn.execute(stmt).scalar_one()
        return result

    def _get_rider_id_map(self, conn: Connection, race: Race) -> Dict[str, UUID]:
        all_rider_pcs_ids = {r.rider_pcs_id for c in race.classifications for r in c.results}
        if not all_rider_pcs_ids: return {}
        stmt = select(riders_table.c.pcs_id, riders_table.c.id).where(riders_table.c.pcs_id.in_(all_rider_pcs_ids))
        result = conn.execute(stmt).fetchall()
        return {pcs_id: db_id for pcs_id, db_id in result}

    def _save_classification_and_get_id(self, conn: Connection, classification: Classification, race_db_id: UUID) -> UUID:
        stmt = insert(classifications_table).values(
            race_id=race_db_id,
            type=classification.classification_type,
            stage_number=classification.stage_number
        )
        stmt = stmt.on_conflict_do_update(
            index_elements=['race_id', 'type', 'stage_number'],
            set_={'type': classification.classification_type},
        ).returning(classifications_table.c.id)
        result = conn.execute(stmt).scalar_one()
        return result

    def _save_results(self, conn: Connection, results: List[ResultLine], classification_db_id: UUID, rider_id_map: Dict[str, UUID]):
        if not results: return
        results_to_insert: List[Dict[str, Union[UUID, str, int]]] = []
        for result in results:
            rider_db_id = rider_id_map.get(result.rider_pcs_id)
            if rider_db_id:
                results_to_insert.append({
                    "classification_id": classification_db_id,
                    "rider_id": rider_db_id,
                    "team_name": result.team_name,
                    "points": result.points
                })
        
        if results_to_insert:
            stmt = insert(pcs_points_results_table).values(results_to_insert)
            stmt = stmt.on_conflict_do_nothing(index_elements=['classification_id', 'rider_id'])
            conn.execute(stmt)