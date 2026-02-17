from typing import Dict, Any
from parsers.base_parser import BaseParser
from parsers.parser_factory import register_parser


@register_parser("football")
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
