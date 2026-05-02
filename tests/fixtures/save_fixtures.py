import argparse
import logging
from pathlib import Path

from models.odds.odds_factory import get_odds_enum
from models.sports import Sports
from utils.url_builder import FlashscoreUrlBuilder
from tests.fixtures._fixture_helpers import fetch_and_save

logging.basicConfig(level=logging.INFO)

FIXTURE_CONFIGS = {
    Sports.FOOTBALL: {
        "event": [
            {"url": "https://www.flashscore.com/match/football/aston-villa-W00wmLO0/west-ham-Cxq57r8g/?mid=U7CL8Og5"},
        ],
        "odds": [
            {"url": "https://www.flashscore.com/match/football/aston-villa-W00wmLO0/west-ham-Cxq57r8g/?mid=U7CL8Og5"},
        ],
        "draw": [
            {"url": "https://www.flashscore.com/match/football/jagiellonia-lIDaZJTc/legia-K6kUepBs/draw/?mid=tzz8vxl1"},
        ],
        "standings": [
            {"url": "https://www.flashscore.com/match/football/las-palmas-IyRQC2vM/real-madrid-W8mj7MDD/standings/standings/overall/?mid=CE0hJiFM"},
        ],
    },
}


def build_items(config: dict, save_dir: Path, sport: Sports) -> list[tuple[str, Path]]:
    items: list[tuple[str, Path]] = []

    for entry in config.get("event", []):
        items.append((entry["url"], save_dir / "event.html"))

    for entry in config.get("odds", []):
        for odds_type in get_odds_enum(sport.value):
            odds_url = FlashscoreUrlBuilder.build_odds_url(entry["url"], odds_type.value)
            items.append((odds_url, save_dir / f"odds_{odds_type.value}.html"))

    for entry in config.get("draw", []):
        items.append((entry["url"], save_dir / "event_info_draw.html"))

    for entry in config.get("standings", []):
        items.append((entry["url"], save_dir / "event_info_standings.html"))

    return items


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch and save HTML fixtures for a given sport.")
    parser.add_argument("--sport", required=True, choices=[s.name.lower() for s in Sports],
                        help="Sport type (e.g. football)")
    parser.add_argument("--engine-type", default="playwright",
                        help="Engine type for fetching (default: playwright)")
    parser.add_argument("--timeout", type=int, default=15,
                        help="Timeout in seconds (default: 15)")
    args = parser.parse_args()

    sport = Sports[args.sport.upper()]
    save_dir = Path(__file__).parent / sport.name.lower()
    save_dir.mkdir(parents=True, exist_ok=True)

    config = FIXTURE_CONFIGS[sport]
    items = build_items(config, save_dir, sport)

    fetch_and_save(items, engine_type=args.engine_type, timeout=args.timeout)


if __name__ == "__main__":
    main()
