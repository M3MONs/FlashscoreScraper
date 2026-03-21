from dataclasses import dataclass
from typing import Dict
from .odds_result import OddsResult

@dataclass
class FetchOddsResponse:
    event_url: str
    odds_types: Dict[str, OddsResult]

    def has_errors(self) -> bool:
        return any(result.error for result in self.odds_types.values())