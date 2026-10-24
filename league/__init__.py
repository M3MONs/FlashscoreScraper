from league.base_league_parser import BaseLeagueParser
from league.football_league_parser import FootballLeagueParser
from models.sports import Sports

# Sports supporting `league`. To add a sport: create league/<sport>_league_parser.py and register it here.
_LEAGUE_PARSERS: dict[str, type[BaseLeagueParser]] = {
    Sports.FOOTBALL.value: FootballLeagueParser,
}


def get_league_parser(sport_type: str) -> BaseLeagueParser:
    """Returns the league parser for the given sport, raises ValueError when the sport has no league support."""
    if sport_type not in _LEAGUE_PARSERS:
        raise ValueError(f"League scraping is not supported for sport '{sport_type}'")
    return _LEAGUE_PARSERS[sport_type]()
