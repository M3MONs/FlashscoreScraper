from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class OddsParserResult:
    odds_type: str
    data: Any
    error: str | None

@dataclass
class OddsResult:
    url: str
    data: Dict[str, Any] | OddsParserResult | None = None
    error: str | None = None

    def is_successful(self) -> bool:
        return self.error is None


@dataclass
class FetchOddsResponse:
    event_url: str
    odds_types: Dict[str, OddsResult]

    def has_errors(self) -> bool:
        return any(result.error for result in self.odds_types.values())
