from procycling_scraper.analysis.domain.rider_matching_service import (
    RiderMatchingService,
)
from procycling_scraper.scraping.domain.entities.rider import Rider


def test_find_best_match_high_score():
    riders = [
        Rider(pcs_id="tadej-pogacar", name="Pogacar Tadej"),
        Rider(pcs_id="jonas-vingegaard", name="Vingegaard Jonas"),
    ]
    service = RiderMatchingService(riders, score_cutoff=80)

    match = service.find_best_match("pogacar tadej")
    assert match is not None
    assert match.pcs_id == "tadej-pogacar"


def test_find_best_match_no_choices():
    service = RiderMatchingService([], score_cutoff=80)
    assert service.find_best_match("any") is None
