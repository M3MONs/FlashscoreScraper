from dataclasses import dataclass
from typing import Any
from parsers.base_odds_parser import BaseOddsParser
from bs4 import BeautifulSoup, Tag
from utils.detect_sport import Sport
from odds.football_odds import FootballOdds


@dataclass
class FootballAsianHandicapParserResult:
    bookmaker: str
    bookmaker_link: str | None
    handicap: str
    odds_1: str
    odds_2: str


MIN_ODDS_COUNT = 2


class AsianHandicapParser(BaseOddsParser):
    sport_type = Sport.FOOTBALL.value
    odds_type = FootballOdds.ASIAN_HANDICAP.value

    def parse(self, url: str, data: str) -> list[FootballAsianHandicapParserResult]:
        soup = BeautifulSoup(data, "html.parser")
        wrapper = soup.find("div", class_="oddsTab__tableWrapper")

        if not wrapper:
            return []

        rows = wrapper.select(".ui-table__row")
        results = [self._parse_row(row) for row in rows]
        results = [r for r in results if r is not None]

        return results

    def _parse_row(self, row: Tag) -> Any | None:
        try:
            odds_values = self._extract_odds(row)

            if len(odds_values) < MIN_ODDS_COUNT:
                return None

            return FootballAsianHandicapParserResult(
                bookmaker=self._extract_bookmaker_name(row),
                bookmaker_link=self._extract_bookmaker_link(row),
                handicap=self._extract_handicap(row),
                odds_1=odds_values[0],
                odds_2=odds_values[1],
            )
        except Exception as e:
            self.logger.error(f"Error parsing row: {e}")
            return None

    @staticmethod
    def _extract_handicap(row: Tag) -> str:
        handicap_span = row.find("span", {"data-testid": "wcl-oddsValue"})
        return handicap_span.get_text(strip=True) if handicap_span else ""

    @staticmethod
    def _extract_odds(row: Tag) -> list[str]:
        return [span.get_text(strip=True) for span in row.select("a.oddsCell__odd span")]
