from models.sports import Sports
from stats.base_stats_parser import BaseStatsParser
from stats.football_stats_parser import FootballStatsParser

# Sports supporting --with-stats. To add a sport: create stats/<sport>_stats_parser.py and register it here.
_STATS_PARSERS: dict[str, type[BaseStatsParser]] = {
    Sports.FOOTBALL.value: FootballStatsParser,
}


def get_stats_parser(sport_type: str) -> BaseStatsParser:
    """Returns the stats parser for the given sport, raises ValueError when the sport has no stats support."""
    if sport_type not in _STATS_PARSERS:
        raise ValueError(f"Stats are not supported for sport '{sport_type}'")
    return _STATS_PARSERS[sport_type]()
