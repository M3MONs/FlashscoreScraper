from abc import ABC, abstractmethod
from typing import Any, Dict
import logging


class BaseParser(ABC):
    sport_type: str

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

    def parse_event_info(self, url: str, data: Any) -> Dict[str, Any]:
        self.logger.debug(f"Parsing event info from URL: {url}")
        result = self._parse_event_info(url, data)
        self.logger.debug(f"Finished parsing event info from URL: {url}")
        return result

    @abstractmethod
    def _parse_event_info(self, url: str, data: Any) -> Dict[str, Any]:
        raise NotImplementedError("Subclasses must implement the _parse_event_info method.")

    def parse_odds(self, url: str, data: Any, odds_type: str) -> Dict[str, Any]:
        self.logger.debug(f"Parsing odds from URL: {url} with odds type: {odds_type}")
        result = self._parse_odds(url, data, odds_type)
        self.logger.debug(f"Finished parsing odds from URL: {url} with odds type: {odds_type}")
        return result

    @abstractmethod
    def _parse_odds(self, url: str, data: Any, odds_type: str) -> Dict[str, Any]:
        raise NotImplementedError("Subclasses must implement the _parse_odds method.")
