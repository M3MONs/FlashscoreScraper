from abc import ABC, abstractmethod
from typing import Any


class BaseStatsParser(ABC):
    """Base class for sport-specific match statistics parsers."""

    url_path: str
    wait_for_selector: str | None = None

    @abstractmethod
    def parse(self, data: str) -> dict[str, Any]:
        """Parses the statistics page, raises ValueError when no stats are present."""
