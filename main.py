import argparse
import logging
from scraper.scraper_factory import ScraperFactory
from utils.detect_sport import detect_sport_from_url
from utils.json_formatter import JsonFormatter


logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", handlers=[logging.StreamHandler()])


def scrape_cmd(event_url: str, sport: str | None, engine: str, timeout: int, fetch_func) -> None:
    """Common function for scraping commands with error handling"""
    if sport is None:
        sport = detect_sport_from_url(event_url)

    scraper = ScraperFactory.create_scraper(engine_type=engine, sport_type=sport, timeout=timeout)
    scraper.event_url = event_url

    try:
        data = fetch_func(scraper)
        print(JsonFormatter.to_json(data))
    finally:
        scraper.engine.close()


def scrape_odds_cmd(event_url: str, sport: str | None = None, engine: str = "curl", timeout: int = 10, odds: list[str] | None = None) -> None:
    """CLI interface for scraping odds"""
    scrape_cmd(event_url, sport, engine, timeout, lambda scraper: scraper.fetch_and_parse_odds(odds=odds))


def scrape_event_cmd(event_url: str, sport: str | None = None, engine: str = "curl", timeout: int = 10) -> None:
    """CLI interface for scraping event information"""
    scrape_cmd(event_url, sport, engine, timeout, lambda scraper: scraper.fetch_and_parse_event())


def scrape_event_info_cmd(event_url: str, sport: str | None = None, engine: str = "curl", timeout: int = 10) -> None:
    """CLI interface for scraping context information"""
    scrape_cmd(event_url, sport, engine, timeout, lambda scraper: scraper.fetch_and_parse_event_info())


def add_common_arguments(parser: argparse.ArgumentParser) -> None:
    """Add common arguments to a subparser"""
    parser.add_argument("url", help="URL Flashscore")
    parser.add_argument("--sport", default=None, help="Sport type (football, tennis). If not provided, detected from URL")
    parser.add_argument("--engine", default="playwright", help="Engine type (default: playwright)")
    parser.add_argument("--timeout", type=int, default=10, help="Timeout in seconds")


def main() -> None:
    parser = argparse.ArgumentParser(description="Flashscore Scraper")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    odds_parser = subparsers.add_parser("odds", help="Scrap odds")
    odds_parser.add_argument("--odds", nargs="*", default=[], help="Specific odds types to scrape (e.g. '1x2-odds', 'over-under'). If not provided, all available odds types will be scraped")
    add_common_arguments(odds_parser)

    event_parser = subparsers.add_parser("event", help="Scrap event information")
    add_common_arguments(event_parser)

    event_info_parser = subparsers.add_parser("event-info", help="Scrap context information")
    add_common_arguments(event_info_parser)

    args = parser.parse_args()

    command_dispatch = {
        "odds": lambda: scrape_odds_cmd(args.url, args.sport, args.engine, args.timeout, args.odds),
        "event": lambda: scrape_event_cmd(args.url, args.sport, args.engine, args.timeout),
        "event-info": lambda: scrape_event_info_cmd(args.url, args.sport, args.engine, args.timeout),
    }

    if args.command in command_dispatch:
        command_dispatch[args.command]()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
