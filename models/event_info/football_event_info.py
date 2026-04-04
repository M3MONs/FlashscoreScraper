from dataclasses import dataclass, field

from models.base_event_info import BaseEventInfo
from models.event_info.event_info_factory import register_event_info
from utils.detect_sport import Sports


@register_event_info(Sports.FOOTBALL.value)
class FootballEventInfo(BaseEventInfo):
    STANDINGS = ("standings", "standings/standings/overall/")
    DRAW = ("draw", "draw/draw/")

    @property
    def tab_label(self) -> str:
        return self.value[0]

    @property
    def url_path(self) -> str:
        return self.value[1]


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
