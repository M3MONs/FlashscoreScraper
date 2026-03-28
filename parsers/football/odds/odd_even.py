from bs4 import Tag
from models.odds.football_odds import FootballOdds
from models.odds_parser_row import OddsParserRow, OddsParserRowData
from parsers.base_odds_parser import BaseOddsParser, BookmakerInfo
from utils.detect_sport import Sports


class FootballOddEvenParser(BaseOddsParser):
    sport_type = Sports.FOOTBALL.value
    odds_type = FootballOdds.ODD_EVEN.value
    ODDS_COUNT = 2

    def _parse_row(self, row: Tag, bookmaker: BookmakerInfo) -> OddsParserRow | None:
        odds_values = self._extract_odds(row)

        if len(odds_values) is not self.ODDS_COUNT:
            return None

        odds_values = [
            OddsParserRowData(value="odd", type="odd", odds=odds_values[0]),
            OddsParserRowData(value="even", type="even", odds=odds_values[1]),
        ]

        return self._generate_result(bookmaker, odds_values)
