from dataclasses import dataclass
from bs4 import Tag
from models.odds.football_odds import FootballOdds
from parsers.base_odds_parser import BaseOddsParser, BookmakerInfo
from utils.detect_sport import Sports


@dataclass
class FootballOneXTwoParserResult:
    bookmaker: str
    bookmaker_link: str | None
    odds_1: str
    odds_X: str
    odds_2: str


class FootballOneXTwoParser(BaseOddsParser):
    sport_type = Sports.FOOTBALL.value
    odds_type = FootballOdds.ONE_X_TWO.value
    ODDS_COUNT = 3

    def _parse_row(self, row: Tag, bookmaker: BookmakerInfo) -> FootballOneXTwoParserResult | None:
        odds_values = self._extract_odds(row)

        if len(odds_values) is not self.ODDS_COUNT:
            return None

        return FootballOneXTwoParserResult(
            bookmaker=bookmaker.name,
            bookmaker_link=bookmaker.link,
            odds_1=odds_values[0],
            odds_X=odds_values[1],
            odds_2=odds_values[2],
        )

    @staticmethod
    def _extract_odds(row: Tag) -> list[str]:
        return [span.get_text(strip=True) for span in row.select("a.oddsCell__odd span")]
