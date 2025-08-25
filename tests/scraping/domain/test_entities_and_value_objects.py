from procycling_scraper.scraping.domain.entities.classification import (
    Classification,
    ClassificationType,
)
from procycling_scraper.scraping.domain.entities.race import Race, RaceType
from procycling_scraper.scraping.domain.value_objects.result_line import ResultLine


def test_race_aggregate_add_classification_and_results():
    race = Race(
        pcs_id="tour-de-test",
        name="Tour de Test 2024",
        year=2024,
        race_type=RaceType.STAGE_RACE,
    )

    classification = Classification(
        classification_type=ClassificationType.GENERAL,
        results=[
            ResultLine(rider_pcs_id="rider-1", team_name="Team A", points=50),
            ResultLine(rider_pcs_id="rider-2", team_name="Team B", points=30),
        ],
    )

    race.add_classification(classification)

    assert len(race.classifications) == 1
    assert race.classifications[0].classification_type == ClassificationType.GENERAL
    assert sum(r.points for r in race.classifications[0].results) == 80
