import sys
import pytest
from pathlib import Path
from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).parent))

from soup_helpers import load_soup_from_path


@pytest.fixture(scope="module")
def load_soup(fixture_path: str) -> BeautifulSoup:
    return load_soup_from_path(fixture_path)