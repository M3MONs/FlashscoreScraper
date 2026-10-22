from pathlib import Path

import pytest

from engines.base_engine import BaseEngine
from parsers.base_parser import BaseParser
from scraper.scraper_service import ScraperService
from stats.football_stats_parser import FootballStatsParser
from utils.url_builder import FlashscoreUrlBuilder

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures" / "football"
EVENT_URL = "https://www.flashscore.com/match/football/aston-villa-W00wmLO0/west-ham-Cxq57r8g/?mid=U7CL8Og5"
STATS_URL = FlashscoreUrlBuilder.build_event_info_url(EVENT_URL, FootballStatsParser.url_path)


class FakeEngine(BaseEngine):
    def __init__(self, pages: dict[str, str]) -> None:
        super().__init__()
        self.pages = pages
        self.requested: list[str] = []

    def _get_page(self, url: str, wait_for_selector: str | None = None) -> str:
        self.requested.append(url)
        if url not in self.pages:
            raise TimeoutError(f"Timeout waiting for {wait_for_selector}")
        return self.pages[url]

    def _get_pages(self, urls: dict[str, str], wait_for_selectors: dict[str, str | None] | None = None) -> dict[str, str]:
        return {key: self._get_page(url) for key, url in urls.items()}

    def _close(self) -> None:
        pass


def _read_fixture(name: str) -> str:
    try:
        return (FIXTURES_DIR / name).read_text(encoding="utf-8")
    except FileNotFoundError:
        pytest.fail(f"Fixture file not found: {FIXTURES_DIR / name}")


def _service(sport: str, pages: dict[str, str]) -> tuple[ScraperService, FakeEngine]:
    engine = FakeEngine(pages)
    return ScraperService(engine, BaseParser.create(sport)), engine


class TestScraperServiceStats:
    def test_event_without_stats_fetches_only_event_page(self) -> None:
        service, engine = _service("football", {EVENT_URL: _read_fixture("event.html")})
        result = service.fetch_and_parse_event(EVENT_URL)
        assert "stats" not in result
        assert engine.requested == [EVENT_URL]

    def test_event_with_stats(self) -> None:
        service, engine = _service("football", {EVENT_URL: _read_fixture("event.html"), STATS_URL: _read_fixture("stats.html")})
        result = service.fetch_and_parse_event_with_stats(EVENT_URL)
        assert "Top stats" in result["stats"]
        assert engine.requested == [EVENT_URL, STATS_URL]
        assert STATS_URL.endswith("?mid=U7CL8Og5")

    def test_unsupported_sport_raises_before_fetching(self) -> None:
        service, engine = _service("volleyball", {})
        with pytest.raises(ValueError, match="not supported"):
            service.fetch_and_parse_event_with_stats(EVENT_URL)
        assert engine.requested == []

    def test_stats_page_fetch_failure_raises_no_stats(self) -> None:
        service, _ = _service("football", {EVENT_URL: _read_fixture("event.html")})
        with pytest.raises(ValueError, match="No stats available"):
            service.fetch_and_parse_event_with_stats(EVENT_URL)
