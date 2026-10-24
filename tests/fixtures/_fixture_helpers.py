import logging
from pathlib import Path

from engines.engine_factory import create_engine

logger = logging.getLogger(__name__)


def fetch_and_save(items: list[tuple[str, Path, str | None]], engine_type: str = "playwright", timeout: int = 15) -> None:
    """Fetches HTML from each URL (optionally waiting for a selector) and saves it to the corresponding file path."""
    engine = create_engine(engine_type, timeout=timeout)
    try:
        for url, file_path, wait_for_selector in items:
            html = engine.get_page(url, wait_for_selector)
            file_path.write_text(html, encoding="utf-8")
            logger.info(f"Saved: {file_path.name}")
    finally:
        engine.close()
