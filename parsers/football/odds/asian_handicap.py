from models.odds_parser_row import OddsParserRow, OddsParserRowData
from parsers.base_odds_parser import BaseOddsParser, BookmakerInfo
from bs4 import Tag
from utils.detect_sport import Sports
from models.odds.football_odds import FootballOdds


class AsianHandicapParser(BaseOddsParser):
    sport_type = Sports.FOOTBALL.value
    odds_type = FootballOdds.ASIAN_HANDICAP.value
    ODDS_COUNT = 2

    def _parse_row(self, row: Tag, bookmaker: BookmakerInfo) -> OddsParserRow | None:
        odds_values = self._extract_odds(row)

        if len(odds_values) is not self.ODDS_COUNT:
            return None

        odds_values = [
            OddsParserRowData(value=self._extract_value(row), type="handicap", odds=odds_values[0]),
            OddsParserRowData(value=self._extract_value(row), type="handicap", odds=odds_values[1]),
        ]

        return self._generate_result(bookmaker, odds_values)
