from bs4 import Tag

from models.odds.football_odds import FootballOdds
from models.odds_parser_row import OddsParserRow, OddsParserRowData
from models.sports import Sports
from parsers.base_odds_parser import BaseOddsParser, BookmakerInfo


class FootballDoubleChanceParser(BaseOddsParser):
    sport_type = Sports.FOOTBALL.value
    odds_type = FootballOdds.DOUBLE_CHANCE.value
    ODDS_COUNT = 3

    def _parse_row(self, row: Tag, bookmaker: BookmakerInfo) -> OddsParserRow | None:
        odds_values = self._extract_odds(row)

        if len(odds_values) is not self.ODDS_COUNT:
            return None

        odds_values = [
            OddsParserRowData(value="1x", type="1x", odds=odds_values[0]),
            OddsParserRowData(value="12", type="12", odds=odds_values[1]),
            OddsParserRowData(value="x2", type="x2", odds=odds_values[2]),
        ]

        return self._generate_result(bookmaker, odds_values)
