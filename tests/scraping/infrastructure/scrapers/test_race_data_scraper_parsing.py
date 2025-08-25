from procycling_scraper.scraping.infrastructure.scrapers.procyclingstats_race_data_scraper import ProCyclingStatsRaceDataScraper
from procycling_scraper.scraping.domain.entities.classification import ClassificationType
from procycling_scraper.scraping.domain.entities.race import RaceType

# We unit-test parsing by monkeypatching network and returning minimal HTML snippets per page

ONE_DAY_HTML = """
<html>
  <body>
    <h1>2024 Some Classic</h1>
    <div class="resTab">
      <table class="results">
        <thead>
          <tr><th>Rider</th><th>Team</th><th>Pnt</th></tr>
        </thead>
        <tbody>
          <tr><td><a href="rider/john-doe">John Doe</a></td><td>Team A</td><td>50</td></tr>
          <tr><td><a href="rider/jane-roe">Jane Roe</a></td><td>Team B</td><td>30</td></tr>
        </tbody>
      </table>
    </div>
  </body>
</html>
"""

STAGE_RACE_GC_HTML = """
<html>
  <body>
    <h1>2024 Some Stage Race</h1>
    <div class="selectNav">
      <a>PREV</a><a>NEXT</a>
      <select>
        <option value="race/some-stage-race/2024/stage-1">Stage 1</option>
        <option value="race/some-stage-race/2024/points">Points classification</option>
        <option value="race/some-stage-race/2024/kom">Mountains classification</option>
        <option value="race/some-stage-race/2024/gc">Final GC</option>
      </select>
    </div>
  </body>
</html>
"""

STAGE_HTML = """
<html>
  <body>
    <div class="resTab">
      <table class="results">
        <thead>
          <tr><th>Rider</th><th>Tm</th><th>Pnt</th></tr>
        </thead>
        <tbody>
          <tr><td><a href="rider/john-doe">John Doe</a></td><td>Team A</td><td>10</td></tr>
        </tbody>
      </table>
    </div>
  </body>
</html>
"""

POINTS_HTML = STAGE_HTML.replace("10", "8")
KOM_HTML = STAGE_HTML.replace("10", "6")
GC_HTML = STAGE_HTML.replace("10", "12")


class DummyResp:
    def __init__(self, text: str, status_code: int = 200):
        self.text = text
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise Exception("bad status")


def test_one_day_parsing(monkeypatch):
    def fake_get(url, timeout=10):
        return DummyResp(ONE_DAY_HTML)
    monkeypatch.setattr("requests.get", fake_get)

    scraper = ProCyclingStatsRaceDataScraper(base_url="https://example.com")
    data = scraper.scrape(("race/some-classic/2024", RaceType.ONE_DAY))

    assert data.race.name.startswith("2024 Some Classic")
    assert len(data.race.classifications) == 1
    assert data.race.classifications[0].classification_type == ClassificationType.GENERAL
    assert sum(r.points for r in data.race.classifications[0].results) == 80


def test_stage_race_parsing(monkeypatch):
    def fake_get(url, timeout=10):
        if url.endswith("/gc"):
            return DummyResp(STAGE_RACE_GC_HTML)
        if url.endswith("/stage-1"):
            return DummyResp(STAGE_HTML)
        if url.endswith("/points"):
            return DummyResp(POINTS_HTML)
        if url.endswith("/kom"):
            return DummyResp(KOM_HTML)
        if url.endswith("/gc") or url.endswith("/result"):
            return DummyResp(GC_HTML)
        return DummyResp(STAGE_HTML)

    monkeypatch.setattr("requests.get", fake_get)

    scraper = ProCyclingStatsRaceDataScraper(base_url="https://example.com")
    data = scraper.scrape(("race/some-stage-race/2024", RaceType.STAGE_RACE))

    # Should collect classifications for Stage, Points, KOM, GC
    assert {c.classification_type for c in data.race.classifications} == {
        ClassificationType.STAGE,
        ClassificationType.POINTS,
        ClassificationType.KOM,
        ClassificationType.GENERAL,
    }
