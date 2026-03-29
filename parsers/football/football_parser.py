from bs4 import BeautifulSoup
from typing import Dict, Any
from models.odds_filter import OddsFilter
from parsers.base_odds_parser import BaseOddsParser
from models.odds_parser_result import OddsParserResult
from parsers.base_parser import BaseParser
from parsers.football.football_event_parser import FootballEventParser
from utils.detect_sport import Sports


class FootballParser(BaseParser, sport_type=Sports.FOOTBALL.value):
    def _parse_event(self, url: str, data: Any) -> Dict[str, Any]:
        self.logger.debug(f"Parsing football event from URL: {url}")
        soup = BeautifulSoup(data, 'html.parser')
        event_data = FootballEventParser.parse_event(soup)
        return event_data.__dict__ if event_data else {}

    def _parse_event_info(self, url: str, data: Any) -> Dict[str, Any]:
        self.logger.debug(f"Parsing football event info from URL: {url}")
        return {"event_info": "football_event_info_data"}

    def _parse_odds(self, url: str, data: Any, odds_type: str, odds_filter: OddsFilter | None = None) -> OddsParserResult:
        self.logger.debug(f"Parsing football odds from URL: {url}")
        parser = BaseOddsParser.create(
            Sports.FOOTBALL.value,
            odds_type
        )
        
        if parser is None:
            self.logger.warning(f"No parser implemented for odds type: '{odds_type}'")
            return OddsParserResult(odds_type=odds_type, data=None, error=f"No parser implemented for odds type: '{odds_type}'")
        
        return OddsParserResult(odds_type=odds_type, data=parser.parse(url, data, odds_filter), error=None)
