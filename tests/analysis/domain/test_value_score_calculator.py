import math
from datetime import datetime
from uuid import uuid4

from procycling_scraper.analysis.domain.value_score_calculator import ValueScoreCalculator
from procycling_scraper.analysis.application.dto.analysis_dtos import RiderResultDTO
from procycling_scraper.scraping.domain.entities.race import RaceType


def _year(n: int) -> int:
    return datetime.now().year - n


def test_value_score_weights_by_year_and_type():
    calc = ValueScoreCalculator()
    results = [
        RiderResultDTO(rider_id=uuid4(), points=100,
                       year=_year(0), race_type=RaceType.ONE_DAY),
        RiderResultDTO(rider_id=uuid4(), points=100,
                       year=_year(1), race_type=RaceType.ONE_DAY),
        RiderResultDTO(rider_id=uuid4(), points=100,
                       year=_year(2), race_type=RaceType.STAGE_RACE),
        RiderResultDTO(rider_id=uuid4(), points=100,
                       year=_year(3), race_type=RaceType.ONE_DAY),
    ]

    total, value = calc.calculate(
        results, price=200, target_race_type=RaceType.ONE_DAY)

    # Expected: 100*1.0 + 100*0.5 + 100*0.25*0.5 + 100*0.1 = 100 + 50 + 12.5 + 10 = 172.5
    assert math.isclose(total, 172.5, rel_tol=1e-9)
    assert math.isclose(value, 172.5/200, rel_tol=1e-9)


def test_value_score_zero_price():
    calc = ValueScoreCalculator()
    total, value = calc.calculate(
        [], price=0, target_race_type=RaceType.ONE_DAY)
    assert total == 0
    assert value == 0.0
