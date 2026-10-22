from pathlib import Path

import pytest

from stats.football_stats_parser import FootballStatsParser

FIXTURE_PATH = Path(__file__).parent.parent.parent / "fixtures" / "football" / "stats.html"


@pytest.fixture(scope="module")
def stats_result() -> dict:
    try:
        html = FIXTURE_PATH.read_text(encoding="utf-8")
    except FileNotFoundError:
        pytest.fail(f"Fixture file not found: {FIXTURE_PATH}")
    return FootballStatsParser().parse(html)


class TestFootballStatsParser:
    def test_returns_sections(self, stats_result: dict) -> None:
        assert len(stats_result) > 0
        assert "Top stats" in stats_result

    def test_rows_have_category_and_values(self, stats_result: dict) -> None:
        for section, rows in stats_result.items():
            assert len(rows) > 0, f"Section '{section}' has no rows"
            for row in rows:
                assert row["category"]
                assert row["home"]
                assert row["away"]

    def test_ball_possession_present(self, stats_result: dict) -> None:
        categories = {row["category"] for row in stats_result["Top stats"]}
        assert "Ball possession" in categories

    def test_empty_page_raises(self) -> None:
        with pytest.raises(ValueError):
            FootballStatsParser().parse("<html><body></body></html>")

    def test_malformed_row_is_skipped(self) -> None:
        html = """
        <div data-testid="statGroup">
          <div data-testid="wcl-headerSection-text">Shots</div>
          <div data-testid="wcl-statistics"><div><div>1</div><div>Broken</div></div></div>
          <div data-testid="wcl-statistics"><div><div>5</div><div>Total shots</div><div>3</div></div></div>
        </div>
        """
        result = FootballStatsParser().parse(html)
        assert result == {"Shots": [{"category": "Total shots", "home": "5", "away": "3"}]}
