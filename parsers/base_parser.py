from typing import Any, Dict, Sequence, Type
import logging

from bs4 import BeautifulSoup, Tag

from models.base_event_info import BaseEventInfo, GenericEventInfo
from models.event_data import EventData
from models.event_info_data import EventInfoData
from models.odds_filter import OddsFilter
from models.odds_parser_result import OddsParserResult
from models.parse_text_element_params import ParseTextElementParams


class BaseParser:
    _registry: Dict[str, Type["BaseParser"]] = {}
    sport_type: str
    _MAIN_TAB_LABELS = frozenset({"match", "summary", "odds"})
    _INFO_SELECTOR_MAP = {
        "draw": ".draw__cover",
        "h2h": ".h2h__section",
        "standings": ".ui-table",
        "table": ".ui-table",
    }

    def __init_subclass__(cls, sport_type: str | None = None, **kwargs) -> None:
        """Registers subclass in the parser registry under its sport type."""
        super().__init_subclass__(**kwargs)
        if sport_type:
            cls.sport_type = sport_type
            BaseParser._registry[sport_type] = cls

    @classmethod
    def create(cls, sport_type: str) -> "BaseParser":
        """Returns a parser instance for the given sport type, or a default instance."""
        if sport_type in cls._registry:
            return cls._registry[sport_type]()
        instance = cls()
        instance.sport_type = sport_type
        instance.logger.warning(f"No specific parser for sport '{sport_type}', using defaults")
        return instance

    def __init__(self) -> None:
        """Initializes the parser with a logger."""
        self.logger = logging.getLogger(self.__class__.__name__)

    def parse_event(self, url: str, data: Any) -> Dict[str, Any]:
        """Parses event data from a URL and raw HTML, with debug logging."""
        self.logger.debug(f"Parsing event from URL: {url}")
        result = self._parse_event(url, data)
        self.logger.debug(f"Finished parsing event from URL: {url}")
        return result

    def _parse_event(self, url: str, data: Any) -> Dict[str, Any]:
        """Extracts structured event data from raw HTML."""
        soup = BeautifulSoup(data, "html.parser")
        event = EventData(
            date=self._parse_event_date(soup),
            participants=self._parse_event_participants(soup),
            score=self._parse_event_score(soup),
            detail_status=self._parse_event_detail_status(soup),
            league=self._parse_event_league(soup),
        )
        return event.__dict__ if event else {}

    def detect_available_event_info_types(self, data: Any) -> Sequence[BaseEventInfo]:
        """Returns available event info types detected from the page tabs, with debug logging."""
        self.logger.debug("Detecting available event info types")
        result = self._detect_available_event_info_types(data)
        self.logger.debug(f"Detected event info types: {[getattr(t, 'value', t.tab_label) for t in result]}")
        return result

    def _detect_available_event_info_types(self, data: Any) -> Sequence[BaseEventInfo]:
        """Detects event info types from page tabs using sport-specific or generic fallback logic."""
        soup = BeautifulSoup(data, "html.parser")
        tabs_container = soup.find("div", attrs={"data-testid": "wcl-tabs"})
        if not tabs_container:
            return []
        tab_labels = {btn.get_text(strip=True).lower() for btn in tabs_container.find_all("button", attrs={"data-testid": "wcl-tab"})}
        from models.event_info.event_info_factory import get_event_info_enum

        try:
            event_info_cls = get_event_info_enum(self.sport_type)
        except ValueError:
            return self._detect_generic_tab_types(tabs_container, tab_labels)  # type: ignore[return-value]
        return [e for e in event_info_cls if e.tab_label in tab_labels]

    def _detect_generic_tab_types(self, tabs_container: Tag, tab_labels: set[str]) -> list[GenericEventInfo]:
        """Builds a list of GenericEventInfo from anchor tags when no sport-specific enum exists."""
        result = []
        for a_tag in tabs_container.find_all("a", attrs={"data-analytics-alias": True}):
            alias = str(a_tag.get("data-analytics-alias", ""))
            if alias in ("match-summary", "odds-comparison"):
                continue
            btn = a_tag.find("button", attrs={"data-testid": "wcl-tab"})
            label = btn.get_text(strip=True).lower() if btn else alias
            url_path = self._extract_info_path(str(a_tag.get("href", "")))
            if label and url_path and label not in self._MAIN_TAB_LABELS:
                result.append(GenericEventInfo(tab_label=label, url_path=url_path, wait_for_selector=self._INFO_SELECTOR_MAP.get(label)))
        if not result:
            result = [
                GenericEventInfo(tab_label=l, url_path=f"{l}/", wait_for_selector=self._INFO_SELECTOR_MAP.get(l))  # noqa: E741
                for l in sorted(tab_labels)  # noqa: E741
                if l not in self._MAIN_TAB_LABELS
            ]
        return result  # type: ignore

    def parse_event_info(self, url: str, data: Any, info_type: str) -> Dict[str, Any]:
        """Parses a specific event info section from raw HTML, with debug logging."""
        self.logger.debug(f"Parsing event info from URL: {url}, type: {info_type}")
        result = self._parse_event_info(url, data, info_type)
        self.logger.debug(f"Finished parsing event info from URL: {url}, type: {info_type}")
        return result

    def _parse_event_info(self, url: str, data: Any, info_type: str) -> Dict[str, Any]:
        """Extracts event info data for the given info_type, returning an error payload if unsupported."""
        soup = BeautifulSoup(data, "html.parser")
        from models.event_info.event_info_factory import get_event_info_enum

        try:
            event_info_cls = get_event_info_enum(self.sport_type)
            event_info_type = next((e for e in event_info_cls if e.tab_label == info_type), None)
            if event_info_type is None:
                return EventInfoData(
                    info_type=info_type,
                    data=None,
                    metadata={"error": f"Unsupported info type: {info_type}"},
                ).__dict__
        except ValueError:
            pass

        data = self._extract_generic_event_info(soup, info_type)
        return EventInfoData(info_type=info_type, data=data).__dict__

    def parse_odds(self, url: str, data: Any, odds_type: str, odds_filter: OddsFilter | None = None) -> OddsParserResult:
        """Parses odds data for the given odds type, with debug logging."""
        self.logger.debug(f"Parsing odds from URL: {url} with odds type: {odds_type}")
        result = self._parse_odds(url, data, odds_type, odds_filter)
        self.logger.debug(f"Finished parsing odds from URL: {url} with odds type: {odds_type}")
        return result

    def _parse_odds(self, url: str, data: Any, odds_type: str, odds_filter: OddsFilter | None = None) -> OddsParserResult:
        """Delegates to the appropriate odds parser and wraps the result."""
        from parsers.base_odds_parser import BaseOddsParser

        try:
            parser = BaseOddsParser.create(self.sport_type, odds_type)
            return OddsParserResult(odds_type=odds_type, data=parser.parse(url, data, odds_filter), error=None)
        except ValueError as e:
            self.logger.warning(f"No odds parser for sport '{self.sport_type}': {e}")
            return OddsParserResult(odds_type=odds_type, data=None, error=str(e))

    @staticmethod
    def parse_text_element(params: ParseTextElementParams) -> str:
        """Finds an HTML element by tag and class and returns its text, or the default value."""
        element = params.soup.find(params.html_tag, class_=params.class_name)
        if element:
            return element.get_text(strip=True)
        logging.warning(f"Element with class '{params.class_name}' not found")
        return params.default_value

    def _parse_event_date(self, soup: BeautifulSoup) -> str:
        """Extracts the event start date from the page."""
        params = ParseTextElementParams(soup=soup, class_name="duelParticipant__startTime", html_tag="div", default_value="Unknown date")
        return self.parse_text_element(params)

    def _parse_event_participants(self, soup: BeautifulSoup) -> list[Dict[str, str | None]]:
        """Extracts home and away participant info from the page."""
        team_elements = soup.find_all("div", class_="participant__participantName")
        team_img_elements = soup.find_all("a", class_="participant__participantLink--team")
        if len(team_elements) != 2 or len(team_img_elements) != 2:
            self.logger.warning(f"Expected 2 participants, found {len(team_elements)} names, {len(team_img_elements)} links")
            return []
        return [
            self._build_participant_info(role, name_el, link_el) for role, name_el, link_el in zip(("home", "away"), team_elements, team_img_elements)
        ]

    @staticmethod
    def _build_participant_info(role: str, name_el: Tag, link_el: Tag) -> Dict[str, str | None]:
        """Builds a participant info dict with role, name, image URL, and profile link."""
        img_tag = link_el.find("img")
        return {
            "role": role,
            "name": name_el.get_text(strip=True),
            "img": str(img_tag.get("src")) if img_tag else None,
            "link": str(link_el.get("href")) if link_el.get("href") else None,
        }

    def _parse_event_score(self, soup: BeautifulSoup) -> str | None:
        """Extracts the event score from the page."""
        params = ParseTextElementParams(soup=soup, class_name="detailScore__wrapper", html_tag="div", default_value="Unknown score")
        return self.parse_text_element(params)

    def _parse_event_detail_status(self, soup: BeautifulSoup) -> str | None:
        """Extracts the event detail status from the page header."""
        params = ParseTextElementParams(
            soup=soup,
            class_name="fixedHeaderDuel__detailStatus",
            html_tag="span",
            default_value="Unknown status",
        )
        return self.parse_text_element(params)

    def _parse_event_league(self, soup: BeautifulSoup) -> Dict[str, str | None] | None:
        """Extracts the league name and link from the breadcrumb navigation."""
        breadcrumbs = soup.find("div", class_="detail__breadcrumbs")
        if not breadcrumbs:
            return None
        items = breadcrumbs.find_all("li")
        if not items:
            return None
        last = items[-1]
        return {"name": self._extract_league_name(last), "link": self._extract_league_link(last)}

    @staticmethod
    def _extract_league_name(item: Tag) -> str | None:
        """Extracts the league name text from a breadcrumb item."""
        name_el = item.find(attrs={"itemprop": "name"}) or item.find("span") or item.find("a") or item
        return name_el.get_text(strip=True) if name_el else None

    @staticmethod
    def _extract_league_link(item: Tag) -> str | None:
        """Extracts the league href from a breadcrumb item."""
        a_tag = item.find("a", href=True)
        return str(a_tag.get("href")) if a_tag else None

    @staticmethod
    def _extract_info_path(href: str) -> str | None:
        """Extracts the last URL path segment from an href, used as the info type path."""
        clean = href.split("?")[0].rstrip("/")
        segment = clean.rsplit("/", 1)[-1] if clean else ""
        return f"{segment}/" if segment else None

    @staticmethod
    def has_table_cell_class(value: Any) -> bool:
        """Returns True if the value is a CSS class string containing 'table__cell'."""
        return isinstance(value, str) and "table__cell" in value

    def _extract_ui_tables(self, soup: BeautifulSoup) -> list[list[list[str]]]:
        """Extracts all ui-table elements as nested lists of cell text values."""
        tables = [self._extract_table_rows(t) for t in soup.find_all("div", class_="ui-table")]
        return [t for t in tables if t]

    def _extract_table_rows(self, ui_table: Tag) -> list[list[str]]:
        """Extracts non-empty rows from a single ui-table element."""
        rows = [[cell.get_text(strip=True) for cell in row.find_all(class_=self.has_table_cell_class)] for row in ui_table.select(".ui-table__row")]
        return [r for r in rows if r]

    def _extract_draw_side(self, bracket: Tag, side: str) -> dict | None:
        """Extracts participant info for one side (home or away) of a draw bracket."""
        row = bracket.find("div", class_=f"bracket__participantRow bracket__participantRow--{side}")
        if not row:
            return None
        img = row.find("img", class_=f"bracket__image bracket__image--{side}")
        name_el = row.find("span", class_="bracket__name")
        info_el = row.find("span", class_="bracket__info")
        result_el = bracket.find("div", class_=f"bracket__result bracket__result--{side}")
        score_el = result_el.find("div", class_="result") if result_el else None
        return {
            "name": name_el.get_text(strip=True) if name_el else None,
            "img": str(img.get("src")) if img else None,
            "seed": info_el.get_text(strip=True) if info_el else None,
            "score": score_el.get_text(strip=True) if score_el else None,
            "is_advancing": "bracket__name--advancing" in (name_el.get("class") or []) if name_el else False,
        }

    def _extract_draw_generic(self, soup: BeautifulSoup) -> Any:
        """Extracts all draw rounds from the page as a list of round dicts."""
        dc = soup.find("div", class_="draw")
        if not dc:
            return None
        return [self._extract_draw_round(r_el) for r_el in dc.find_all("div", class_="draw__round")]

    def _extract_draw_round(self, r_el: Tag) -> dict:
        """Extracts a single draw round with its name and list of bracket matches."""
        name_el = r_el.find("div", class_="draw__label")
        return {
            "name": name_el.get_text(strip=True) if name_el else None,
            "matches": [self._extract_draw_bracket(b) for b in r_el.find_all("div", class_="bracket")],
        }

    def _extract_draw_bracket(self, bracket: Tag) -> dict:
        """Extracts home/away sides and flags from a single bracket element."""
        classes = bracket.get("class") or []
        return {
            "home": self._extract_draw_side(bracket, "home"),
            "away": self._extract_draw_side(bracket, "away"),
            "is_eventless": "bracket--eventless" in classes,
            "is_highlighted": "bracket--defaultHighlighted" in classes,
        }

    def _extract_h2h_generic(self, soup: BeautifulSoup) -> Any:
        """Extracts all H2H sections as a list of section dicts, or None if empty."""
        sections = [
            {"title": self._extract_h2h_section_title(section), "matches": self._extract_h2h_matches(section)}
            for section in soup.select(".h2h__section")
        ]
        sections = [s for s in sections if s["matches"]]
        return sections if sections else None

    @staticmethod
    def _extract_h2h_section_title(section: Tag) -> str | None:
        """Extracts the title text from an H2H section header."""
        header = section.select_one("[data-testid='wcl-headerSection-text'] span")
        return header.get_text(strip=True) if header else None

    def _extract_h2h_matches(self, section: Tag) -> list[dict]:
        """Extracts all match rows from a single H2H section."""
        return [self._extract_h2h_match(row) for row in section.select(".h2h__row")]

    @staticmethod
    def _extract_h2h_match(row: Tag) -> dict:
        """Extracts a single H2H match row into a structured dict."""
        date_el = row.select_one(".h2h__date")
        event_el = row.select_one(".h2h__event span:last-child")
        home_el = row.select_one(".h2h__homeParticipant .h2h__participantInner")
        away_el = row.select_one(".h2h__awayParticipant .h2h__participantInner")
        home_img = row.select_one(".h2h__homeParticipant img")
        away_img = row.select_one(".h2h__awayParticipant img")
        result_spans = row.select(".h2h__result span")
        icon_el = row.select_one(".h2h__icon [data-testid^='wcl-badgeForm']")

        return {
            "date": date_el.get_text(strip=True) if date_el else None,
            "event": event_el.get_text(strip=True) if event_el else None,
            "home": {
                "name": home_el.get_text(strip=True) if home_el else None,
                "img": str(home_img.get("src")) if home_img else None,
            },
            "away": {
                "name": away_el.get_text(strip=True) if away_el else None,
                "img": str(away_img.get("src")) if away_img else None,
            },
            "result": [s.get_text(strip=True) for s in result_spans] if result_spans else [],
            "outcome": icon_el.get("title") if icon_el else None,
            "link": str(row.get("href")) if row.get("href") else None,
        }

    def _extract_generic_event_info(self, soup: BeautifulSoup, info_type: str = "") -> Any:
        """Dispatches extraction to the appropriate method based on info_type, with raw text fallback."""
        if info_type == "h2h":
            h2h = self._extract_h2h_generic(soup)
            return {"h2h": h2h} if h2h else None
        if info_type == "draw":
            draw = self._extract_draw_generic(soup)
            return {"draw": draw} if draw else None
        if info_type in ("standings", "table"):
            tables = self._extract_ui_tables(soup)
            return {"tables": tables} if tables else None

        h2h = self._extract_h2h_generic(soup)
        if h2h:
            return {"h2h": h2h}

        tables = self._extract_ui_tables(soup)
        draw = self._extract_draw_generic(soup)

        result = {}
        if tables:
            result["tables"] = tables
        if draw:
            result["draw"] = draw
        if result:
            return result

        main = soup.find("main") or soup.find("div", class_="detail") or soup
        text = main.get_text("\n", strip=True) if main else ""
        return {"raw_text": text} if text else None

    def discover_odds_types(self, data: Any) -> list[str]:
        """Discovers available odds types from the page, using hrefs first then tab labels as fallback."""
        soup = BeautifulSoup(data, "html.parser")
        odds_types = self._discover_odds_from_hrefs(soup)
        return list(odds_types or self._discover_odds_from_tabs(soup))

    @staticmethod
    def _discover_odds_from_hrefs(soup: BeautifulSoup) -> set[str]:
        """Extracts odds type keys from anchor href attributes containing '/odds/'."""
        odds_types = set()
        for a_tag in soup.find_all("a", href=True):
            href = str(a_tag.get("href"))
            if "/odds/" not in href:
                continue
            parts = href.rsplit("/odds/", 1)
            if len(parts) > 1:
                odds_key = parts[1].strip("/")
                if odds_key:
                    odds_types.add(odds_key)
        return odds_types

    @staticmethod
    def _discover_odds_from_tabs(soup: BeautifulSoup) -> set[str]:
        """Extracts odds type keys from tab button labels as a fallback when no hrefs are found."""
        tabs_container = soup.find("div", attrs={"data-testid": "wcl-tabs"})
        if not tabs_container:
            return set()
        return {
            label.replace(" ", "-").replace("/", "-")
            for btn in tabs_container.find_all("button", attrs={"data-testid": "wcl-tab"})
            if (label := btn.get_text(strip=True).lower()) and label not in ("odds", "summary", "h2h", "standings", "draw", "table")
        }
