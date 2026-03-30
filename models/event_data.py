from dataclasses import dataclass
from typing import Dict


@dataclass
class EventData:
    date: str | None
    participants: list[Dict[str, str | None]]
    score: str | None
    detail_status: str | None
    league: Dict[str, str | None] | None
