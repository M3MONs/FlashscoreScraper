from bs4 import Tag

from models.odds.football_odds import FootballOdds
from models.odds_parser_row import OddsParserRow, OddsParserRowData
from models.sports import Sports
from parsers.base_odds_parser import BaseOddsParser, BookmakerInfo


class FootballCorrectScoreParser(BaseOddsParser):
    sport_type = Sports.FOOTBALL.value
    odds_type = FootballOdds.CORRECT_SCORE.value
    ODDS_COUNT = 1

    def _parse_row(self, row: Tag, bookmaker: BookmakerInfo) -> OddsParserRow | None:
        total = self._extract_value(row)
        odds_values = self._extract_odds(row)

        if len(odds_values) is not self.ODDS_COUNT:
            return None

        odds_values = [
            OddsParserRowData(value=total, type="1", odds=odds_values[0]),
        ]

        return self._generate_result(bookmaker, odds_values)
