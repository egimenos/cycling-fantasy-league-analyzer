import re
from typing import Dict, List, Optional, Set, Tuple

import requests
from bs4 import BeautifulSoup, Tag
import logging

from procycling_scraper.scraping.application.dto.scraped_race_data import ScrapedRaceData
from procycling_scraper.scraping.application.ports.race_data_scraper import RaceDataScraper
from procycling_scraper.scraping.domain.entities.classification import Classification, ClassificationType
from procycling_scraper.scraping.domain.entities.race import Race, RaceType
from procycling_scraper.scraping.domain.entities.rider import Rider
from procycling_scraper.scraping.domain.value_objects.result_line import ResultLine

logger = logging.getLogger(__name__)


class ProCyclingStatsRaceDataScraper(RaceDataScraper):
    def __init__(self, base_url: str = "https://www.procyclingstats.com"):
        self._base_url = base_url

    def scrape(self, race_info: Tuple[str, RaceType]) -> ScrapedRaceData:
        base_race_url_path = re.sub(r"/(gc|result|results)$", "", race_info[0])
        race_type = race_info[1]
        full_base_url = f"{self._base_url}/{base_race_url_path}"
        logger.info("scrape_race_start", extra={
                    "race_url": full_base_url, "race_type": race_type.value})
        try:
            if race_type == RaceType.ONE_DAY:
                return self._scrape_one_day_race(full_base_url, race_type)
            else:
                return self._scrape_stage_race(full_base_url, race_type)
        except ValueError as e:
            logger.error("scrape_race_failed", extra={
                         "race_url": full_base_url, "error": str(e)})
            race = Race(pcs_id=base_race_url_path,
                        name="Scraping Failed", year=0, race_type=race_type)
            return ScrapedRaceData(race=race, riders=[])

    def _scrape_one_day_race(self, race_url: str, race_type: RaceType) -> ScrapedRaceData:
        results_url = f"{race_url}/result"
        race, soup = self._scrape_race_details(results_url, race_type)
        if not soup:
            return ScrapedRaceData(race=race, riders=[])
        gc_classification, gc_riders = self._scrape_classification_table(
            soup, ClassificationType.GENERAL)
        race.add_classification(gc_classification)
        return ScrapedRaceData(race=race, riders=gc_riders)

    def _scrape_stage_race(self, race_url: str, race_type: RaceType) -> ScrapedRaceData:
        entry_url = f"{race_url}/gc"
        race, soup = self._scrape_race_details(entry_url, race_type)
        if not soup:
            return ScrapedRaceData(race=race, riders=[])

        all_found_riders: Set[Rider] = set()

        classification_urls = self._extract_classification_urls(soup)
        if not classification_urls:
            logger.warning("classification_urls_missing",
                           extra={"race_url": race_url})
            _, gc_riders = self._scrape_classification_table(
                soup, ClassificationType.GENERAL)
            all_found_riders.update(gc_riders)
        else:
            for url_path, classification_type, stage_num in classification_urls:
                full_url = f"{self._base_url}/{url_path}"
                logger.info("scrape_classification", extra={
                            "classification_url": full_url, "type": classification_type.value, "stage": stage_num})
                page_soup = self._get_page_soup(full_url)
                if not page_soup:
                    continue
                classification, riders = self._scrape_classification_table(
                    page_soup, classification_type, stage_num)
                race.add_classification(classification)
                all_found_riders.update(riders)
        return ScrapedRaceData(race=race, riders=list(all_found_riders))

    def _extract_classification_urls(self, soup: BeautifulSoup) -> List[Tuple[str, ClassificationType, Optional[int]]]:
        nav_containers = soup.select('div.selectNav')
        if not nav_containers:
            return []
        for container in nav_containers:
            prev_next_links = container.find_all("a")
            has_prev_next = False
            for link in prev_next_links:
                link_text = link.get_text(strip=True)
                if "PREV" in link_text or "NEXT" in link_text or "«" in link_text or "»" in link_text:
                    has_prev_next = True
                    break
            if has_prev_next:
                target_select_menu = container.find("select")
                if isinstance(target_select_menu, Tag):
                    return self._parse_select_menu_options(target_select_menu)
        logger.warning("classification_select_missing")
        return []

    def _parse_select_menu_options(self, select_menu: Tag) -> List[Tuple[str, ClassificationType, Optional[int]]]:
        urls_to_scrape: List[Tuple[str,
                                   ClassificationType, Optional[int]]] = []
        for option in select_menu.find_all("option"):
            if not isinstance(option, Tag) or not option.has_attr("value"):
                continue
            value_attr = option["value"]
            if not isinstance(value_attr, str) or not value_attr:
                continue
            url_path, option_text = value_attr, option.text.lower()
            if "teams" in url_path or "youth" in url_path:
                continue
            stage_num_match = re.search(r"stage-(\d+)", url_path)
            if "stage-" in url_path and stage_num_match and "points" not in url_path and "kom" not in url_path:
                urls_to_scrape.append(
                    (url_path, ClassificationType.STAGE, int(stage_num_match.group(1))))
                continue
            if "points classification" in option_text:
                urls_to_scrape.append(
                    (url_path, ClassificationType.POINTS, None))
            elif "mountains classification" in option_text:
                urls_to_scrape.append((url_path, ClassificationType.KOM, None))
            elif "final gc" in option_text:
                urls_to_scrape.append(
                    (url_path, ClassificationType.GENERAL, None))
        return urls_to_scrape

    def _get_page_soup(self, url: str) -> Optional[BeautifulSoup]:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 404:
                return None
            response.raise_for_status()
            return BeautifulSoup(response.text, 'lxml')
        except requests.exceptions.RequestException as e:
            logger.error("fetch_failed", extra={"url": url, "error": str(e)})
            return None

    def _scrape_race_details(self, url: str, race_type: RaceType) -> Tuple[Race, BeautifulSoup]:
        soup = self._get_page_soup(url)
        if not soup:
            raise ValueError(f"Could not fetch or parse page: {url}")
        title_tag = soup.find("h1")
        if not isinstance(title_tag, Tag):
            raise ValueError(f"Race title (h1) not found on page: {url}")
        title = title_tag.text.strip()
        year_match = re.search(r"^\d{4}", title)
        year = int(year_match.group(0)) if year_match else 0
        pcs_id = re.sub(r"/(gc|result|results|stage-\d+|points|kom).*",
                        "", url).replace(f"{self._base_url}/", "")
        race = Race(pcs_id=pcs_id, name=title, year=year, race_type=race_type)
        return race, soup

    def _scrape_classification_table(self, soup: BeautifulSoup, classification_type: ClassificationType, stage_number: Optional[int] = None) -> Tuple[Classification, List[Rider]]:
        results: List[ResultLine] = []
        found_riders: List[Rider] = []
        table = soup.select_one("div.resTab:not(.hide) table.results")
        if not isinstance(table, Tag):
            logger.warning("results_table_missing", extra={
                           "classification": classification_type.value})
            return Classification(classification_type, [], stage_number), []
        try:
            thead = table.find("thead")
            if not isinstance(thead, Tag):
                raise ValueError("Table head not found")
            header_tags = thead.find_all("th")
            team_headers, points_header, rider_header = [
                "Team", "Tm"], "Pnt", "Rider"
            headers = [h.text.strip() for h in header_tags]
            team_header_found = next(
                (th for th in team_headers if th in headers), None)
            if not team_header_found:
                raise ValueError("Team header not found")
            header_map: Dict[str, int] = {"Rider": headers.index(rider_header), "Team": headers.index(
                team_header_found), "Pnt": headers.index(points_header)}
        except (ValueError, AttributeError):
            logger.warning("results_table_headers_missing", extra={
                           "classification": classification_type.value})
            return Classification(classification_type, [], stage_number), []
        tbody = table.find("tbody")
        if not isinstance(tbody, Tag):
            return Classification(classification_type, [], stage_number), []
        for row_element in tbody.find_all("tr"):
            if not isinstance(row_element, Tag):
                continue
            parsed_data = self._parse_result_row(row_element, header_map)
            if parsed_data:
                rider, result_line = parsed_data
                results.append(result_line)
                found_riders.append(rider)
        classification = Classification(
            classification_type=classification_type, results=results, stage_number=stage_number)
        return classification, found_riders

    def _parse_result_row(self, row: Tag, header_map: Dict[str, int]) -> Optional[Tuple[Rider, ResultLine]]:
        if len(row.find_all("td")) <= max(header_map.values()):
            return None
        try:
            pcs_points_text = row.find_all(
                "td")[header_map["Pnt"]].text.strip()
            pcs_points_str = pcs_points_text.split(
            )[0] if pcs_points_text else "0"
            pcs_points = int(pcs_points_str)
            if pcs_points <= 0:
                return None
        except (ValueError, IndexError):
            return None
        rider_cell = row.find_all("td")[header_map["Rider"]]
        if not isinstance(rider_cell, Tag):
            return None
        rider_link = rider_cell.find("a")
        if not isinstance(rider_link, Tag):
            return None
        href_value = rider_link.get("href")
        if not isinstance(href_value, str):
            return None
        rider_pcs_id = href_value
        rider_name = rider_link.text.strip()
        rider = Rider(pcs_id=rider_pcs_id, name=rider_name)
        team_name = row.find_all("td")[header_map["Team"]].text.strip()
        result_line = ResultLine(
            rider_pcs_id=rider_pcs_id, team_name=team_name, points=pcs_points)
        return rider, result_line
