import pytest
from pathlib import Path
from bs4 import BeautifulSoup
from models.odds.football_odds import FootballOdds
from models.odds_parser_row import OddsParserRow
from parsers.base_odds_parser import BaseOddsParser
from soup_helpers import load_soup_from_path
from utils.detect_sport import Sports

FIXTURES_DIR = Path(__file__).parent.parent.parent / "fixtures"


def load_odds_soup(odds_type: FootballOdds) -> BeautifulSoup:
    return load_soup_from_path(FIXTURES_DIR / f"football_odds_{odds_type.value}.html")


def parse_odds(odds_type: FootballOdds) -> list[OddsParserRow]:
    parser = BaseOddsParser.create(Sports.FOOTBALL.value, odds_type.value)
    assert parser is not None
    soup = load_odds_soup(odds_type)
    return parser.parse("", str(soup))


class TestFootballOneXTwoOdds:
    ODDS_TYPE = FootballOdds.ONE_X_TWO

    def test_returns_results(self) -> None:
        rows = parse_odds(self.ODDS_TYPE)
        assert len(rows) > 0

    def test_row_has_bookmaker_info(self) -> None:
        rows = parse_odds(self.ODDS_TYPE)
        row = rows[0]
        assert row.bookmaker_name is not None
        assert len(row.bookmaker_name) > 0
        assert row.bookmaker_id is not None

    def test_row_has_three_odds(self) -> None:
        rows = parse_odds(self.ODDS_TYPE)
        for row in rows:
            assert len(row.odds_values) == 3

    def test_odds_types_are_1_x_2(self) -> None:
        rows = parse_odds(self.ODDS_TYPE)
        row = rows[0]
        types = [o.type for o in row.odds_values]
        assert types == ["1", "X", "2"]


class TestFootballOverUnderOdds:
    ODDS_TYPE = FootballOdds.OVER_UNDER

    def test_returns_results(self) -> None:
        rows = parse_odds(self.ODDS_TYPE)
        assert len(rows) > 0

    def test_row_has_two_odds(self) -> None:
        rows = parse_odds(self.ODDS_TYPE)
        for row in rows:
            assert len(row.odds_values) == 2

    def test_odds_types_are_over_under(self) -> None:
        rows = parse_odds(self.ODDS_TYPE)
        row = rows[0]
        types = [o.type for o in row.odds_values]
        assert types == ["over", "under"]

    def test_value_is_total(self) -> None:
        rows = parse_odds(self.ODDS_TYPE)
        row = rows[0]
        assert row.odds_values[0].value != ""


class TestFootballBTTSOdds:
    ODDS_TYPE = FootballOdds.BTTS

    def test_returns_results(self) -> None:
        rows = parse_odds(self.ODDS_TYPE)
        assert len(rows) > 0

    def test_row_has_two_odds(self) -> None:
        rows = parse_odds(self.ODDS_TYPE)
        for row in rows:
            assert len(row.odds_values) == 2

    def test_odds_types_are_yes_no(self) -> None:
        rows = parse_odds(self.ODDS_TYPE)
        row = rows[0]
        types = [o.type for o in row.odds_values]
        assert types == ["yes", "no"]


class TestFootballOneXTwoOddsExactValues:
    ODDS_TYPE = FootballOdds.ONE_X_TWO

    EXPECTED_BOOKMAKER_ID = "539"
    EXPECTED_BOOKMAKER_NAME = "Betclic.pl"
    EXPECTED_BOOKMAKER_LINK = "https://www.flashscore.com/bookmaker/539"
    EXPECTED_ODDS_1 = "1.72"
    EXPECTED_ODDS_X = "3.58"
    EXPECTED_ODDS_2 = "4.20"

    def test_exact_bookmaker(self) -> None:
        rows = parse_odds(self.ODDS_TYPE)
        row = next((r for r in rows if r.bookmaker_id == self.EXPECTED_BOOKMAKER_ID), None)
        assert row is not None
        assert row.bookmaker_name == self.EXPECTED_BOOKMAKER_NAME
        if row.bookmaker_link is None:
            return pytest.fail("Bookmaker link is None")
        assert row.bookmaker_link.startswith(self.EXPECTED_BOOKMAKER_LINK)

    def test_exact_odds(self) -> None:
        rows = parse_odds(self.ODDS_TYPE)
        row = next((r for r in rows if r.bookmaker_id == self.EXPECTED_BOOKMAKER_ID), None)
        assert row is not None
        assert row.odds_values[0].odds == self.EXPECTED_ODDS_1
        assert row.odds_values[1].odds == self.EXPECTED_ODDS_X
        assert row.odds_values[2].odds == self.EXPECTED_ODDS_2


class TestFootballOverUnderOddsExactValues:
    ODDS_TYPE = FootballOdds.OVER_UNDER

    EXPECTED_BOOKMAKER_ID = "539"
    EXPECTED_BOOKMAKER_NAME = "Betclic.pl"
    EXPECTED_TOTAL = "0.5"
    EXPECTED_ODDS_OVER = "1.03"
    EXPECTED_ODDS_UNDER = "14.00"

    def test_exact_bookmaker(self) -> None:
        rows = parse_odds(self.ODDS_TYPE)
        row = next((r for r in rows if r.bookmaker_id == self.EXPECTED_BOOKMAKER_ID), None)
        assert row is not None
        assert row.bookmaker_name == self.EXPECTED_BOOKMAKER_NAME

    def test_exact_odds(self) -> None:
        rows = parse_odds(self.ODDS_TYPE)
        row = next((r for r in rows if r.bookmaker_id == self.EXPECTED_BOOKMAKER_ID), None)
        assert row is not None
        assert row.odds_values[0].value == self.EXPECTED_TOTAL
        assert row.odds_values[0].odds == self.EXPECTED_ODDS_OVER
        assert row.odds_values[1].odds == self.EXPECTED_ODDS_UNDER


class TestFootballBTTSOddsExactValues:
    ODDS_TYPE = FootballOdds.BTTS

    EXPECTED_BOOKMAKER_ID = "539"
    EXPECTED_BOOKMAKER_NAME = "Betclic.pl"
    EXPECTED_ODDS_YES = "1.65"
    EXPECTED_ODDS_NO = "2.07"

    def test_exact_bookmaker(self) -> None:
        rows = parse_odds(self.ODDS_TYPE)
        row = next((r for r in rows if r.bookmaker_id == self.EXPECTED_BOOKMAKER_ID), None)
        assert row is not None
        assert row.bookmaker_name == self.EXPECTED_BOOKMAKER_NAME

    def test_exact_odds(self) -> None:
        rows = parse_odds(self.ODDS_TYPE)
        row = next((r for r in rows if r.bookmaker_id == self.EXPECTED_BOOKMAKER_ID), None)
        assert row is not None
        assert row.odds_values[0].odds == self.EXPECTED_ODDS_YES
        assert row.odds_values[1].odds == self.EXPECTED_ODDS_NO
