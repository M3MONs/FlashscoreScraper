import pytest
from pathlib import Path
from parsers.football.football_event_parser import FootballEventParser
from models.event_data import EventData

FIXTURE_PATH = Path(__file__).parent.parent.parent / "fixtures" / "football_event.html"


@pytest.fixture(scope="module")
def fixture_path() -> str:
    return str(FIXTURE_PATH)


class TestFootballEventParser:
    def test_parse_event_returns_data(self, load_soup) -> None:
        result = FootballEventParser.parse_event(load_soup)
        assert result is not None
        assert isinstance(result, EventData)

    def test_date_is_not_default(self, load_soup) -> None:
        date = FootballEventParser.parse_event_date(load_soup)
        assert date != "Unknown date"
        assert len(date) > 5

    def test_two_teams_with_names(self, load_soup) -> None:
        participants = FootballEventParser.parse_event_teams(load_soup)
        assert len(participants) == 2
        assert participants[0]["role"] == "home"
        assert participants[1]["role"] == "away"
        assert participants[0]["name"] is not None
        assert len(participants[0]["name"]) > 0
        assert participants[1]["name"] is not None
        assert len(participants[1]["name"]) > 0

    def test_teams_have_images(self, load_soup) -> None:
        participants = FootballEventParser.parse_event_teams(load_soup)
        assert participants[0]["img"] is not None
        assert participants[1]["img"] is not None

    def test_teams_have_links(self, load_soup) -> None:
        participants = FootballEventParser.parse_event_teams(load_soup)
        assert participants[0]["link"] is not None
        assert participants[1]["link"] is not None

    def test_score_is_not_default(self, load_soup) -> None:
        score = FootballEventParser.parse_event_score(load_soup)
        assert score is not None
        assert score != "Unknown score"
        assert "-" in score

    def test_status_is_not_default(self, load_soup) -> None:
        status = FootballEventParser.parse_event_detail_status(load_soup)
        assert status is not None
        assert status != "Unknown status"
        assert len(status) > 0

    def test_league_exists(self, load_soup) -> None:
        league = FootballEventParser.parse_event_league(load_soup)
        assert league is not None
        assert league["name"] is not None
        assert len(league["name"]) > 0


class TestFootballEventParserExactValues:
    EXPECTED_DATE = "22.03.2026 15:15"
    EXPECTED_HOME_NAME = "Aston Villa"
    EXPECTED_AWAY_NAME = "West Ham"
    EXPECTED_HOME_IMG = "https://static.flashscore.com/res/image/data/QsnteKXg-jwz95gs0.png"
    EXPECTED_AWAY_IMG = "https://static.flashscore.com/res/image/data/Qo3RdMjl-Q9DJHs4l.png"
    EXPECTED_HOME_LINK = "/team/aston-villa/W00wmLO0/"
    EXPECTED_AWAY_LINK = "/team/west-ham/Cxq57r8g/"
    EXPECTED_SCORE = "2-0"
    EXPECTED_STATUS = "Finished"
    EXPECTED_LEAGUE_NAME = "Premier League - Round 31"
    EXPECTED_LEAGUE_LINK = "/football/england/premier-league/"

    def test_exact_date(self, load_soup) -> None:
        date = FootballEventParser.parse_event_date(load_soup)
        assert date == self.EXPECTED_DATE

    def test_exact_home_team(self, load_soup) -> None:
        participants = FootballEventParser.parse_event_teams(load_soup)
        home = participants[0]
        assert home["name"] == self.EXPECTED_HOME_NAME
        assert home["img"] == self.EXPECTED_HOME_IMG
        assert home["link"] == self.EXPECTED_HOME_LINK

    def test_exact_away_team(self, load_soup) -> None:
        participants = FootballEventParser.parse_event_teams(load_soup)
        away = participants[1]
        assert away["name"] == self.EXPECTED_AWAY_NAME
        assert away["img"] == self.EXPECTED_AWAY_IMG
        assert away["link"] == self.EXPECTED_AWAY_LINK

    def test_exact_score(self, load_soup) -> None:
        score = FootballEventParser.parse_event_score(load_soup)
        assert score == self.EXPECTED_SCORE

    def test_exact_status(self, load_soup) -> None:
        status = FootballEventParser.parse_event_detail_status(load_soup)
        assert status == self.EXPECTED_STATUS

    def test_exact_league(self, load_soup) -> None:
        league = FootballEventParser.parse_event_league(load_soup)
        assert league is not None
        assert league["name"] == self.EXPECTED_LEAGUE_NAME
        assert league["link"] == self.EXPECTED_LEAGUE_LINK
