import re
from typing import Dict, List, Set, Tuple

import requests
from bs4 import BeautifulSoup, Tag

from procycling_scraper.scraping.application.ports.race_list_scraper import RaceListScraper
from procycling_scraper.scraping.domain.entities.race import RaceType


class ProCyclingStatsRaceListScraper(RaceListScraper):
    # WorldTour, World/Continental Champs, ProSeries, Europe Tour
    CIRCUIT_IDS = ["1", "2"]  # "26", "13"

    def __init__(self, base_url: str = "https://www.procyclingstats.com"):
        self._base_url = base_url

    def scrape(self, year: int) -> List[Tuple[str, RaceType]]:
        print(f"--- Scraping Race List for {year} ---")
        unique_races: Set[Tuple[str, RaceType]] = set()

        for circuit_id in self.CIRCUIT_IDS:
            target_url = f"{self._base_url}/races.php?year={year}&circuit={circuit_id}&filter=Filter"
            print(f"Fetching races from circuit URL: {target_url}")

            try:
                response = requests.get(target_url, timeout=10)
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                print(
                    f"WARN: Could not fetch URL {target_url}: {e}. Skipping circuit.")
                continue

            soup = BeautifulSoup(response.text, 'lxml')

            table = soup.select_one('table[class*="basic"]')
            if not isinstance(table, Tag):
                print(
                    f"WARN: No races table found for circuit {circuit_id}. Skipping.")
                continue

            try:
                thead = table.find("thead")
                if not isinstance(thead, Tag):
                    continue

                header_tags = thead.find_all("th")
                headers = [h.text.strip() for h in header_tags]

                header_map: Dict[str, int] = {
                    "race": headers.index("Race"),
                    "class": headers.index("Class")
                }
            except (ValueError, AttributeError):
                print(
                    f"WARN: Could not find required headers in table for circuit {circuit_id}. Skipping.")
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
                race_type = RaceType.STAGE_RACE if class_cell_text.startswith(
                    "2.") else RaceType.ONE_DAY

                link_cell = cells[header_map["race"]]
                if not isinstance(link_cell, Tag):
                    continue

                link_tag = link_cell.find("a")
                if not isinstance(link_tag, Tag):
                    continue

                href_value = link_tag.get("href")
                if not isinstance(href_value, str):
                    continue

                base_race_url = re.sub(
                    r"/(gc|result|results)$", "", href_value)
                unique_races.add((base_race_url, race_type))

        print(
            f"--- Found {len(unique_races)} total unique races for {year} ---")
        return list(unique_races)


if __name__ == "__main__":
    scraper = ProCyclingStatsRaceListScraper()
    races_to_scrape = scraper.scrape(year=2024)

    if races_to_scrape:
        print("\n--- Race List Scraping Test Results ---")
        one_day_races = len(
            [r for r, t in races_to_scrape if t == RaceType.ONE_DAY])
        stage_races = len(
            [r for r, t in races_to_scrape if t == RaceType.STAGE_RACE])
        print(
            f"Found {one_day_races} One-Day races and {stage_races} Stage races.")

        print("\nFirst 5 stage race URLs found:")
        stage_race_urls = [url for url,
                           t in races_to_scrape if t == RaceType.STAGE_RACE]
        for url in stage_race_urls[:5]:
            print(f"- {url}")
    else:
        print("Scraping did not return any race URLs.")
