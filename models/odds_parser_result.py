from dataclasses import dataclass
from typing import Any

@dataclass
class OddsParserResult:
    odds_type: str
    data: Any
    error: str | None