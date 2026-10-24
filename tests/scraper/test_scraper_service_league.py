from pathlib import Path

import pytest

from engines.base_engine import BaseEngine
from parsers.base_parser import BaseParser
from scraper.scraper_service import ScraperService
from utils.url_builder import FlashscoreUrlBuilder

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures" / "football"
RESULTS_URL = "https://www.flashscore.com/football/germany/bundesliga/results/"
FIXTURES_URL = "https://www.flashscore.com/football/germany/bundesliga/fixtures/"


class FakeEngine(BaseEngine):
    def __init__(self, pages: dict[str, str]) -> None:
        super().__init__()
        self.pages = pages
        self.load_more: dict[str, str | None] = {}

    def _get_page(self, url: str, wait_for_selector: str | None = None, load_more_selector: str | None = None) -> str:
        self.load_more[url] = load_more_selector
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


class TestBuildLeagueUrl:
    @pytest.mark.parametrize(
        "league",
        [
            "germany/bundesliga",
            "/germany/bundesliga/",
            "football/germany/bundesliga",
            "https://www.flashscore.com/football/germany/bundesliga/",
            "https://www.flashscore.com/football/germany/bundesliga/results/",
        ],
    )
    def test_normalizes_league_input(self, league: str) -> None:
        assert FlashscoreUrlBuilder.build_league_url("football", league, "results") == RESULTS_URL


class TestFetchAndParseLeague:
    def test_merges_results_and_fixtures(self) -> None:
        service, engine = _service("football", {RESULTS_URL: _read_fixture("league_results.html"), FIXTURES_URL: _read_fixture("league_fixtures.html")})

        result = service.fetch_and_parse_league("germany/bundesliga")

        statuses = {match.status for match in result["matches"]}
        assert statuses == {"finished", "scheduled"}
        urls = [match.event_url for match in result["matches"]]
        assert len(urls) == len(set(urls))
        assert all(selector is not None for selector in engine.load_more.values())

    def test_missing_section_is_skipped(self) -> None:
        service, _ = _service("football", {RESULTS_URL: _read_fixture("league_results.html")})

        result = service.fetch_and_parse_league("germany/bundesliga")

        assert {match.status for match in result["matches"]} == {"finished"}

    def test_all_sections_failing_returns_error(self) -> None:
        service, _ = _service("football", {})

        result = service.fetch_and_parse_league("germany/bundesliga")

        assert result["error"]
        assert result["url"] == RESULTS_URL

    def test_unsupported_sport_raises(self) -> None:
        service, _ = _service("volleyball", {})

        with pytest.raises(ValueError, match="not supported"):
            service.fetch_and_parse_league("poland/plusliga")
