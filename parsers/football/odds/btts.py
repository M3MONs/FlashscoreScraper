from bs4 import Tag

from models.odds.football_odds import FootballOdds
from models.odds_parser_row import OddsParserRow, OddsParserRowData
from models.sports import Sports
from parsers.base_odds_parser import BaseOddsParser, BookmakerInfo


class FootballBTTSParser(BaseOddsParser):
    sport_type = Sports.FOOTBALL.value
    odds_type = FootballOdds.BTTS.value
    ODDS_COUNT = 2

    def _parse_row(self, row: Tag, bookmaker: BookmakerInfo) -> OddsParserRow | None:
        odds_values = self._extract_odds(row)

        if len(odds_values) is not self.ODDS_COUNT:
            return None

        odds_values = [
            OddsParserRowData(value="yes", type="yes", odds=odds_values[0]),
            OddsParserRowData(value="no", type="no", odds=odds_values[1]),
        ]

        return self._generate_result(bookmaker, odds_values)
