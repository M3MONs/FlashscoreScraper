from typing import Any, Dict
from odds.football_odds import FootballOdds
from parsers.base_odds_parser import BaseOddsParser
from utils.detect_sport import Sport


class FootballOneXTwoParser(BaseOddsParser):
    sport_type = Sport.FOOTBALL.value
    odds_type = FootballOdds.ONE_X_TWO.value

    def parse(self, url: str, data: Any) -> Dict[str, Any]:
        return {
            "odds_type": "1x2",
            "data": "parsed_1x2_data",
            "error": None
        }