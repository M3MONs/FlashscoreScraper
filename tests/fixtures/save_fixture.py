import logging
from engines.engine_factory import create_engine
from models.sports import Sports

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


URLS = [
    {"url": "https://www.flashscore.com/match/football/aston-villa-W00wmLO0/west-ham-Cxq57r8g/?mid=U7CL8Og5", "sport": Sports.FOOTBALL},
]

engine = create_engine("playwright", timeout=15)

try:
    for url_info in URLS:
        html = engine.get_page(url_info["url"])
        file_path = f"tests/fixtures/{url_info['sport'].name.lower()}_event.html"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html)
        logger.info(f"{url_info['sport'].name} match page saved successfully.")
finally:
    engine.close()
