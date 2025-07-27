from typing import Dict, List
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.engine import Engine

from procycling_scraper.scraping.domain.entities.race import Race
from procycling_scraper.scraping.domain.repositories.race_repository import RaceRepository
from procycling_scraper.scraping.infrastructure.database.schema import (
    classifications_table, pcs_points_results_table, races_table, riders_table
)


class PostgresRaceRepository(RaceRepository):
    def __init__(self, engine: Engine):
        self._engine = engine

    def save(self, race: Race) -> None:
        """Saves the entire Race aggregate in a single transaction."""
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

    def find_by_pcs_id(self, pcs_id: str):
        pass

    def _save_race_and_get_id(self, conn, race: Race) -> UUID:
        """Saves the race and returns its database ID."""
        stmt = insert(races_table).values(
            pcs_id=race.pcs_id,
            name=race.name,
            year=race.year,
            type=race.race_type
        )
        stmt = stmt.on_conflict_do_update(
            index_elements=['pcs_id'],
            set_={'name': stmt.excluded.name},
            where=(races_table.c.pcs_id == stmt.excluded.pcs_id)
        ).returning(races_table.c.id)

        result = conn.execute(stmt).scalar_one()
        return result

    def _get_rider_id_map(self, conn, race: Race) -> Dict[str, UUID]:
        """
        Fetches all rider DB IDs for a given race in a single query
        for performance optimization.
        """
        all_rider_pcs_ids = {
            result.rider_pcs_id
            for classification in race.classifications
            for result in classification.results
        }
        if not all_rider_pcs_ids:
            return {}

        stmt = select(riders_table.c.pcs_id, riders_table.c.id).where(
            riders_table.c.pcs_id.in_(all_rider_pcs_ids)
        )

        result = conn.execute(stmt).fetchall()
        return {pcs_id: db_id for pcs_id, db_id in result}

    def _save_classification_and_get_id(self, conn, classification, race_db_id: UUID) -> UUID:
        """Saves a classification and returns its database ID."""
        stmt = insert(classifications_table).values(
            race_id=race_db_id,
            type=classification.classification_type,
            stage_number=classification.stage_number
        )
        stmt = stmt.on_conflict_do_nothing(
            index_elements=['race_id', 'type', 'stage_number']
        ).returning(classifications_table.c.id)

        conn.execute(stmt)
        select_stmt = select(classifications_table.c.id).where(
            classifications_table.c.race_id == race_db_id,
            classifications_table.c.type == classification.classification_type,
            classifications_table.c.stage_number == classification.stage_number
        )
        classification_id = conn.execute(select_stmt).scalar_one()
        return classification_id

    def _save_results(self, conn, results, classification_db_id: UUID, rider_id_map: Dict[str, UUID]):
        """Saves a list of ResultLine objects."""
        if not results:
            return

        results_to_insert = []
        for result in results:
            rider_db_id = rider_id_map.get(result.rider_pcs_id)
            if rider_db_id:  # Solo insertamos si encontramos el rider en nuestro mapa
                results_to_insert.append({
                    "classification_id": classification_db_id,
                    "rider_id": rider_db_id,
                    "team_name": result.team_name,
                    "points": result.points
                })

        if results_to_insert:
            conn.execute(insert(pcs_points_results_table), results_to_insert)
