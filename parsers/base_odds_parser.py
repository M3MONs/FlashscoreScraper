from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Type
from bs4 import BeautifulSoup, Tag
import logging

from models.odds_filter import OddsFilter
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
        """Automatically registers subclasses in the parser registry based on their sport and odds type."""
        super().__init_subclass__(**kwargs)
        cls.logger = logging.getLogger(cls.__name__)

        if cls._should_register():
            cls._register_parser()

    @classmethod
    def _should_register(cls) -> bool:
        """Determines if the subclass should be registered as a parser."""
        if getattr(cls, "__abstractmethods__", None):
            return False
        if not hasattr(cls, "sport_type") or not hasattr(cls, "odds_type"):
            raise AttributeError(f"{cls.__name__} must define 'sport_type' and 'odds_type'")
        return cls.sport_type is not None

    @classmethod
    def _register_parser(cls) -> None:
        """Registers the parser class in the global registry under its sport and odds type."""
        BaseOddsParser._registry.setdefault(cls.sport_type, {})
        BaseOddsParser._registry[cls.sport_type][cls.odds_type] = cls

    def parse(self, url: str, data: Any, odds_filter: OddsFilter | None = None) -> list[OddsParserRow]:
        """Main method to parse odds data, applies filtering and returns structured results."""
        soup = BeautifulSoup(data, "html.parser")
        wrapper = soup.find("div", class_="oddsTab__tableWrapper")

        if not wrapper:
            return []

        rows = wrapper.select(".ui-table__row")
        bookmaker_filter = set(odds_filter.bookmakers) if odds_filter and odds_filter.bookmakers else None
        return self._parse_rows(rows, bookmaker_filter)

    def _parse_rows(self, rows: list[Tag], bookmaker_filter: set[str] | None) -> list[OddsParserRow]:
        """Parses each row of odds data, applying bookmaker filtering and error handling."""
        results = []
        for row in rows:
            try:
                bookmaker = BookmakerInfo(
                    id=self._extract_bookmaker_id(row),
                    name=self._extract_bookmaker_name(row),
                    link=self._extract_bookmaker_link(row),
                )

                if bookmaker_filter is not None and bookmaker.id not in bookmaker_filter:
                    continue

                result = self._parse_row(row, bookmaker)

                if result is not None:
                    results.append(result)

            except Exception as e:
                self.logger.error(f"Error parsing row: {e}")

        return results

    @abstractmethod
    def _parse_row(self, row: Tag, bookmaker: BookmakerInfo) -> OddsParserRow | None:
        """Abstract method to parse a single row of odds data, must be implemented by subclasses."""
        pass

    @classmethod
    def create(cls, sport_type: str, odds_type: str) -> "BaseOddsParser":
        """Factory method to create an instance of the appropriate parser based on sport and odds type."""
        parser_class = cls._get_parser_class(sport_type, odds_type)
        if parser_class:
            return parser_class()
        return cls._create_default_parser(sport_type, odds_type)

    @classmethod
    def _get_parser_class(cls, sport_type: str, odds_type: str) -> Type["BaseOddsParser"] | None:
        """Retrieves the parser class for the given sport and odds type from the registry."""
        sport_registry = cls._registry.get(sport_type)
        if not sport_registry:
            return None
        return sport_registry.get(odds_type)

    @classmethod
    def _create_default_parser(cls, sport_type: str, odds_type: str) -> "BaseOddsParser":
        """Creates a default parser instance when no specific parser is found."""
        parser = DefaultOddsParser()
        parser.sport_type = sport_type
        parser.odds_type = odds_type
        parser.logger = logging.getLogger(f"DefaultOddsParser[{sport_type}/{odds_type}]")
        return parser

    def _generate_result(self, bookmaker: BookmakerInfo, odds_values: list[OddsParserRowData]) -> OddsParserRow:
        """Generates a structured OddsParserRow result from the bookmaker info and extracted odds values."""
        return OddsParserRow(
            bookmaker_id=bookmaker.id,
            bookmaker_name=bookmaker.name,
            bookmaker_link=bookmaker.link,
            odds_values=odds_values,
        )

    def _extract_bookmaker_link(self, row: Tag) -> str | None:
        """Extracts the bookmaker link from a row."""
        link_tag = row.select_one(".oddsCell__bookmakerPart a")
        return str(link_tag["href"]) if link_tag and "href" in link_tag.attrs else None

    def _extract_bookmaker_name(self, row: Tag) -> str:
        """Extracts the bookmaker name from a row."""
        img_tag = row.select_one(".oddsCell__bookmakerPart img")
        return str(img_tag.get("alt")) if img_tag else "Unknown"

    def _extract_bookmaker_id(self, row: Tag) -> str | None:
        """Extracts the bookmaker ID from a row."""
        odds_cell = row.select_one(".oddsCell__bookmakerPart")
        if odds_cell and "data-analytics-bookmaker-id" in odds_cell.attrs:
            return str(odds_cell["data-analytics-bookmaker-id"])
        return "Unknown"

    def _extract_odds(self, row: Tag) -> list[str]:
        """Extracts the odds values from a row."""
        return [span.get_text(strip=True) for span in row.select("a.oddsCell__odd span")]

    def _extract_value(self, row: Tag) -> str:
        """Extracts a specific value from a row."""
        value_span = row.find("span", {"data-testid": "wcl-oddsValue"})
        return value_span.get_text(strip=True) if value_span else ""

    def _extract_header_labels(self, soup: BeautifulSoup) -> list[str]:
        """Extracts odds column header labels from the table."""
        headers = soup.select(".ui-table__header .oddsCell__header")
        return [h.get_text(strip=True) for h in headers]

    def _extract_active_tab_label(self, soup: BeautifulSoup) -> str:
        """Extracts the active odds tab label."""
        tab = soup.select_one("button[data-selected='true'][data-testid='wcl-tab']")
        return tab.get_text(strip=True) if tab else ""

    def _extract_all_odds_cells(self, row: Tag) -> list[str]:
        """Extracts all odds value cells from a row (both odds and no-odds cells)."""
        cells = row.select("a.oddsCell__odd, span.oddsCell__noOddsCell")
        result = []
        for cell in cells:
            if "oddsCell__noOddsCell" in (cell.get("class") or []):
                result.append("-")
            else:
                span = cell.find("span")
                result.append(span.get_text(strip=True) if span else "")
        return result


class DefaultOddsParser(BaseOddsParser):
    """Fallback parser for unhandled sport/odds types, extracts odds in a generic way."""

    sport_type = ""
    odds_type = ""

    def parse(self, url: str, data: Any, odds_filter: OddsFilter | None = None) -> list[OddsParserRow]:
        """Overrides the base parse method to provide a generic parsing implementation when no specific parser is found."""
        soup = BeautifulSoup(data, "html.parser")
        wrapper = soup.find("div", class_="oddsTab__tableWrapper")
        if not wrapper:
            return []

        self._odds_headers = self._extract_header_labels(soup)
        self._odds_tab_label = self._extract_active_tab_label(soup)

        rows = wrapper.select(".ui-table__row")
        bookmaker_filter = set(odds_filter.bookmakers) if odds_filter and odds_filter.bookmakers else None
        return self._parse_rows(rows, bookmaker_filter)

    def _parse_row(self, row: Tag, bookmaker: BookmakerInfo) -> OddsParserRow | None:
        """Parses a single row of odds data in a generic way, extracting all odds cells and constructing the result."""
        headers = getattr(self, "_odds_headers", [])
        cells = self._extract_all_odds_cells(row)

        if all(c == "-" for c in cells):
            return None

        wcl_value = self._extract_value(row)
        odds_data = self._build_odds_data(cells, wcl_value, headers)

        return self._generate_result(bookmaker, odds_data)

    def _build_odds_data(self, cells: list[str], wcl_value: str, headers: list[str]) -> list[OddsParserRowData]:
        """Constructs odds data objects from cell values and headers."""
        odds_data = []
        for i, odds in enumerate(cells):
            value = wcl_value if wcl_value else (headers[i] if i < len(headers) else f"col_{i}")
            type_ = headers[i] if i < len(headers) else f"col_{i}"
            odds_data.append(OddsParserRowData(value=value, type=type_, odds=odds))
        return odds_data
