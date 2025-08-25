from typing import Dict, List, Optional

from thefuzz import process

from procycling_scraper.scraping.domain.entities.rider import Rider


class RiderMatchingService:
    def __init__(self, all_riders: List[Rider], score_cutoff: int = 85):
        self._choices: Dict[str, Rider] = {
            self._normalize(r.name): r for r in all_riders
        }
        self._score_cutoff = score_cutoff

    def _normalize(self, name: str) -> str:
        return name.lower()

    def find_best_match(self, api_name: str) -> Optional[Rider]:
        if not self._choices:
            return None

        normalized_api_name = self._normalize(api_name)

        result = process.extractOne(normalized_api_name, self._choices.keys())

        if not result:
            return None

        best_match_name = result[0]
        score = result[1]

        if score >= self._score_cutoff:
            return self._choices[best_match_name]

        return None
