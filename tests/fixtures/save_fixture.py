import logging
from engines.engine_factory import create_engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

URL = "https://www.flashscore.com/match/football/aston-villa-W00wmLO0/west-ham-Cxq57r8g/?mid=U7CL8Og5"

engine = create_engine("playwright", timeout=15)

try:
    html = engine.get_page(URL)
    with open("tests/fixtures/football_match.html", "w", encoding="utf-8") as f:
        f.write(html)
    logger.info("Football match page saved successfully.")
finally:
    engine.close()