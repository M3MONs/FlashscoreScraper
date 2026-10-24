from dataclasses import dataclass


@dataclass
class LeagueMatch:
    event_url: str
    status: str  # "finished" | "scheduled"
    round: str | None
    date: str
    home: str
    away: str
    score_home: int | None
    score_away: int | None
