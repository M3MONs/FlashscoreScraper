from typing import Dict, Any
from parsers.base_parser import BaseParser


class FootballParser(BaseParser):
    def __init__(self) -> None:
        super().__init__()

    def parse_event(self, url, data) -> Dict[str, Any]:
        self.logger.debug(f"Parsing football event from URL: {url}")
        return {"event": "football_event_data"}

    def parse_event_info(self, url, data) -> Dict[str, Any]:
        self.logger.debug(f"Parsing football event info from URL: {url}")
        return {"event_info": "football_event_info_data"}

    def parse_odds(self, url, data) -> Dict[str, Any]:
        self.logger.debug(f"Parsing football odds from URL: {url}")
        return {"odds": "football_odds_data"}
    
    def get_odds_urls(self, event_url: str) -> Dict[str, str]:
        self.logger.debug(f"Getting football odds URLs from event URL: {event_url}")
        return {
            "1X2": f"{event_url}/odds/1x2",
            "Over/Under": f"{event_url}/odds/over-under",
            "Handicap": f"{event_url}/odds/handicap"
        }
