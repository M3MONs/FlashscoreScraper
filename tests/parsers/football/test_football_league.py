from pathlib import Path

import pytest

from league.football_league_parser import FootballLeagueParser
from models.league_match import LeagueMatch

FIXTURES_DIR = Path(__file__).parent.parent.parent / "fixtures" / "football"


def _parse(name: str) -> list[LeagueMatch]:
    try:
        html = (FIXTURES_DIR / name).read_text(encoding="utf-8")
    except FileNotFoundError:
        pytest.fail(f"Fixture file not found: {FIXTURES_DIR / name}")
    return FootballLeagueParser().parse(html)


@pytest.fixture(scope="module")
def results() -> list[LeagueMatch]:
    return _parse("league_results.html")


@pytest.fixture(scope="module")
def fixtures() -> list[LeagueMatch]:
    return _parse("league_fixtures.html")


class TestFootballLeagueResults:
    def test_returns_finished_matches_with_scores(self, results: list[LeagueMatch]) -> None:
        assert len(results) > 0
        for match in results:
            assert match.status == "finished"
            assert isinstance(match.score_home, int)
            assert isinstance(match.score_away, int)

    def test_matches_have_event_url_teams_and_date(self, results: list[LeagueMatch]) -> None:
        for match in results:
            assert match.event_url.startswith("https://www.flashscore.com/match/football/")
            assert "mid=" in match.event_url
            assert match.home and match.away and match.date

    def test_matches_have_round(self, results: list[LeagueMatch]) -> None:
        assert all(match.round and match.round.startswith("Round") for match in results)


class TestFootballLeagueFixtures:
    def test_returns_scheduled_matches_without_scores(self, fixtures: list[LeagueMatch]) -> None:
        assert len(fixtures) > 0
        for match in fixtures:
            assert match.status == "scheduled"
            assert match.score_home is None
            assert match.score_away is None
            assert match.event_url.startswith("https://www.flashscore.com/match/football/")
