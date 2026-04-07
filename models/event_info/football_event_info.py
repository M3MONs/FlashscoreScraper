from dataclasses import dataclass, field

from models.base_event_info import BaseEventInfo
from models.event_info.event_info_factory import register_event_info
from utils.detect_sport import Sports


@register_event_info(Sports.FOOTBALL.value)
class FootballEventInfo(BaseEventInfo):
    STANDINGS = ("standings", "standings/standings/overall/")
    DRAW = ("draw", "draw/")

    @property
    def tab_label(self) -> str:
        return self.value[0]

    @property
    def url_path(self) -> str:
        return self.value[1]

    @property
    def wait_for_selector(self) -> str | None:
        _selectors = {
            FootballEventInfo.DRAW: "div.draw",
        }
        return _selectors.get(self)


@dataclass
class FootballFormEntry:
    result: str
    match_url: str | None


@dataclass
class FootballStandingsEntry:
    rank: int | str | None
    promotion_status: str | None
    team: str | None
    team_url: str | None
    matches_played: str | None
    wins: str | None
    draws: str | None
    losses: str | None
    goals_for: str | None
    goals_against: str | None
    goal_difference: str | None
    points: str | None
    form: list[FootballFormEntry] = field(default_factory=list)
    highlighted: bool = False


@dataclass
class FootballDrawParticipant:
    name: str | None
    is_home: bool
    is_advancing: bool
    score: str | None


@dataclass
class FootballDrawMatch:
    home: FootballDrawParticipant | None
    away: FootballDrawParticipant | None
    is_eventless: bool
    is_highlighted: bool


@dataclass
class FootballDrawRound:
    round_name: str | None
    matches: list[FootballDrawMatch] = field(default_factory=list)
