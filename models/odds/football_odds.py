from models.odds.odds_factory import register_odds
from models.base_odds import BaseOdds
from utils.detect_sport import Sports


@register_odds(Sports.FOOTBALL.value)
class FootballOdds(BaseOdds):
    ONE_X_TWO = "1x2-odds"
    OVER_UNDER = "over-under"
    ASIAN_HANDICAP = "asian-handicap"
    BTTS = "both-teams-to-score"
    DOUBLE_CHANCE = "double-chance"
    EUROPEAN_HANDICAP = "european-handicap"
    DRAW_NO_BET = "draw-no-bet"
    CORRECT_SCORE = "correct-score"
    HT_FT = "ht-ft"
    ODD_EVEN = "odd-even"