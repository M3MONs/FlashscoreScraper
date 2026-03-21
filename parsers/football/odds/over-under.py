from dataclasses import dataclass
from typing import Any
from bs4 import BeautifulSoup, Tag
from models.odds.football_odds import FootballOdds
from parsers.base_odds_parser import BaseOddsParser
from utils.detect_sport import Sports


@dataclass
class OverUnderParserResult:
    bookmaker: str
    bookmaker_link: str | None
    total: str
    odds_over: str
    odds_under: str


MIN_ODDS_COUNT = 2


class FootballOverUnderParser(BaseOddsParser):
    sport_type = Sports.FOOTBALL.value
    odds_type = FootballOdds.OVER_UNDER.value

    def parse(self, url: str, data: Any) -> list[OverUnderParserResult]:
        soup = BeautifulSoup(data, "html.parser")
        wrapper = soup.find("div", class_="oddsTab__tableWrapper")

        if not wrapper:
            return []

        rows = wrapper.select(".ui-table__row")
        results = [self._parse_row(row) for row in rows]
        results = [r for r in results if r is not None]

        return results

    def _parse_row(self, row: Tag) -> OverUnderParserResult | None:
        try:
            total = self._extract_total(row)
            odds_values = self._extract_odds(row)

            if len(odds_values) < MIN_ODDS_COUNT:
                return None

            return OverUnderParserResult(
                bookmaker=self._extract_bookmaker_name(row),
                bookmaker_link=self._extract_bookmaker_link(row),
                total=total,
                odds_over=odds_values[0],
                odds_under=odds_values[1],
            )
        except Exception as e:
            self.logger.error(f"Error parsing row: {e}")
            return None

    @staticmethod
    def _extract_total(row: Tag) -> str:
        total_span = row.find("span", {"data-testid": "wcl-oddsValue"})
        return total_span.get_text(strip=True) if total_span else ""

    @staticmethod
    def _extract_odds(row: Tag) -> list[str]:
        return [span.get_text(strip=True) for span in row.select("a.oddsCell__odd span")]
