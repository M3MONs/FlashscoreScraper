from typing import Callable, Dict, Any
from odds.football_odds import FootballOdds
from parsers.base_parser import BaseParser
from parsers.parser_factory import register_parser
from utils.detect_sport import Sport


_odds_parsers: Dict[str, Callable] = {}


def register_odds_parser(odds_type: str) -> Callable[..., Callable[..., Any]]:
    def decorator(func: Callable) -> Callable[..., Any]:
        _odds_parsers[odds_type] = func
        return func

    return decorator


@register_parser(Sport.FOOTBALL.value)
class FootballParser(BaseParser):
    def __init__(self) -> None:
        super().__init__()

    def parse_event(self, url: str, data: Any) -> Dict[str, Any]:
        self.logger.debug(f"Parsing football event from URL: {url}")
        return {"event": "football_event_data"}

    def parse_event_info(self, url: str, data: Any) -> Dict[str, Any]:
        self.logger.debug(f"Parsing football event info from URL: {url}")
        return {"event_info": "football_event_info_data"}

    def parse_odds(self, url: str, data: Any, odds_type: str) -> Dict[str, Any]:
        self.logger.debug(f"Parsing football odds from URL: {url}")
        if odds_type in _odds_parsers:
            return _odds_parsers[odds_type](self, url, data)
        else:
            self.logger.error(f"Unsupported odds type: {odds_type}")
            return {"error": f"Unsupported odds type: {odds_type}"}

    @register_odds_parser(FootballOdds.ONE_X_TWO.value)
    def _parse_1x2_odds(self, url: str, data: Any) -> Dict[str, Any]:
        self.logger.debug("Parsing 1x2 odds")
        return {"odds_type": "1x2", "data": "parsed_1x2_data"}
