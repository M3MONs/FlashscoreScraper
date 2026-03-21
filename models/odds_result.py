from dataclasses import dataclass
from typing import Any, Dict
from .odds_parser_result import OddsParserResult


@dataclass
class OddsResult:
    url: str
    data: Dict[str, Any] | OddsParserResult | None = None
    error: str | None = None

    def is_successful(self) -> bool:
        return self.error is None