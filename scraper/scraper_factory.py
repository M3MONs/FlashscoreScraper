from engines.base_engine import BaseEngine
from parsers.parser_factory import create_parser
from utils.detect_sport import detect_sport_from_url
from .scraper_service import ScraperService
from engines.engine_factory import create_engine


class ScraperFactory:
    @staticmethod
    def create_scraper(event_url: str, engine_type: str = "curl", sport_type: str | None = None, timeout: int = 10) -> ScraperService:

        if not event_url:
            raise ValueError("event_url is required")

        if sport_type is None:
            sport_type = detect_sport_from_url(event_url)

        engine = create_engine(engine_type, timeout)
        parser = create_parser(sport_type)

        return ScraperService(engine, parser, event_url)

    @staticmethod
    def create_scraper_with_custom_engine(event_url: str, engine: BaseEngine, sport_type: str | None = None) -> ScraperService:
        if not event_url:
            raise ValueError("event_url is required")

        if sport_type is None:
            sport_type = detect_sport_from_url(event_url)

        parser = create_parser(sport_type)
        return ScraperService(engine, parser, event_url)
