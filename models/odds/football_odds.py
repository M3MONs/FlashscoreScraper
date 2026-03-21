from models.odds.odds_factory import register_odds
from models.base_odds import BaseOdds
from utils.detect_sport import Sports


@register_odds(Sports.FOOTBALL.value)
class FootballOdds(BaseOdds):
    ONE_X_TWO = "1x2-odds"
    OVER_UNDER = "over-under"
    ASIAN_HANDICAP = "asian-handicap"
