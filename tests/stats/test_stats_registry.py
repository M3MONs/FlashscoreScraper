import pytest

from stats import get_stats_parser
from stats.football_stats_parser import FootballStatsParser


class TestStatsRegistry:
    def test_football_is_supported(self) -> None:
        assert isinstance(get_stats_parser("football"), FootballStatsParser)

    def test_unsupported_sport_raises(self) -> None:
        with pytest.raises(ValueError, match="volleyball"):
            get_stats_parser("volleyball")
