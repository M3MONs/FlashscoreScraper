import logging
from pathlib import Path
from engines.engine_factory import create_engine
from models.sports import Sports

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

FILE_PATH = Path(__file__).parent


URLS = [
    {"url": "https://www.flashscore.com/match/football/las-palmas-IyRQC2vM/real-madrid-W8mj7MDD/standings/standings/overall/?mid=CE0hJiFM", "sport": Sports.FOOTBALL},
]

engine = create_engine("playwright", timeout=15)

try:
    for url_info in URLS:
        html = engine.get_page(url_info["url"])
        file_path = FILE_PATH / f"{url_info['sport'].name.lower()}_event_info_standings.html"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html)
        logger.info(f"{url_info['sport'].name} match page saved successfully.")
finally:
    engine.close()
