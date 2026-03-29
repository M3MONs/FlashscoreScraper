from dataclasses import dataclass, field


@dataclass
class OddsFilter:
    odds: list[str] = field(default_factory=list)
    bookmakers: list[str] = field(default_factory=list)
