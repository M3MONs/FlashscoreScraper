from abc import ABC, abstractmethod
from typing import Any, Dict
import logging


class BaseParser(ABC):
    def __init__(self) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def parse_event(self, url, data) -> Dict[str, Any]:
        raise NotImplementedError("Subclasses must implement the parse_event method.")

    @abstractmethod
    def parse_event_info(self, url, data) -> Dict[str, Any]:
        raise NotImplementedError("Subclasses must implement the parse_event_info method.")

    @abstractmethod
    def parse_odds(self, url, data) -> Dict[str, Any]:
        raise NotImplementedError("Subclasses must implement the parse_odds method.")

    @abstractmethod
    def get_odds_urls(self, event_url: str) -> Dict[str, str]:
        raise NotImplementedError("Subclasses must implement the get_odds_urls method.")
