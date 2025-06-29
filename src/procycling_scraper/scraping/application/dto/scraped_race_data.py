from dataclasses import dataclass
from typing import List

from procycling_scraper.scraping.domain.entities.race import Race
from procycling_scraper.scraping.domain.entities.rider import Rider


@dataclass(frozen=True)
class ScrapedRaceData:
    """
    A Data Transfer Object to hold the data scraped from a single race page.
    """
    race: Race
    riders: List[Rider]
