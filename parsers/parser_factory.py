from parsers.base_parser import BaseParser
from utils.detect_sport import Sport


def create_parser(sport_type: str) -> BaseParser:
    if sport_type == Sport.FOOTBALL.value:
        from parsers.football_parser import FootballParser

        return FootballParser()
    else:
        raise ValueError(f"Unsupported sport type: {sport_type}")
