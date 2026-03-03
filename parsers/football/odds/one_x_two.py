from typing import Any, Dict

from bs4 import BeautifulSoup, Tag
from odds.football_odds import FootballOdds
from parsers.base_odds_parser import BaseOddsParser
from utils.detect_sport import Sport

MIN_ODDS_COUNT = 3

class FootballOneXTwoParser(BaseOddsParser):
    sport_type = Sport.FOOTBALL.value
    odds_type = FootballOdds.ONE_X_TWO.value

    def parse(self, url: str, data: Any) -> Dict[str, Any]:
        soup = BeautifulSoup(data, "html.parser")
        wrapper = soup.find("div", class_="oddsTab__tableWrapper")

        if not wrapper:
            return self._error_response("Odds table wrapper not found")

        rows = wrapper.select(".ui-table__row")
        results = [self._parse_row(row) for row in rows]
        results = [r for r in results if r is not None]

        return {"odds_type": "1x2", "data": results, "error": None}
    
    def _parse_row(self, row: Tag) -> dict | None:
        odds_values = self._extract_odds(row)
        if len(odds_values) < MIN_ODDS_COUNT:
            return None

        return {
            "bookmaker": self._extract_bookmaker_name(row),
            "bookmaker_link": self._extract_bookmaker_link(row),
            "1": odds_values[0],
            "X": odds_values[1],
            "2": odds_values[2],
        }
    
    @staticmethod
    def _error_response(message: str) -> Dict[str, Any]:
        return {"odds_type": "1x2", "data": None, "error": message}
    
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

    
