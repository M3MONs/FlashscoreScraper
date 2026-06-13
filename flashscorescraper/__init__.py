from typing import Any, Dict

from models.fetch_odds_response import FetchOddsResponse
from models.odds_filter import OddsFilter
from scraper.scraper_factory import ScraperFactory
from utils.detect_sport import detect_sport_from_url


def _resolve_sport(event_url: str, sport: str | None) -> str:
    if sport is not None:
        return sport
    return detect_sport_from_url(event_url)


def scrape_odds(
    event_url: str,
    sport: str | None = None,
    engine: str = "playwright",
    timeout: int = 10,
    odds_filter: OddsFilter | None = None,
) -> FetchOddsResponse:
    sport = _resolve_sport(event_url, sport)
    with ScraperFactory.create_scraper(engine_type=engine, sport_type=sport, timeout=timeout) as scraper:
        scraper.event_url = event_url
        return scraper.fetch_and_parse_odds(odds_filter=odds_filter)


def scrape_event(
    event_url: str,
    sport: str | None = None,
    engine: str = "playwright",
    timeout: int = 10,
) -> Dict[str, Any]:
    sport = _resolve_sport(event_url, sport)
    with ScraperFactory.create_scraper(engine_type=engine, sport_type=sport, timeout=timeout) as scraper:
        scraper.event_url = event_url
        return scraper.fetch_and_parse_event()


def scrape_event_info(
    event_url: str,
    sport: str | None = None,
    engine: str = "playwright",
    timeout: int = 10,
) -> Dict[str, Any]:
    sport = _resolve_sport(event_url, sport)
    with ScraperFactory.create_scraper(engine_type=engine, sport_type=sport, timeout=timeout) as scraper:
        scraper.event_url = event_url
        return scraper.fetch_and_parse_event_info()
