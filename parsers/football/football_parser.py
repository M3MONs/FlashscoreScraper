from bs4 import BeautifulSoup
from typing import Dict, Any, Sequence
from models.base_event_info import BaseEventInfo
from models.odds_filter import OddsFilter
from parsers.base_odds_parser import BaseOddsParser
from models.odds_parser_result import OddsParserResult
from parsers.base_parser import BaseParser
from parsers.football.football_event_info_parser import FootballEventInfoParser
from parsers.football.football_event_parser import FootballEventParser
from utils.detect_sport import Sports


class FootballParser(BaseParser, sport_type=Sports.FOOTBALL.value):
    def _parse_event(self, url: str, data: Any) -> Dict[str, Any]:
        self.logger.debug(f"Parsing football event from URL: {url}")
        soup = BeautifulSoup(data, "html.parser")
        event_data = FootballEventParser.parse_event(soup)
        return event_data.__dict__ if event_data else {}

    def _detect_available_event_info_types(self, data: Any) -> Sequence[BaseEventInfo]:
        soup = BeautifulSoup(data, "html.parser")
        return FootballEventInfoParser.detect_available_types(soup)

    def _parse_event_info(self, url: str, data: Any, info_type: str) -> Dict[str, Any]:
        self.logger.debug(f"Parsing football event info from URL: {url}, type: {info_type}")
        soup = BeautifulSoup(data, "html.parser")
        event_info_data = FootballEventInfoParser.parse_event_info(soup, info_type)
        return event_info_data.__dict__ if event_info_data else {}

    def _parse_odds(self, url: str, data: Any, odds_type: str, odds_filter: OddsFilter | None = None) -> OddsParserResult:
        self.logger.debug(f"Parsing football odds from URL: {url}")
        parser = BaseOddsParser.create(Sports.FOOTBALL.value, odds_type)

        if parser is None:
            self.logger.warning(f"No parser implemented for odds type: '{odds_type}'")
            return OddsParserResult(odds_type=odds_type, data=None, error=f"No parser implemented for odds type: '{odds_type}'")

        return OddsParserResult(odds_type=odds_type, data=parser.parse(url, data, odds_filter), error=None)
