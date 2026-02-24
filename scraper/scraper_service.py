from typing import Dict, Any
from models import OddsResult, FetchOddsResponse
from engines.base_engine import BaseEngine
from odds.odds_factory import get_odds_enum
from parsers.base_parser import BaseParser
import logging

from utils.url_builder import FlashscoreUrlBuilder


class ScraperService:
    def __init__(self, engine: BaseEngine, parser: BaseParser) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
        self.engine = engine
        self.parser = parser
        self._event_url = None

    @property
    def event_url(self) -> str | None:
        return self._event_url

    @event_url.setter
    def event_url(self, url: str) -> None:
        if not url:
            raise ValueError("event_url cannot be empty")
        self._event_url = url

    def fetch_and_parse_odds(self, event_url: str | None = None) -> FetchOddsResponse:
        url = event_url or self._event_url

        if not url:
            raise ValueError("event_url is required")

        odds_urls = self._get_odds_urls_safely(url)

        if not odds_urls:
            self.logger.warning(f"No odds URLs found for event: {url}")

        odds_types = self._fetch_odds_types(odds_urls)

        return FetchOddsResponse(event_url=url, odds_types=odds_types)

    def fetch_and_parse_event(self, event_url: str | None = None) -> Dict[str, Any]:
        return self._fetch_and_parse_generic(event_url, self.parser.parse_event)

    def fetch_and_parse_event_info(self, event_url: str | None = None) -> Dict[str, Any]:
        return self._fetch_and_parse_generic(event_url, self.parser.parse_event_info)

    def _fetch_and_parse_generic(self, event_url: str | None, parse_func) -> Dict[str, Any]:
        """Common method for fetching and parsing with error handling"""
        url = event_url or self._event_url

        if not url:
            raise ValueError("event_url is required")

        try:
            page_content = self.engine.get_page(url)
            return parse_func(url, page_content)
        except Exception as e:
            self.logger.error(f"Failed to fetch and parse data from {url}: {e}", exc_info=True)
            return {"error": str(e), "url": url}

    def _get_odds_urls_safely(self, event_url: str) -> Dict[str, str]:
        """Securely get odds URLs, handling any exceptions that may occur."""
        try:
            odds_types = get_odds_enum(self.parser.sport_type)
            return {odd_type.value: FlashscoreUrlBuilder.build_odds_url(event_url, odd_type.value.lower()) for odd_type in odds_types}
        except Exception as e:
            self.logger.error(f"Failed to get odds URLs for {event_url}: {e}", exc_info=True)
            return {}

    def _fetch_odds_types(self, odds_urls: Dict[str, str]) -> Dict[str, OddsResult]:
        """Fetch odds for each odds type, handling exceptions for each individual fetch."""
        return {odds_type: self._fetch_single_odds(odds_url, odds_type) for odds_type, odds_url in odds_urls.items()}

    def _fetch_single_odds(self, odds_url: str, odds_type: str) -> OddsResult:
        """Fetch odds from a single URL, handling any exceptions that may occur."""
        try:
            page_content = self.engine.get_page(odds_url)
            parsed_odds = self.parser.parse_odds(odds_url, page_content, odds_type)
            return OddsResult(url=odds_url, data=parsed_odds)
        except Exception as e:
            error_msg = f"Failed to fetch odds from {odds_url}: {e}"
            self.logger.error(error_msg, exc_info=True)
            return OddsResult(url=odds_url, error=str(e))
