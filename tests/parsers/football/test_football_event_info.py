import pytest
from pathlib import Path
from bs4 import BeautifulSoup

from parsers.football.football_event_info_parser import FootballEventInfoParser
from models.event_info_data import EventInfoData
from models.event_info.football_event_info import (
    FootballEventInfo,
    FootballFormEntry,
    FootballStandingsEntry,
    FootballDrawParticipant,
    FootballDrawMatch,
    FootballDrawRound,
)
from tests.parsers.soup_helpers import load_soup_from_path

STANDINGS_FIXTURE_PATH = Path(__file__).parent.parent.parent / "fixtures" / "football_event_info_standings.html"
DRAW_FIXTURE_PATH = Path(__file__).parent.parent.parent / "fixtures" / "football_event_info_draw.html"


@pytest.fixture(scope="module")
def standings_soup() -> BeautifulSoup:
    return load_soup_from_path(STANDINGS_FIXTURE_PATH)


@pytest.fixture(scope="module")
def standings_result(standings_soup: BeautifulSoup) -> EventInfoData:
    result = FootballEventInfoParser.parse_event_info(standings_soup, FootballEventInfo.STANDINGS.tab_label)
    assert result is not None
    return result


class TestFootballEventInfoParserStandings:
    def test_standings_in_detected_types(self, standings_soup: BeautifulSoup) -> None:
        types = FootballEventInfoParser.detect_available_types(standings_soup)
        assert FootballEventInfo.STANDINGS in types

    def test_parse_standings_returns_event_info_data(self, standings_result: EventInfoData) -> None:
        assert isinstance(standings_result, EventInfoData)

    def test_standings_info_type_is_standings(self, standings_result: EventInfoData) -> None:
        assert standings_result.info_type == FootballEventInfo.STANDINGS.tab_label

    def test_standings_data_is_list(self, standings_result: EventInfoData) -> None:
        assert isinstance(standings_result.data, list)

    def test_standings_has_20_entries(self, standings_result: EventInfoData) -> None:
        assert len(standings_result.data) == 20

    def test_standings_entries_are_correct_type(self, standings_result: EventInfoData) -> None:
        for entry in standings_result.data:
            assert isinstance(entry, FootballStandingsEntry)

    def test_standings_no_metadata_error(self, standings_result: EventInfoData) -> None:
        assert "error" not in standings_result.metadata

    def test_standings_highlighted_row_exists(self, standings_result: EventInfoData) -> None:
        highlighted = [e for e in standings_result.data if e.highlighted]
        assert len(highlighted) >= 1

    def test_standings_form_entries_are_correct_type(self, standings_result: EventInfoData) -> None:
        for entry in standings_result.data:
            assert isinstance(entry.form, list)
            for form_entry in entry.form:
                assert isinstance(form_entry, FootballFormEntry)

    def test_standings_all_teams_have_names(self, standings_result: EventInfoData) -> None:
        for entry in standings_result.data:
            assert entry.team is not None
            assert len(entry.team) > 0

    def test_standings_ranks_are_sequential(self, standings_result: EventInfoData) -> None:
        ranks = [entry.rank for entry in standings_result.data]
        assert ranks == list(range(1, 21))


class TestFootballEventInfoParserStandingsExactValues:
    FIRST_RANK = 1
    FIRST_PROMOTION_STATUS = "Promotion - Champions League (League phase)"
    FIRST_TEAM = "Barcelona"
    FIRST_TEAM_URL = "/team/barcelona/SKbpVP5K/"
    FIRST_MATCHES_PLAYED = "38"
    FIRST_WINS = "28"
    FIRST_DRAWS = "4"
    FIRST_LOSSES = "6"
    FIRST_GOALS_FOR = "102"
    FIRST_GOALS_AGAINST = "39"
    FIRST_GOAL_DIFFERENCE = "63"
    FIRST_POINTS = "88"
    FIRST_FORM = ["W", "L", "W", "W", "W"]
    FIRST_HIGHLIGHTED = False

    HIGHLIGHTED_RANK = 2
    HIGHLIGHTED_TEAM = "Real Madrid"
    HIGHLIGHTED_TEAM_URL = "/team/real-madrid/W8mj7MDD/"
    HIGHLIGHTED_MATCHES_PLAYED = "38"
    HIGHLIGHTED_WINS = "26"
    HIGHLIGHTED_DRAWS = "6"
    HIGHLIGHTED_LOSSES = "6"
    HIGHLIGHTED_GOALS_FOR = "78"
    HIGHLIGHTED_GOALS_AGAINST = "38"
    HIGHLIGHTED_GOAL_DIFFERENCE = "40"
    HIGHLIGHTED_POINTS = "84"

    LAST_RANK = 20
    LAST_PROMOTION_STATUS = "Relegation - LaLiga2"
    LAST_TEAM = "Valladolid"
    LAST_TEAM_URL = "/team/valladolid/zkpajjvm/"
    LAST_MATCHES_PLAYED = "38"
    LAST_WINS = "4"
    LAST_DRAWS = "4"
    LAST_LOSSES = "30"
    LAST_GOALS_FOR = "26"
    LAST_GOALS_AGAINST = "90"
    LAST_GOAL_DIFFERENCE = "-64"
    LAST_POINTS = "16"
    LAST_FORM = ["L", "L", "L", "L", "L"]
    LAST_HIGHLIGHTED = False

    def test_first_entry_rank(self, standings_result: EventInfoData) -> None:
        assert standings_result.data[0].rank == self.FIRST_RANK

    def test_first_entry_promotion_status(self, standings_result: EventInfoData) -> None:
        assert standings_result.data[0].promotion_status == self.FIRST_PROMOTION_STATUS

    def test_first_entry_team(self, standings_result: EventInfoData) -> None:
        assert standings_result.data[0].team == self.FIRST_TEAM

    def test_first_entry_team_url(self, standings_result: EventInfoData) -> None:
        assert standings_result.data[0].team_url == self.FIRST_TEAM_URL

    def test_first_entry_stats(self, standings_result: EventInfoData) -> None:
        entry = standings_result.data[0]
        assert entry.matches_played == self.FIRST_MATCHES_PLAYED
        assert entry.wins == self.FIRST_WINS
        assert entry.draws == self.FIRST_DRAWS
        assert entry.losses == self.FIRST_LOSSES
        assert entry.goals_for == self.FIRST_GOALS_FOR
        assert entry.goals_against == self.FIRST_GOALS_AGAINST
        assert entry.goal_difference == self.FIRST_GOAL_DIFFERENCE
        assert entry.points == self.FIRST_POINTS

    def test_first_entry_form(self, standings_result: EventInfoData) -> None:
        form = [f.result for f in standings_result.data[0].form]
        assert form == self.FIRST_FORM

    def test_first_entry_not_highlighted(self, standings_result: EventInfoData) -> None:
        assert standings_result.data[0].highlighted is self.FIRST_HIGHLIGHTED

    def test_highlighted_entry_rank_and_team(self, standings_result: EventInfoData) -> None:
        entry = standings_result.data[1]
        assert entry.rank == self.HIGHLIGHTED_RANK
        assert entry.team == self.HIGHLIGHTED_TEAM
        assert entry.team_url == self.HIGHLIGHTED_TEAM_URL
        assert entry.highlighted is True

    def test_highlighted_entry_stats(self, standings_result: EventInfoData) -> None:
        entry = standings_result.data[1]
        assert entry.matches_played == self.HIGHLIGHTED_MATCHES_PLAYED
        assert entry.wins == self.HIGHLIGHTED_WINS
        assert entry.draws == self.HIGHLIGHTED_DRAWS
        assert entry.losses == self.HIGHLIGHTED_LOSSES
        assert entry.goals_for == self.HIGHLIGHTED_GOALS_FOR
        assert entry.goals_against == self.HIGHLIGHTED_GOALS_AGAINST
        assert entry.goal_difference == self.HIGHLIGHTED_GOAL_DIFFERENCE
        assert entry.points == self.HIGHLIGHTED_POINTS

    def test_last_entry_rank(self, standings_result: EventInfoData) -> None:
        assert standings_result.data[-1].rank == self.LAST_RANK

    def test_last_entry_promotion_status(self, standings_result: EventInfoData) -> None:
        assert standings_result.data[-1].promotion_status == self.LAST_PROMOTION_STATUS

    def test_last_entry_team(self, standings_result: EventInfoData) -> None:
        assert standings_result.data[-1].team == self.LAST_TEAM

    def test_last_entry_team_url(self, standings_result: EventInfoData) -> None:
        assert standings_result.data[-1].team_url == self.LAST_TEAM_URL

    def test_last_entry_stats(self, standings_result: EventInfoData) -> None:
        entry = standings_result.data[-1]
        assert entry.matches_played == self.LAST_MATCHES_PLAYED
        assert entry.wins == self.LAST_WINS
        assert entry.draws == self.LAST_DRAWS
        assert entry.losses == self.LAST_LOSSES
        assert entry.goals_for == self.LAST_GOALS_FOR
        assert entry.goals_against == self.LAST_GOALS_AGAINST
        assert entry.goal_difference == self.LAST_GOAL_DIFFERENCE
        assert entry.points == self.LAST_POINTS

    def test_last_entry_form(self, standings_result: EventInfoData) -> None:
        form = [f.result for f in standings_result.data[-1].form]
        assert form == self.LAST_FORM

    def test_last_entry_not_highlighted(self, standings_result: EventInfoData) -> None:
        assert standings_result.data[-1].highlighted is self.LAST_HIGHLIGHTED


@pytest.fixture(scope="module")
def draw_soup() -> BeautifulSoup:
    if not DRAW_FIXTURE_PATH.exists():
        pytest.skip(f"Draw fixture not yet available: {DRAW_FIXTURE_PATH}")
    return load_soup_from_path(DRAW_FIXTURE_PATH)


@pytest.fixture(scope="module")
def draw_result(draw_soup: BeautifulSoup) -> EventInfoData:
    result = FootballEventInfoParser.parse_event_info(draw_soup, FootballEventInfo.DRAW.tab_label)
    assert result is not None
    return result


class TestFootballEventInfoParserDraw:
    def test_draw_in_detected_types(self, draw_soup: BeautifulSoup) -> None:
        types = FootballEventInfoParser.detect_available_types(draw_soup)
        assert FootballEventInfo.DRAW in types

    def test_parse_draw_returns_event_info_data(self, draw_result: EventInfoData) -> None:
        assert isinstance(draw_result, EventInfoData)

    def test_draw_info_type_is_draw(self, draw_result: EventInfoData) -> None:
        assert draw_result.info_type == FootballEventInfo.DRAW.tab_label

    def test_draw_data_is_not_none(self, draw_result: EventInfoData) -> None:
        assert draw_result.data is not None

    def test_draw_no_metadata_error(self, draw_result: EventInfoData) -> None:
        assert "error" not in draw_result.metadata

    def test_draw_data_is_list(self, draw_result: EventInfoData) -> None:
        assert isinstance(draw_result.data, list)

    def test_draw_rounds_are_correct_type(self, draw_result: EventInfoData) -> None:
        for round_ in draw_result.data:
            assert isinstance(round_, FootballDrawRound)

    def test_draw_matches_are_correct_type(self, draw_result: EventInfoData) -> None:
        for round_ in draw_result.data:
            for match in round_.matches:
                assert isinstance(match, FootballDrawMatch)

    def test_draw_participants_are_correct_type(self, draw_result: EventInfoData) -> None:
        for round_ in draw_result.data:
            for match in round_.matches:
                if match.home is not None:
                    assert isinstance(match.home, FootballDrawParticipant)
                if match.away is not None:
                    assert isinstance(match.away, FootballDrawParticipant)


class TestFootballEventInfoParserDrawExactValues:
    TOTAL_ROUNDS = 7
    ROUND_NAMES = [
        "1/64-finals",
        "1/32-finals",
        "1/16-finals",
        "1/8-finals",
        "Quarter-finals",
        "Semi-finals",
        "Final",
    ]
    ROUND_MATCH_COUNTS = [64, 32, 16, 8, 4, 2, 1]

    QF_INDEX = 4
    QF_HIGHLIGHTED_MATCH_INDEX = 3
    QF_HIGHLIGHTED_HOME = "Legia"
    QF_HIGHLIGHTED_AWAY = "Jagiellonia"

    FINAL_HOME = "Pogon Szczecin"
    FINAL_AWAY = "Legia"
    FINAL_HIGHLIGHTED = True

    FIRST_ROUND_EVENTLESS_COUNT = 54
    FIRST_ROUND_TWO_PARTICIPANT_COUNT = 10

    FIRST_64_MATCH_HOME = "Zaglebie Sosnowiec"
    FIRST_64_MATCH_AWAY = "Sandecja Nowy S."
    FIRST_64_MATCH_HOME_SCORE = "0"
    FIRST_64_MATCH_AWAY_SCORE = "1"
    FIRST_64_MATCH_HOME_ADVANCING = False
    FIRST_64_MATCH_AWAY_ADVANCING = True

    def test_total_rounds(self, draw_result: EventInfoData) -> None:
        assert len(draw_result.data) == self.TOTAL_ROUNDS

    def test_round_names(self, draw_result: EventInfoData) -> None:
        names = [r.round_name for r in draw_result.data]
        assert names == self.ROUND_NAMES

    def test_round_match_counts(self, draw_result: EventInfoData) -> None:
        counts = [len(r.matches) for r in draw_result.data]
        assert counts == self.ROUND_MATCH_COUNTS

    def test_first_round_eventless_count(self, draw_result: EventInfoData) -> None:
        first_round = draw_result.data[0]
        eventless = sum(1 for m in first_round.matches if m.is_eventless)
        assert eventless == self.FIRST_ROUND_EVENTLESS_COUNT

    def test_first_round_two_participant_matches(self, draw_result: EventInfoData) -> None:
        first_round = draw_result.data[0]
        two_participant = sum(
            1 for m in first_round.matches
            if m.home is not None and m.away is not None
        )
        assert two_participant == self.FIRST_ROUND_TWO_PARTICIPANT_COUNT

    def test_scores_parsed_for_completed_match(self, draw_result: EventInfoData) -> None:
        first_round = draw_result.data[0]
        match = next(m for m in first_round.matches if m.home is not None and m.away is not None)
        assert match.home.name == self.FIRST_64_MATCH_HOME
        assert match.away.name == self.FIRST_64_MATCH_AWAY
        assert match.home.score == self.FIRST_64_MATCH_HOME_SCORE
        assert match.away.score == self.FIRST_64_MATCH_AWAY_SCORE
        assert match.home.is_advancing is self.FIRST_64_MATCH_HOME_ADVANCING
        assert match.away.is_advancing is self.FIRST_64_MATCH_AWAY_ADVANCING

    def test_qf_highlighted_match(self, draw_result: EventInfoData) -> None:
        qf = draw_result.data[self.QF_INDEX]
        match = qf.matches[self.QF_HIGHLIGHTED_MATCH_INDEX]
        assert match.is_highlighted is True
        assert match.home is not None
        assert match.home.name == self.QF_HIGHLIGHTED_HOME
        assert match.away is not None
        assert match.away.name == self.QF_HIGHLIGHTED_AWAY

    def test_qf_highlighted_match_home_is_home(self, draw_result: EventInfoData) -> None:
        match = draw_result.data[self.QF_INDEX].matches[self.QF_HIGHLIGHTED_MATCH_INDEX]
        assert match.home.is_home is True
        assert match.away.is_home is False

    def test_qf_non_highlighted_matches(self, draw_result: EventInfoData) -> None:
        qf = draw_result.data[self.QF_INDEX]
        non_highlighted = [m for m in qf.matches if not m.is_highlighted]
        assert len(non_highlighted) == 3

    def test_final_match(self, draw_result: EventInfoData) -> None:
        final = draw_result.data[-1]
        assert len(final.matches) == 1
        match = final.matches[0]
        assert match.home is not None
        assert match.home.name == self.FINAL_HOME
        assert match.away is not None
        assert match.away.name == self.FINAL_AWAY
        assert match.is_highlighted is self.FINAL_HIGHLIGHTED

    def test_final_round_name(self, draw_result: EventInfoData) -> None:
        assert draw_result.data[-1].round_name == "Final"
