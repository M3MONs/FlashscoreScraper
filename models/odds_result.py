from dataclasses import dataclass
from models.odds_parser_row import OddsParserRow


@dataclass
class OddsResult:
    url: str
    odd_type: str
    data: list[OddsParserRow] | None
    error: str | None = None

    def is_successful(self) -> bool:
        return self.error is None
