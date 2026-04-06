import logging
from pathlib import Path
from models.sports import Sports
from tests.fixtures._fixture_helpers import fetch_and_save

logging.basicConfig(level=logging.INFO)

FILE_PATH = Path(__file__).parent

URLS = [
    {
        "url": "https://www.flashscore.com/match/football/las-palmas-IyRQC2vM/real-madrid-W8mj7MDD/standings/standings/overall/?mid=CE0hJiFM",
        "sport": Sports.FOOTBALL,
    },
]

items = [(url_info["url"], FILE_PATH / f"{url_info['sport'].name.lower()}_event_info_standings.html") for url_info in URLS]

fetch_and_save(items)
