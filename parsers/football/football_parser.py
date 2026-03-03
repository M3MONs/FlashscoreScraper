from bs4 import BeautifulSoup, Tag
from typing import Dict, Any
from parsers.base_odds_parser import BaseOddsParser
from parsers.base_parser import BaseParser
from utils.detect_sport import Sport


class FootballParser(BaseParser, sport_type=Sport.FOOTBALL.value):
    def _parse_event(self, url: str, data: Any) -> Dict[str, Any]:
        self.logger.debug(f"Parsing football event from URL: {url}")

        soup = BeautifulSoup(data, 'html.parser')

        date = self._parse_event_date(soup)
        teams = self._parse_event_teams(soup)
        score = self._parse_event_score(soup)
        detail_status = self._parse_event_detail_status(soup)
        league = self._parse_event_league(soup)

        return {"date": date, "teams": teams, "score": score, "detail_status": detail_status, "league": league}

    def _parse_event_info(self, url: str, data: Any) -> Dict[str, Any]:
        self.logger.debug(f"Parsing football event info from URL: {url}")
        return {"event_info": "football_event_info_data"}

    def _parse_odds(self, url: str, data: Any, odds_type: str) -> Dict[str, Any]:
        self.logger.debug(f"Parsing football odds from URL: {url}")
        parser = BaseOddsParser.create(
            Sport.FOOTBALL.value,
            odds_type
        )
        if parser is None:
            self.logger.warning(f"No parser implemented for odds type: '{odds_type}'")
            return {"odds_type": odds_type, "data": None, "error": "not_implemented"}
        
        return parser.parse(url, data)
    
    # --- Event Parsing ---

    def _parse_event_date(self, soup: BeautifulSoup) -> str | None:
        return self._parse_text_element(soup, 'duelParticipant__startTime', "div", "Unknown date")

    def _parse_event_teams(self, soup: BeautifulSoup) -> Dict[str, Dict[str, str | None]]:
        team_elements = soup.find_all('div', class_='participant__participantName')
        team_img_elements = soup.find_all('a', class_='participant__participantLink--team')

        if len(team_elements) != 2:
            raise ValueError(f"Expected 2 team elements, found {len(team_elements)}")
        if len(team_img_elements) != 2:
            raise ValueError(f"Expected 2 team image elements, found {len(team_img_elements)}")

        return {
            role: self._build_team_info(name_el, link_el)
            for role, name_el, link_el in zip(
                ('home', 'away'),
                team_elements,
                team_img_elements,
            )
        }
    
    def _build_team_info(self, name_el: Tag, link_el: Tag) -> Dict[str, str | None]:
        img_tag = link_el.find('img')
        return {
            "name": name_el.get_text(strip=True),
            "img": str(img_tag.get('src')) if img_tag else None,
            "link": str(link_el.get('href')) if link_el.get('href') else None,
        }
    
    def _parse_event_score(self, soup: BeautifulSoup) -> str | None:
        return self._parse_text_element(soup, 'detailScore__wrapper', "div", "Unknown score")
        
    def _parse_event_detail_status(self, soup: BeautifulSoup) -> str | None:
        return self._parse_text_element(soup, 'fixedHeaderDuel__detailStatus', "span", "Unknown status")
    
    def _parse_event_league(self, soup: BeautifulSoup) -> Dict[str, str | None] | None:
        breadcrumbs = soup.find('div', class_='detail__breadcrumbs')
        if not breadcrumbs:
            return None

        items = breadcrumbs.find_all('li')
        if not items:
            return None

        last = items[-1]
        
        name = self._extract_league_name(last)
        link = self._extract_league_link(last)
        
        return {"name": name, "link": link}
    
    def _extract_league_name(self, item: Tag) -> str | None:
        name_el = (
            item.find(attrs={'itemprop': 'name'}) or
            item.find('span') or
            item.find('a') or
            item
        )
        return name_el.get_text(strip=True) if name_el else None
    
    def _extract_league_link(self, item: Tag) -> str | None:
        a_tag = item.find('a', href=True)
        return str(a_tag.get('href')) if a_tag else None