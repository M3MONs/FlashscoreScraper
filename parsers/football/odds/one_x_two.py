from dataclasses import dataclass
from typing import Any

from bs4 import BeautifulSoup, Tag
from odds.football_odds import FootballOdds
from parsers.base_odds_parser import BaseOddsParser
from utils.detect_sport import Sport

@dataclass
class FootballOneXTwoParserResult:
    bookmaker: str
    bookmaker_link: str | None
    odds_1: str
    odds_X: str
    odds_2: str

MIN_ODDS_COUNT = 3

class FootballOneXTwoParser(BaseOddsParser):
    sport_type = Sport.FOOTBALL.value
    odds_type = FootballOdds.ONE_X_TWO.value

    def parse(self, url: str, data: Any) -> list[FootballOneXTwoParserResult]:
        soup = BeautifulSoup(data, "html.parser")
        wrapper = soup.find("div", class_="oddsTab__tableWrapper")

        if not wrapper:
            return []

        rows = wrapper.select(".ui-table__row")
        results = [self._parse_row(row) for row in rows]
        results = [r for r in results if r is not None]

        return results
    
    def _parse_row(self, row: Tag) -> FootballOneXTwoParserResult | None:
        try:
            odds_values = self._extract_odds(row)
            
            if len(odds_values) < MIN_ODDS_COUNT:
                return None

            return FootballOneXTwoParserResult(
                bookmaker=self._extract_bookmaker_name(row),
                bookmaker_link=self._extract_bookmaker_link(row),
                odds_1=odds_values[0],
                odds_X=odds_values[1],
                odds_2=odds_values[2],
            )
        except Exception as e:
            self.logger.error(f"Error parsing row: {e}")
            return None
    
    @staticmethod
    def _extract_odds(row: Tag) -> list[str]:
        return [span.get_text(strip=True) for span in row.select("a.oddsCell__odd span")]
    
    @staticmethod
    def _extract_bookmaker_name(row: Tag) -> str:
        img_tag = row.select_one(".oddsCell__bookmakerPart img")
        return str(img_tag.get("alt")) if img_tag else "Unknown"
    
    @staticmethod
    def _extract_bookmaker_link(row: Tag) -> str | None:
        link_tag = row.select_one('.wcl-bookmakerLogo_4IUU0 a')
        return str(link_tag.get('href')) if link_tag else None

    
