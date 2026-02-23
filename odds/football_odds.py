from odds.odds_factory import BaseOdds, register_odds
from utils.detect_sport import Sport


@register_odds(Sport.FOOTBALL.value)
class FootballOdds(BaseOdds):
    ONE_X_TWO = "1x2-odds"
    OVER_UNDER = "over-under"
    ASIAN_HANDICAP = "asian-handicap"
