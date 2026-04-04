from abc import ABC, abstractmethod
from typing import Any, Dict, Sequence, Type
import logging

from models.base_event_info import BaseEventInfo
from models.odds_filter import OddsFilter
from models.parse_text_element_params import ParseTextElementParams
from models.odds_parser_result import OddsParserResult


class BaseParser(ABC):
    _registry: Dict[str, Type["BaseParser"]] = {}
    sport_type: str

    def __init_subclass__(cls, sport_type: str | None = None, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        if sport_type:
            cls.sport_type = sport_type
            BaseParser._registry[sport_type] = cls

    @classmethod
    def create(cls, sport_type: str) -> "BaseParser":
        if sport_type not in cls._registry:
            raise ValueError(f"Unsupported sport type: {sport_type}")
        return cls._registry[sport_type]()

    def __init__(self) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)

    def parse_event(self, url: str, data: Any) -> Dict[str, Any]:
        self.logger.debug(f"Parsing event from URL: {url}")
        result = self._parse_event(url, data)
        self.logger.debug(f"Finished parsing event from URL: {url}")
        return result

    @abstractmethod
    def _parse_event(self, url: str, data: Any) -> Dict[str, Any]:
        raise NotImplementedError("Subclasses must implement the _parse_event method.")

    def detect_available_event_info_types(self, data: Any) -> Sequence[BaseEventInfo]:
        self.logger.debug("Detecting available event info types")
        result = self._detect_available_event_info_types(data)
        self.logger.debug(f"Detected event info types: {[t.value for t in result]}")
        return result

    @abstractmethod
    def _detect_available_event_info_types(self, data: Any) -> Sequence[BaseEventInfo]:
        raise NotImplementedError("Subclasses must implement the _detect_available_event_info_types method.")

    def parse_event_info(self, url: str, data: Any, info_type: str) -> Dict[str, Any]:
        self.logger.debug(f"Parsing event info from URL: {url}, type: {info_type}")
        result = self._parse_event_info(url, data, info_type)
        self.logger.debug(f"Finished parsing event info from URL: {url}, type: {info_type}")
        return result

    @abstractmethod
    def _parse_event_info(self, url: str, data: Any, info_type: str) -> Dict[str, Any]:
        raise NotImplementedError("Subclasses must implement the _parse_event_info method.")

    def parse_odds(self, url: str, data: Any, odds_type: str, odds_filter: OddsFilter | None = None) -> OddsParserResult:
        self.logger.debug(f"Parsing odds from URL: {url} with odds type: {odds_type}")
        result = self._parse_odds(url, data, odds_type, odds_filter)
        self.logger.debug(f"Finished parsing odds from URL: {url} with odds type: {odds_type}")
        return result

    @abstractmethod
    def _parse_odds(self, url: str, data: Any, odds_type: str, odds_filter: OddsFilter | None = None) -> OddsParserResult:
        raise NotImplementedError("Subclasses must implement the _parse_odds method.")

    @staticmethod
    def parse_text_element(params: ParseTextElementParams) -> str:
        element = params.soup.find(params.html_tag, class_=params.class_name)
        if element:
            return element.get_text(strip=True)
        else:
            logging.warning(f"Element with class '{params.class_name}' not found")
            return params.default_value
