import logging
from pathlib import Path
from models.odds.odds_factory import get_odds_enum
from models.sports import Sports
from utils.url_builder import FlashscoreUrlBuilder
from tests.fixtures._fixture_helpers import fetch_and_save

logging.basicConfig(level=logging.INFO)

FILE_PATH = Path(__file__).parent

URLS = [
    {"url": "https://www.flashscore.com/match/football/aston-villa-W00wmLO0/west-ham-Cxq57r8g/?mid=U7CL8Og5", "sport": Sports.FOOTBALL},
]

items = [
    (
        FlashscoreUrlBuilder.build_odds_url(url_info["url"], odds_type.value),
        FILE_PATH / f"{url_info['sport'].name.lower()}_odds_{odds_type.value}.html",
    )
    for url_info in URLS
    for odds_type in get_odds_enum(url_info["sport"].value)
]

fetch_and_save(items)
