from dataclasses import dataclass
from parsers.base_odds_parser import BaseOddsParser, BookmakerInfo
from bs4 import Tag
from utils.detect_sport import Sports
from models.odds.football_odds import FootballOdds


@dataclass
class FootballAsianHandicapParserResult:
    bookmaker: str
    bookmaker_link: str | None
    handicap: str
    odds_1: str
    odds_2: str


class AsianHandicapParser(BaseOddsParser):
    sport_type = Sports.FOOTBALL.value
    odds_type = FootballOdds.ASIAN_HANDICAP.value
    ODDS_COUNT = 2

    def _parse_row(self, row: Tag, bookmaker: BookmakerInfo) -> FootballAsianHandicapParserResult | None:
        odds_values = self._extract_odds(row)

        if len(odds_values) is not self.ODDS_COUNT:
            return None

        return FootballAsianHandicapParserResult(
            bookmaker=bookmaker.name,
            bookmaker_link=bookmaker.link,
            handicap=self._extract_value(row),
            odds_1=odds_values[0],
            odds_2=odds_values[1],
        )
