from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Type
from bs4 import BeautifulSoup, Tag
import logging

from models.odds_parser_row import OddsParserRow, OddsParserRowData


@dataclass
class BookmakerInfo:
    id: str | None
    name: str
    link: str | None


class BaseOddsParser(ABC):
    """Global base class for all odds parsers across sports."""

    _registry: Dict[str, Dict[str, Type["BaseOddsParser"]]] = {}

    sport_type: str
    odds_type: str

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        cls.logger = logging.getLogger(cls.__name__)

        if getattr(cls, "__abstractmethods__", None):
            return

        if not hasattr(cls, "sport_type") or not hasattr(cls, "odds_type"):
            raise AttributeError(f"{cls.__name__} must define 'sport_type' and 'odds_type'")

        BaseOddsParser._registry.setdefault(cls.sport_type, {})
        BaseOddsParser._registry[cls.sport_type][cls.odds_type] = cls

    def parse(self, url: str, data: Any) -> list[OddsParserRow]:
        soup = BeautifulSoup(data, "html.parser")
        wrapper = soup.find("div", class_="oddsTab__tableWrapper")

        if not wrapper:
            return []

        rows = wrapper.select(".ui-table__row")
        results = []

        for row in rows:
            try:
                bookmaker = BookmakerInfo(
                    id=self._extract_bookmaker_id(row),
                    name=self._extract_bookmaker_name(row),
                    link=self._extract_bookmaker_link(row),
                )
                result = self._parse_row(row, bookmaker)
                if result is not None:
                    results.append(result)
            except Exception as e:
                self.logger.error(f"Error parsing row: {e}")

        return results

    @abstractmethod
    def _parse_row(self, row: Tag, bookmaker: BookmakerInfo) -> OddsParserRow | None:
        pass

    @classmethod
    def create(cls, sport_type: str, odds_type: str) -> "BaseOddsParser | None":
        sport_registry = cls._registry.get(sport_type)

        if not sport_registry:
            raise ValueError(f"Unsupported sport type: {sport_type}")

        parser_class = sport_registry.get(odds_type)
        return parser_class() if parser_class else None

    def _generate_result(self, bookmaker: BookmakerInfo, odds_values: list[OddsParserRowData]) -> OddsParserRow:
        return OddsParserRow(
            bookmaker_id=bookmaker.id,
            bookmaker_name=bookmaker.name,
            bookmaker_link=bookmaker.link,
            odds_values=odds_values,
        )

    def _extract_bookmaker_link(self, row: Tag) -> str | None:
        link_tag = row.select_one(".oddsCell__bookmakerPart a")
        return str(link_tag["href"]) if link_tag and "href" in link_tag.attrs else None

    def _extract_bookmaker_name(self, row: Tag) -> str:
        img_tag = row.select_one(".oddsCell__bookmakerPart img")
        return str(img_tag.get("alt")) if img_tag else "Unknown"

    def _extract_bookmaker_id(self, row: Tag) -> str | None:
        odds_cell = row.select_one(".oddsCell__bookmakerPart")
        if odds_cell and "data-analytics-bookmaker-id" in odds_cell.attrs:
            return str(odds_cell["data-analytics-bookmaker-id"])
        return "Unknown"
    
    def _extract_odds(self, row: Tag) -> list[str]:
        return [span.get_text(strip=True) for span in row.select("a.oddsCell__odd span")]
    
    def _extract_value(self, row: Tag) -> str:
        value_span = row.find("span", {"data-testid": "wcl-oddsValue"})
        return value_span.get_text(strip=True) if value_span else ""
