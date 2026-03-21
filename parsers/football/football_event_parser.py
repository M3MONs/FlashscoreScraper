from dataclasses import dataclass
from typing import Dict
from bs4 import BeautifulSoup, Tag

from models.parse_text_element_params import ParseTextElementParams
from parsers.base_parser import BaseParser


@dataclass
class FootballEventData:
    date: str | None
    teams: Dict[str, Dict[str, str | None]]
    score: str | None
    detail_status: str | None
    league: Dict[str, str | None] | None


class FootballEventParser:
    @staticmethod
    def parse_event(soup: BeautifulSoup) -> FootballEventData | None:
        date = FootballEventParser.parse_event_date(soup)
        teams = FootballEventParser.parse_event_teams(soup)
        score = FootballEventParser.parse_event_score(soup)
        detail_status = FootballEventParser.parse_event_detail_status(soup)
        league = FootballEventParser.parse_event_league(soup)
        return FootballEventData(date=date, teams=teams, score=score, detail_status=detail_status, league=league)

    @staticmethod
    def parse_event_date(soup: BeautifulSoup) -> str:
        event_date_params = ParseTextElementParams(soup=soup, class_name="duelParticipant__startTime", html_tag="div", default_value="Unknown date")
        return BaseParser.parse_text_element(event_date_params)

    @staticmethod
    def parse_event_teams(soup: BeautifulSoup) -> Dict[str, Dict[str, str | None]]:
        team_elements = soup.find_all("div", class_="participant__participantName")
        team_img_elements = soup.find_all("a", class_="participant__participantLink--team")

        if len(team_elements) != 2:
            raise ValueError(f"Expected 2 team elements, found {len(team_elements)}")
        if len(team_img_elements) != 2:
            raise ValueError(f"Expected 2 team image elements, found {len(team_img_elements)}")

        return {
            role: FootballEventParser.build_team_info(name_el, link_el)
            for role, name_el, link_el in zip(
                ("home", "away"),
                team_elements,
                team_img_elements,
            )
        }

    @staticmethod
    def build_team_info(name_el: Tag, link_el: Tag) -> Dict[str, str | None]:
        img_tag = link_el.find("img")
        return {
            "name": name_el.get_text(strip=True),
            "img": str(img_tag.get("src")) if img_tag else None,
            "link": str(link_el.get("href")) if link_el.get("href") else None,
        }

    @staticmethod
    def parse_event_score(soup: BeautifulSoup) -> str | None:
        event_score_params = ParseTextElementParams(soup=soup, class_name="detailScore__wrapper", html_tag="div", default_value="Unknown score")
        return BaseParser.parse_text_element(event_score_params)

    @staticmethod
    def parse_event_detail_status(soup: BeautifulSoup) -> str | None:
        detail_status_params = ParseTextElementParams(
            soup=soup, class_name="fixedHeaderDuel__detailStatus", html_tag="span", default_value="Unknown status"
        )
        return BaseParser.parse_text_element(detail_status_params)

    @staticmethod
    def parse_event_league(soup: BeautifulSoup) -> Dict[str, str | None] | None:
        breadcrumbs = soup.find("div", class_="detail__breadcrumbs")
        if not breadcrumbs:
            return None

        items = breadcrumbs.find_all("li")
        if not items:
            return None

        last = items[-1]

        name = FootballEventParser.extract_league_name(last)
        link = FootballEventParser.extract_league_link(last)

        return {"name": name, "link": link}

    @staticmethod
    def extract_league_name(item: Tag) -> str | None:
        name_el = item.find(attrs={"itemprop": "name"}) or item.find("span") or item.find("a") or item
        return name_el.get_text(strip=True) if name_el else None

    @staticmethod
    def extract_league_link(item: Tag) -> str | None:
        a_tag = item.find("a", href=True)
        return str(a_tag.get("href")) if a_tag else None
