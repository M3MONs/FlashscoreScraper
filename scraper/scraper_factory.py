from parsers.parser_factory import create_parser
from .scraper_service import ScraperService
from engines.engine_factory import create_engine


class ScraperFactory:
    @staticmethod
    def create_scraper(engine_type: str = "playwright", sport_type: str | None = None, timeout: int = 10) -> ScraperService:
        if sport_type is None:
            raise ValueError("sport_type is required")

        engine = create_engine(engine_type, timeout)
        parser = create_parser(sport_type)

        return ScraperService(engine, parser)
