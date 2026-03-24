from dataclasses import dataclass
from bs4 import Tag
from models.odds.football_odds import FootballOdds
from parsers.base_odds_parser import BaseOddsParser, BookmakerInfo
from utils.detect_sport import Sports


@dataclass
class OverUnderParserResult:
    bookmaker: str
    bookmaker_link: str | None
    total: str
    odds_over: str
    odds_under: str


class FootballOverUnderParser(BaseOddsParser):
    sport_type = Sports.FOOTBALL.value
    odds_type = FootballOdds.OVER_UNDER.value
    ODDS_COUNT = 2

    def _parse_row(self, row: Tag, bookmaker: BookmakerInfo) -> OverUnderParserResult | None:
        total = self._extract_total(row)
        odds_values = self._extract_odds(row)

        if len(odds_values) is not self.ODDS_COUNT:
            return None

        return OverUnderParserResult(
            bookmaker=bookmaker.name,
            bookmaker_link=bookmaker.link,
            total=total,
            odds_over=odds_values[0],
            odds_under=odds_values[1],
        )

    @staticmethod
    def _extract_total(row: Tag) -> str:
        total_span = row.find("span", {"data-testid": "wcl-oddsValue"})
        return total_span.get_text(strip=True) if total_span else ""

    @staticmethod
    def _extract_odds(row: Tag) -> list[str]:
        return [span.get_text(strip=True) for span in row.select("a.oddsCell__odd span")]
