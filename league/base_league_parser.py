from abc import ABC, abstractmethod

from models.league_match import LeagueMatch


class BaseLeagueParser(ABC):
    """Base class for sport-specific league results/fixtures page parsers."""

    match_selector: str
    load_more_selector: str | None = None

    @abstractmethod
    def parse(self, data: str) -> list[LeagueMatch]:
        """Parses a league results or fixtures page into matches."""
