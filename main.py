import argparse
from scraper.scraper_factory import ScraperFactory
from utils.json_formatter import JsonFormatter


def scrape_odds_cmd(event_url: str, sport: str | None = None, engine: str = "curl", timeout: int = 10) -> None:
    """CLI interface for scraping odds"""
    scraper = ScraperFactory.create_scraper(event_url=event_url, engine_type=engine, sport_type=sport, timeout=timeout)

    try:
        odds_data = scraper.fetch_and_parse_odds()
        print(JsonFormatter.to_json(odds_data))
    finally:
        scraper.engine.close()


def scrape_event_cmd(event_url: str, sport: str | None = None, engine: str = "curl", timeout: int = 10) -> None:
    """CLI interface for scraping event information"""
    scraper = ScraperFactory.create_scraper(event_url=event_url, engine_type=engine, sport_type=sport, timeout=timeout)

    try:
        event_data = scraper.fetch_and_parse_event()
        print(JsonFormatter.to_json(event_data))
    finally:
        scraper.engine.close()


def scrape_event_info_cmd(event_url: str, sport: str | None = None, engine: str = "curl", timeout: int = 10) -> None:
    """CLI interface for scraping context information"""
    scraper = ScraperFactory.create_scraper(event_url=event_url, engine_type=engine, sport_type=sport, timeout=timeout)

    try:
        event_info = scraper.fetch_and_parse_event_info()
        print(JsonFormatter.to_json(event_info))
    finally:
        scraper.engine.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Flashscore Scraper")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    odds_parser = subparsers.add_parser("odds", help="Scrap odds")
    odds_parser.add_argument("url", help="URL Flashscore")
    odds_parser.add_argument("--sport", default=None, help="Sport type (football, tennis). If not provided, detected from URL")
    odds_parser.add_argument("--engine", default="playwright", help="Engine type (default: playwright)")
    odds_parser.add_argument("--timeout", type=int, default=10, help="Timeout in seconds")

    event_parser = subparsers.add_parser("event", help="Scrap event information")
    event_parser.add_argument("url", help="URL Flashscore")
    event_parser.add_argument("--sport", default=None, help="Sport type")
    event_parser.add_argument("--engine", default="playwright", help="Engine type")
    event_parser.add_argument("--timeout", type=int, default=10, help="Timeout in seconds")

    event_info_parser = subparsers.add_parser("event-info", help="Scrap context information")
    event_info_parser.add_argument("url", help="URL Flashscore")
    event_info_parser.add_argument("--sport", default=None, help="Sport type")
    event_info_parser.add_argument("--engine", default="playwright", help="Engine type")
    event_info_parser.add_argument("--timeout", type=int, default=10, help="Timeout in seconds")

    args = parser.parse_args()

    if args.command == "odds":
        scrape_odds_cmd(args.url, args.sport, args.engine, args.timeout)
    elif args.command == "event":
        scrape_event_cmd(args.url, args.sport, args.engine, args.timeout)
    elif args.command == "event-info":
        scrape_event_info_cmd(args.url, args.sport, args.engine, args.timeout)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
