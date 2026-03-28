from dataclasses import dataclass

@dataclass
class OddsParserRowData:
    value: str
    type: str
    odds: str

@dataclass
class OddsParserRow:
    bookmaker_id: str | None
    bookmaker_name: str
    bookmaker_link: str | None
    odds_values: list[OddsParserRowData]