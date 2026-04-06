import pytest
from pathlib import Path
from bs4 import BeautifulSoup


def load_soup_from_path(path: Path | str) -> BeautifulSoup:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return BeautifulSoup(f.read(), "html.parser")
    except FileNotFoundError:
        pytest.fail(f"Fixture file not found: {path}")
