import argparse
from engines.engine_factory import create_engine

def scrape_page(url: str, engine_type: str = "curl", timeout: int = 10) -> str:
    with create_engine(engine_type, timeout) as engine:
        return engine.get_page(url)

def main():
    parser = argparse.ArgumentParser(description="Flashscore Scraper")
    parser.add_argument("url", help="URL for scraping")
    parser.add_argument("--engine", default="curl", help="Engine type (default: curl)")
    parser.add_argument("--timeout", type=int, default=10, help="Timeout in seconds (default: 10)")
    
    args = parser.parse_args()
    
    page_content = scrape_page(args.url, args.engine, args.timeout)
    print(page_content)


if __name__ == "__main__":
    main()
