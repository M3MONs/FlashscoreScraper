import logging

from bs4 import BeautifulSoup, Tag

from league.base_league_parser import BaseLeagueParser
from models.league_match import LeagueMatch


class FootballLeagueParser(BaseLeagueParser):
    match_selector = "div.event__match"
    load_more_selector = "button:has-text('Show more matches')"

    def __init__(self) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)

    def parse(self, data: str) -> list[LeagueMatch]:
        """Returns matches in page order; a round header applies to the matches following it."""
        soup = BeautifulSoup(data, "html.parser")
        matches = []
        current_round = None

        for element in soup.select(f"div.event__round, {self.match_selector}"):
            if "event__round" in element.get_attribute_list("class"):
                current_round = element.get_text(strip=True)
                continue
            try:
                matches.append(self._parse_match(element, current_round))
            except (ValueError, AttributeError) as e:
                self.logger.warning(f"Skipping league match row with unexpected layout: {e}")

        return matches

    def _parse_match(self, row: Tag, round_name: str | None) -> LeagueMatch:
        link = row.select_one("a.eventRowLink")
        if link is None or not link.get("href"):
            raise ValueError("match row without link")

        scheduled = "event__match--scheduled" in row.get_attribute_list("class")
        return LeagueMatch(
            event_url=str(link["href"]),
            status="scheduled" if scheduled else "finished",
            round=round_name,
            date=self._text(row, ".event__stageTime"),
            home=self._text(row, ".event__homeParticipant"),
            away=self._text(row, ".event__awayParticipant"),
            score_home=None if scheduled else self._score(row, ".event__score--home"),
            score_away=None if scheduled else self._score(row, ".event__score--away"),
        )

    @staticmethod
    def _text(row: Tag, selector: str) -> str:
        element = row.select_one(selector)
        if element is None:
            raise ValueError(f"missing {selector}")
        return element.get_text(strip=True)

    @classmethod
    def _score(cls, row: Tag, selector: str) -> int | None:
        text = cls._text(row, selector)
        return int(text) if text.isdigit() else None
