from abc import ABC, abstractmethod
from typing import Any, Dict, Type
from bs4 import Tag
import logging


class BaseOddsParser(ABC):
    """Global base class for all odds parsers across sports."""

    _registry: Dict[str, Dict[str, Type["BaseOddsParser"]]] = {}

    sport_type: str
    odds_type: str

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.logger = logging.getLogger(cls.__name__)

        if getattr(cls, "__abstractmethods__", None):
            return

        if not hasattr(cls, "sport_type") or not hasattr(cls, "odds_type"):
            raise AttributeError(f"{cls.__name__} must define 'sport_type' and 'odds_type'")

        BaseOddsParser._registry.setdefault(cls.sport_type, {})
        BaseOddsParser._registry[cls.sport_type][cls.odds_type] = cls

    @abstractmethod
    def parse(self, url: str, data: Any) -> list[Any]:
        pass

    @classmethod
    def create(cls, sport_type: str, odds_type: str) -> "BaseOddsParser | None":
        sport_registry = cls._registry.get(sport_type)

        if not sport_registry:
            raise ValueError(f"Unsupported sport type: {sport_type}")

        parser_class = sport_registry.get(odds_type)
        return parser_class() if parser_class else None

    @staticmethod
    def _extract_bookmaker_link(row: Tag) -> str | None:
        link_tag = row.select_one(".oddsCell__bookmakerPart a")
        return str(link_tag["href"]) if link_tag and "href" in link_tag.attrs else None

    @staticmethod
    def _extract_bookmaker_name(row: Tag) -> str:
        img_tag = row.select_one(".oddsCell__bookmakerPart img")
        return str(img_tag.get("alt")) if img_tag else "Unknown"
