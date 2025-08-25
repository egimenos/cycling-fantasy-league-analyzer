import logging
import re
from typing import Dict, List, Set, Tuple

import requests
from bs4 import BeautifulSoup, Tag

from procycling_scraper.scraping.application.ports.race_list_scraper import (
    RaceListScraper,
)
from procycling_scraper.scraping.domain.entities.race import RaceType

logger = logging.getLogger(__name__)


class ProCyclingStatsRaceListScraper(RaceListScraper):
    WORLD_TOUR_CIRCUIT_ID = "1"
    UCI_PRO_SERIES_CIRCUIT_ID = "26"
    EUROPE_TOUR_ID = "13"
    CIRCUIT_IDS = [WORLD_TOUR_CIRCUIT_ID, UCI_PRO_SERIES_CIRCUIT_ID, EUROPE_TOUR_ID]

    def __init__(self, base_url: str = "https://www.procyclingstats.com"):
        self._base_url = base_url

    def scrape(self, year: int) -> List[Tuple[str, RaceType]]:
        logger.info("scrape_race_list_start", extra={"year": year})
        unique_races: Set[Tuple[str, RaceType]] = set()

        for circuit_id in self.CIRCUIT_IDS:
            target_url = f"{self._base_url}/races.php?year={year}&circuit={circuit_id}&filter=Filter"
            logger.info(
                "fetch_circuit_races",
                extra={"url": target_url, "circuit_id": circuit_id},
            )

            try:
                response = requests.get(target_url, timeout=10)
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                logger.warning(
                    "fetch_circuit_failed",
                    extra={
                        "url": target_url,
                        "error": str(e),
                        "circuit_id": circuit_id,
                    },
                )
                continue

            soup = BeautifulSoup(response.text, "lxml")

            table = soup.select_one('table[class*="basic"]')
            if not isinstance(table, Tag):
                logger.warning("no_races_table", extra={"circuit_id": circuit_id})
                continue

            try:
                thead = table.find("thead")
                if not isinstance(thead, Tag):
                    continue

                header_tags = thead.find_all("th")
                headers = [h.text.strip() for h in header_tags]

                header_map: Dict[str, int] = {
                    "race": headers.index("Race"),
                    "class": headers.index("Class"),
                }
            except (ValueError, AttributeError):
                logger.warning(
                    "table_headers_missing", extra={"circuit_id": circuit_id}
                )
                continue

            tbody = table.find("tbody")
            if not isinstance(tbody, Tag):
                continue

            for row in tbody.find_all("tr"):
                if not isinstance(row, Tag):
                    continue

                cells = row.find_all("td")
                if len(cells) <= max(header_map.values()):
                    continue

                class_cell_text = cells[header_map["class"]].text.strip()
                race_type = (
                    RaceType.STAGE_RACE
                    if class_cell_text.startswith("2.")
                    else RaceType.ONE_DAY
                )

                link_cell = cells[header_map["race"]]
                if not isinstance(link_cell, Tag):
                    continue

                link_tag = link_cell.find("a")
                if not isinstance(link_tag, Tag):
                    continue

                href_value = link_tag.get("href")
                if not isinstance(href_value, str):
                    continue

                base_race_url = re.sub(r"/(gc|result|results)$", "", href_value)
                unique_races.add((base_race_url, race_type))

        logger.info(
            "scrape_race_list_complete",
            extra={"year": year, "unique_races": len(unique_races)},
        )
        return list(unique_races)
