from typing import Any, Dict

from bs4 import BeautifulSoup
from odds.football_odds import FootballOdds
from parsers.base_odds_parser import BaseOddsParser
from utils.detect_sport import Sport


class FootballOneXTwoParser(BaseOddsParser):
    sport_type = Sport.FOOTBALL.value
    odds_type = FootballOdds.ONE_X_TWO.value

    def parse(self, url: str, data: Any) -> Dict[str, Any]:
        soup = BeautifulSoup(data, "html.parser")

        wrapper = soup.find("div", class_="oddsTab__tableWrapper")

        if not wrapper:
            return {"odds_type": "1x2", "data": None, "error": "wrapper_not_found"}

        results = []

        rows = wrapper.select(".ui-table__row")

        for row in rows:
            img_tag = row.select_one(".oddsCell__bookmakerPart img")
            bookmaker = img_tag.get("alt") if img_tag else "Unknown"
            link_tag = row.select_one('.wcl-bookmakerLogo_4IUU0 a')
            bookmaker_link = link_tag.get('href') if link_tag else None

            odds_spans = row.select("a.oddsCell__odd span")

            odds_values = [span.get_text(strip=True) for span in odds_spans]

            if len(odds_values) >= 3:
                results.append({"bookmaker": bookmaker, "bookmaker_link": bookmaker_link, "1": odds_values[0], "X": odds_values[1], "2": odds_values[2]})

        return {"odds_type": "1x2", "data": results, "error": None}
