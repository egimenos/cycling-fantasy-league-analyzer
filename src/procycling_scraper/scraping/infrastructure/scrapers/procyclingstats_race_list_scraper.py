from typing import List
import requests
from bs4 import BeautifulSoup, Tag

from procycling_scraper.scraping.application.ports.race_list_scraper import RaceListScraper


class ProCyclingStatsRaceListScraper(RaceListScraper):

    def __init__(self, base_url: str = "https://www.procyclingstats.com"):
        self._base_url = base_url

    def scrape(self, year: int) -> List[str]:
        """
        Scrapes procyclingstats.com for all UCI race URLs in a given year.
        """
        target_url = (
            f"{self._base_url}/races.php?season={year}&month=&category=1"
            "&racelevel=&pracelevel=smallerorequal&racenation=&class="
            "&filter=Filter&p=uci&s=calendar-plus-filters"
        )
        print(f"Fetching race list from: {target_url}")

        try:
            response = requests.get(target_url, timeout=10)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching URL {target_url}: {e}")
            return []

        soup = BeautifulSoup(response.text, 'lxml')

        table = soup.find("table", class_="basic")
        if not isinstance(table, Tag):
            print("ERROR: No se encontró la tabla de resultados en la página.")
            return []

        urls = set()
        for link in table.find_all("a", href=lambda href: isinstance(href, str) and href.startswith("race/")):
            if isinstance(link, Tag):
                href = link.get("href")
                full_url = f"{self._base_url}/{href}"
                urls.add(full_url)

        print(f"Found {len(urls)} unique race URLs for {year}.")
        return list(urls)


# To test the script
if __name__ == "__main__":
    scraper = ProCyclingStatsRaceListScraper()
    scraped_urls = scraper.scrape(year=2024)

    if scraped_urls:
        print("\n--- Scraping Test Results ---")
        print(f"Successfully found {len(scraped_urls)} URLs.")
        print("First 5 URLs found:")
        for url in scraped_urls[:5]:
            print(f"- {url}")
    else:
        print("\n--- Scraping Test Results ---")
        print("Scraping did not return any URLs. Please check for errors above.")
