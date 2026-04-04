from bs4 import BeautifulSoup, Tag
from typing import Any, Callable, List

from models.event_info_data import EventInfoData
from models.event_info.football_event_info import FootballEventInfo, FootballFormEntry, FootballStandingsEntry

_FORM_RESULT_MAP = {
    "win": "W",
    "lose": "L",
    "draw": "D",
}


class FootballEventInfoParser:
    _handlers = {}

    @classmethod
    def _handler(cls, info_type: FootballEventInfo) -> Callable[..., Any]:
        def decorator(fn) -> Any:
            cls._handlers[info_type] = fn
            return fn

        return decorator

    @staticmethod
    def detect_available_types(soup: BeautifulSoup) -> List[FootballEventInfo]:
        tabs_container = soup.find("div", attrs={"data-testid": "wcl-tabs"})
        if not tabs_container:
            return []

        tab_labels = {btn.get_text(strip=True).lower() for btn in tabs_container.find_all("button", attrs={"data-testid": "wcl-tab"})}

        return [info_type for info_type in FootballEventInfo if info_type.tab_label in tab_labels]

    @classmethod
    def parse_event_info(cls, soup: BeautifulSoup, info_type: str) -> EventInfoData | None:
        event_info_type = next((e for e in FootballEventInfo if e.tab_label == info_type), None)
        if event_info_type is None:
            return EventInfoData(info_type=info_type, data=None, metadata={"error": f"Unsupported info type: {info_type}"})

        handler = cls._handlers.get(event_info_type)
        if handler is None:
            return EventInfoData(info_type=info_type, data=None, metadata={"error": f"No handler implemented for: {info_type}"})

        return handler(soup)


@FootballEventInfoParser._handler(FootballEventInfo.STANDINGS)
def _parse_standings(soup: BeautifulSoup) -> EventInfoData[list[FootballStandingsEntry]]:
    ui_table = soup.find("div", class_="ui-table")
    if not ui_table:
        return EventInfoData(
            info_type=FootballEventInfo.STANDINGS.tab_label,
            data=[],
            metadata={"error": "Standings table not found"},
        )

    table_body = ui_table.find("div", class_="ui-table__body")
    if not table_body:
        return EventInfoData(info_type=FootballEventInfo.STANDINGS.tab_label, data=[])

    entries = [_parse_standings_row(row) for row in table_body.find_all("div", class_="ui-table__row")]
    return EventInfoData(info_type=FootballEventInfo.STANDINGS.tab_label, data=entries)


def _parse_standings_row(row: Tag) -> FootballStandingsEntry:
    rank_cell = row.find("div", class_="tableCellRank")
    rank_text, promotion_status = _parse_rank_cell(rank_cell)

    name_link = row.find("a", class_="tableCellParticipant__name")
    value_cells = row.find_all(class_="table__cell--value")

    def _cell(idx: int) -> str | None:
        return value_cells[idx].get_text(strip=True) if idx < len(value_cells) else None

    goals_for, goals_against = _split_goals(_cell(4))

    team_url = None
    if name_link:
        href = name_link.get("href")
        team_url = href if isinstance(href, str) else None

    return FootballStandingsEntry(
        rank=int(rank_text) if rank_text and rank_text.isdigit() else rank_text,
        promotion_status=promotion_status,
        team=name_link.get_text(strip=True) if name_link else None,
        team_url=team_url,
        matches_played=_cell(0),
        wins=_cell(1),
        draws=_cell(2),
        losses=_cell(3),
        goals_for=goals_for,
        goals_against=goals_against,
        goal_difference=_cell(5),
        points=_cell(6),
        form=_parse_form(row),
        highlighted="table__row--selected" in (row.get("class") or []),
    )


def _parse_rank_cell(rank_cell: Tag | None) -> tuple[str | None, str | None]:
    if not rank_cell:
        return None, None
    title = rank_cell.get("title")
    title_str = title if isinstance(title, str) else None
    return rank_cell.get_text(strip=True).rstrip("."), title_str


def _split_goals(goals_raw: str | None) -> tuple[str | None, str | None]:
    if goals_raw and ":" in goals_raw:
        goals_for, goals_against = goals_raw.split(":", 1)
        return goals_for, goals_against
    return None, None


def _parse_form(row: Tag) -> list[FootballFormEntry]:
    entries = []
    for icon in row.find_all("a", class_="tableCellFormIcon"):
        badge = icon.find(attrs={"data-testid": True})
        if not badge:
            continue
        test_id = str(badge.get("data-testid") or "")
        result = next(
            (v for k, v in _FORM_RESULT_MAP.items() if k in test_id),
            badge.get_text(strip=True),
        )
        href = icon.get("href")
        match_url = href if isinstance(href, str) else None
        entries.append(FootballFormEntry(result=result, match_url=match_url))
    return entries


@FootballEventInfoParser._handler(FootballEventInfo.DRAW)
def _parse_draw(soup: BeautifulSoup) -> EventInfoData:
    return EventInfoData(info_type=FootballEventInfo.DRAW.tab_label, data={})
