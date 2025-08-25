import pathlib
from procycling_scraper.scraping.infrastructure.scrapers.procyclingstats_race_list_scraper import ProCyclingStatsRaceListScraper
from procycling_scraper.scraping.domain.entities.race import RaceType

# Note: We test the parsing logic by loading a small, local HTML sample and monkeypatching requests.get

SAMPLE_HTML = """
<html>
  <body>
    <table class="basic">
      <thead>
        <tr>
          <th>Race</th>
          <th>Class</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><a href="race/some-classic/2024/result">Some Classic</a></td>
          <td>1.Pro</td>
        </tr>
        <tr>
          <td><a href="race/some-stage-race/2024/gc">Some Stage Race</a></td>
          <td>2.UWT</td>
        </tr>
      </tbody>
    </table>
  </body>
</html>
"""


class DummyResp:
    def __init__(self, text: str, status_code: int = 200):
        self.text = text
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise Exception("bad status")


def test_parse_race_list_from_html(monkeypatch):
    def fake_get(url, timeout=10):
        return DummyResp(SAMPLE_HTML)

    monkeypatch.setattr("requests.get", fake_get)

    scraper = ProCyclingStatsRaceListScraper(base_url="https://example.com")
    items = scraper.scrape(2024)

    assert ("race/some-classic/2024", RaceType.ONE_DAY) in items
    assert ("race/some-stage-race/2024", RaceType.STAGE_RACE) in items
