import logging
from collections.abc import Sequence
from typing import Any, Self

from engines.base_engine import BaseEngine
from models.base_event_info import BaseEventInfo
from models.fetch_odds_response import FetchOddsResponse
from models.odds.odds_factory import get_odds_enum
from models.odds_filter import OddsFilter
from models.odds_result import OddsResult
from parsers.base_parser import BaseParser
from stats import get_stats_parser
from stats.base_stats_parser import BaseStatsParser
from utils.url_builder import FlashscoreUrlBuilder


class ScraperService:
    def __init__(self, engine: BaseEngine, parser: BaseParser) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
        self.engine = engine
        self.parser = parser
        self._event_url = None

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    def close(self) -> None:
        self.engine.close()

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

    def _fetch_pages(self, urls: dict[str, str]) -> dict[str, str]:
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

    def fetch_and_parse_event(self, event_url: str | None = None) -> dict[str, Any]:
        """Fetches the event page and parses the main event data."""
        url = self._resolve_event_url(event_url)
        event = self._fetch_and_parse_generic(url, self.parser.parse_event)
        if "error" not in event:
            event = {"event_url": url, **event}
        return event

    def fetch_and_parse_event_with_stats(self, event_url: str | None = None) -> dict[str, Any]:
        """Fetches the main event data and adds match statistics under the 'stats' key."""
        url = self._resolve_event_url(event_url)
        stats_parser = get_stats_parser(self.parser.sport_type)
        event = self.fetch_and_parse_event(url)

        if "error" not in event:
            event["stats"] = self._fetch_and_parse_stats(url, stats_parser)

        return event

    def _fetch_and_parse_stats(self, event_url: str, stats_parser: BaseStatsParser) -> dict[str, Any]:
        """Fetches and parses the stats page, raises ValueError when the event has no stats."""
        stats_url = FlashscoreUrlBuilder.build_event_info_url(event_url, stats_parser.url_path)
        try:
            page_content = self.engine.get_page(stats_url, stats_parser.wait_for_selector)
        except Exception as e:
            # Playwright times out on wait_for_selector when the event has no stats (e.g. not started yet)
            self.logger.debug(f"Failed to fetch stats page {stats_url}: {e}", exc_info=True)
            raise ValueError(f"No stats available for {event_url}") from e
        return stats_parser.parse(page_content)

    def fetch_and_parse_event_info(self, event_url: str | None = None) -> dict[str, Any]:
        """Fetches the event page, detects available event info types, and parses each type of event info."""
        url = self._resolve_event_url(event_url)
        page_content = self._fetch_page(url)
        available_types = self._resolve_event_info_types(page_content)

        if not available_types:
            return {"event_url": url}

        return {"event_url": url, **self._fetch_and_parse_info_types(url, available_types)}

    def _fetch_and_parse_generic(self, event_url: str | None, parse_func) -> dict[str, Any]:
        """Common method for fetching and parsing with error handling"""
        url = self._resolve_event_url(event_url)

        try:
            page_content = self._fetch_page(url)
            return parse_func(url, page_content)
        except Exception as e:
            self.logger.error(f"Failed to fetch and parse data from {url}: {e}", exc_info=True)
            return {"error": str(e), "url": url}

    def _get_odds_urls_safely(self, event_url: str, odds: list[str]) -> dict[str, str]:
        """Securely get odds URLs, handling any exceptions that may occur."""
        try:
            all_odds = list(get_odds_enum(self.parser.sport_type))
            filtered_odds = [o for o in all_odds if o.value in set(odds)] if odds else all_odds

            if not filtered_odds:
                self.logger.warning(f"No valid odds types found for filter: {odds}")
                return {}

            return {odd_type.value: FlashscoreUrlBuilder.build_odds_url(event_url, odd_type.value.lower()) for odd_type in filtered_odds}
        except ValueError:
            return self._discover_odds_urls(event_url, odds)
        except Exception as e:
            self.logger.error(f"Failed to get odds URLs for {event_url}: {e}", exc_info=True)
            return {}

    def _discover_odds_urls(self, event_url: str, odds: list[str]) -> dict[str, str]:
        """Fallback method to discover odds URLs by parsing the landing page when no odds enum is available."""
        if odds:
            self.logger.info(f"No odds enum for sport '{self.parser.sport_type}', using user-specified types: {odds}")
            return {ot: FlashscoreUrlBuilder.build_odds_url(event_url, ot) for ot in odds}

        try:
            landing_url = FlashscoreUrlBuilder.build_odds_url(event_url, "")
            self.logger.info(f"Discovering odds types from {landing_url}")
            page = self._fetch_page(landing_url)
            discovered = self.parser.discover_odds_types(page)

            if not discovered:
                self.logger.warning(f"No odds types discovered for sport '{self.parser.sport_type}'")
                return {}
            
            self.logger.info(f"Discovered odds types: {discovered}")
            return {ot: FlashscoreUrlBuilder.build_odds_url(event_url, ot) for ot in discovered}
        except Exception as e:
            self.logger.warning(f"Failed to discover odds types: {e}", exc_info=True)
            return {}

    def _fetch_odds(self, odds_urls: dict[str, str], odds_filter: OddsFilter) -> list[OddsResult]:
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

    def _fetch_and_parse_info_types(self, base_url: str, available_types: Sequence[BaseEventInfo]) -> dict[str, Any]:
        """Fetches and parses multiple types of event info, handling exceptions for each type."""
        typed_urls: dict[str, str] = {
            info_type.tab_label: FlashscoreUrlBuilder.build_event_info_url(base_url, info_type.url_path) for info_type in available_types
        }
        wait_for_selectors: dict[str, str | None] = {
            info_type.tab_label: info_type.wait_for_selector for info_type in available_types
        }
        pages = self.engine.get_pages(typed_urls, wait_for_selectors)

        return {info_type.tab_label: self._parse_single_info_type(info_type.tab_label, typed_urls, pages) for info_type in available_types}

    def _parse_single_info_type(self, key: str, typed_urls: dict[str, str], pages: dict[str, str]) -> Any:
        """Parse a single type of event info from the corresponding page content."""
        try:
            return self.parser.parse_event_info(typed_urls[key], pages.get(key, ""), key)
        except Exception as e:
            self.logger.error("Failed to parse event info '%s': %s", key, e, exc_info=True)
            raise
