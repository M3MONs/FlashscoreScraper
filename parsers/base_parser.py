from abc import ABC, abstractmethod
from typing import Any, Dict
import logging

from bs4 import BeautifulSoup


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
    
    def _parse_text_element(self, soup: BeautifulSoup, class_name: str, html_tag: str = "div", default_value: str = "Unknown") -> str:
        element = soup.find(html_tag, class_=class_name)
        if element:
            return element.get_text(strip=True)
        else:
            self.logger.warning(f"Element with class '{class_name}' not found")
            return default_value
