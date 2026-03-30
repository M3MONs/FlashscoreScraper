import logging
from pathlib import Path
from engines.engine_factory import create_engine
from models.odds.odds_factory import get_odds_enum
from models.sports import Sports
from utils.url_builder import FlashscoreUrlBuilder

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

FILE_PATH = Path(__file__).parent

URLS = [
    {"url": "https://www.flashscore.com/match/football/aston-villa-W00wmLO0/west-ham-Cxq57r8g/?mid=U7CL8Og5", "sport": Sports.FOOTBALL},
]

engine = create_engine("playwright", timeout=15)

try:
    for url_info in URLS:
        sport = url_info["sport"]
        odds_enum = get_odds_enum(sport.value)
        for odds_type in odds_enum:
            odds_url = FlashscoreUrlBuilder.build_odds_url(url_info["url"], odds_type.value)
            html = engine.get_page(odds_url)
            file_path = FILE_PATH / f"{sport.name.lower()}_odds_{odds_type.value}.html"
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(html)
            logger.info(f"{sport.name} odds '{odds_type.value}' page saved successfully.")
finally:
    engine.close()
