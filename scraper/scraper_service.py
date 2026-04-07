from typing import Dict, Any, Sequence
from models.base_event_info import BaseEventInfo
from models.fetch_odds_response import FetchOddsResponse
from models.odds_filter import OddsFilter
from models.odds_result import OddsResult
from engines.base_engine import BaseEngine
from models.odds.odds_factory import get_odds_enum
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

    def _resolve_event_url(self, event_url: str | None) -> str:
        """Determines the event URL to use."""
        url = event_url or self._event_url
        if not url:
            raise ValueError("event_url is required")
        return url

    def _fetch_page(self, url: str) -> str:
        """Fetches the page content for the given URL."""
        try:
            return self.engine.get_page(url)
        except Exception as e:
            self.logger.error(f"Failed to fetch page {url}: {e}", exc_info=True)
            raise

    def _fetch_pages(self, urls: Dict[str, str]) -> Dict[str, str]:
        """Fetches multiple pages given a dictionary of URLs."""
        try:
            return self.engine.get_pages(urls)
        except Exception as e:
            self.logger.error(f"Failed to fetch pages: {e}", exc_info=True)
            raise

    def _resolve_event_info_types(self, page_content: str) -> Sequence[BaseEventInfo]:
        """Detects available event info types from the page content."""
        try:
            types = self.parser.detect_available_event_info_types(page_content)
            if not types:
                self.logger.warning("No event info types detected.")
            return types
        except Exception as e:
            self.logger.error(f"Failed to detect event info types: {e}", exc_info=True)
            return []

    def fetch_and_parse_odds(self, event_url: str | None = None, odds_filter: OddsFilter | None = None) -> FetchOddsResponse:
        """Fetches the odds pages and parses the odds data for the specified event URL and odds filter."""
        url = self._resolve_event_url(event_url)
        odds_filter = odds_filter or OddsFilter()
        odds_urls = self._get_odds_urls_safely(url, odds_filter.odds)
        fetched_odds = self._fetch_odds(odds_urls, odds_filter)
        return FetchOddsResponse(event_url=url, odds=fetched_odds)

    def fetch_and_parse_event(self, event_url: str | None = None) -> Dict[str, Any]:
        """Fetches the event page and parses the main event data."""
        return self._fetch_and_parse_generic(event_url, self.parser.parse_event)

    def fetch_and_parse_event_info(self, event_url: str | None = None) -> Dict[str, Any]:
        """Fetches the event page, detects available event info types, and parses each type of event info."""
        url = self._resolve_event_url(event_url)
        page_content = self._fetch_page(url)
        available_types = self._resolve_event_info_types(page_content)

        if not available_types:
            return {}

        return self._fetch_and_parse_info_types(url, available_types)

    def _fetch_and_parse_generic(self, event_url: str | None, parse_func) -> Dict[str, Any]:
        """Common method for fetching and parsing with error handling"""
        url = self._resolve_event_url(event_url)

        try:
            page_content = self._fetch_page(url)
            return parse_func(url, page_content)
        except Exception as e:
            self.logger.error(f"Failed to fetch and parse data from {url}: {e}", exc_info=True)
            return {"error": str(e), "url": url}

    def _get_odds_urls_safely(self, event_url: str, odds: list[str]) -> Dict[str, str]:
        """Securely get odds URLs, handling any exceptions that may occur."""
        try:
            all_odds = list(get_odds_enum(self.parser.sport_type))
            filtered_odds = [o for o in all_odds if o.value in set(odds)] if odds else all_odds

            if not filtered_odds:
                self.logger.warning(f"No valid odds types found for filter: {odds}")
                return {}

            return {odd_type.value: FlashscoreUrlBuilder.build_odds_url(event_url, odd_type.value.lower()) for odd_type in filtered_odds}
        except Exception as e:
            self.logger.error(f"Failed to get odds URLs for {event_url}: {e}", exc_info=True)
            return {}

    def _fetch_odds(self, odds_urls: Dict[str, str], odds_filter: OddsFilter) -> list[OddsResult]:
        """Fetch odds for each odds type, handling exceptions for each individual fetch."""
        pages = self._fetch_pages(odds_urls)
        return [self._parse_single_odds(odds_type, odds_url, pages.get(odds_type, ""), odds_filter) for odds_type, odds_url in odds_urls.items()]

    def _parse_single_odds(self, odds_type: str, odds_url: str, page_content: str, odds_filter: OddsFilter) -> OddsResult:
        """Parse odds from already-fetched page content."""
        try:
            if not page_content:
                return OddsResult(url=odds_url, odd_type=odds_type, data=None, error="Empty page content")

            parsed_odds = self.parser.parse_odds(odds_url, page_content, odds_type, odds_filter)

            if parsed_odds.error:
                return OddsResult(url=odds_url, odd_type=odds_type, data=None, error=parsed_odds.error)

            return OddsResult(url=odds_url, odd_type=odds_type, data=parsed_odds.data, error=None)
        except Exception as e:
            error_msg = f"Failed to parse odds from {odds_url}: {e}"
            self.logger.error(error_msg, exc_info=True)
            return OddsResult(url=odds_url, odd_type=odds_type, data=None, error=str(e))

    def _fetch_and_parse_info_types(self, base_url: str, available_types: Sequence[BaseEventInfo]) -> Dict[str, Any]:
        typed_urls: Dict[str, str] = {
            info_type.tab_label: FlashscoreUrlBuilder.build_event_info_url(base_url, info_type.url_path) for info_type in available_types
        }
        wait_for_selectors: Dict[str, str | None] = {
            info_type.tab_label: info_type.wait_for_selector for info_type in available_types
        }
        pages = self.engine.get_pages(typed_urls, wait_for_selectors)

        return {info_type.tab_label: self._parse_single_info_type(info_type.tab_label, typed_urls, pages) for info_type in available_types}

    def _parse_single_info_type(self, key: str, typed_urls: Dict[str, str], pages: Dict[str, str]) -> Any:
        try:
            return self.parser.parse_event_info(typed_urls[key], pages.get(key, ""), key)
        except Exception as e:
            self.logger.error("Failed to parse event info '%s': %s", key, e, exc_info=True)
            raise
