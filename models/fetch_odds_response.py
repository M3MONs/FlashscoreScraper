from dataclasses import dataclass
from models.odds_result import OddsResult


@dataclass
class FetchOddsResponse:
    event_url: str
    # TODO: ADD event_id
    odds: list[OddsResult]

    def has_errors(self) -> bool:
        return any(getattr(result, "error", None) for result in self.odds)
