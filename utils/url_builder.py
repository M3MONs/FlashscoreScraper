import posixpath
from urllib.parse import urlparse, urlunparse

FLASHSCORE_URL = "https://www.flashscore.com"
LEAGUE_SECTIONS = ("results", "fixtures")


class FlashscoreUrlBuilder:
    @staticmethod
    def build_odds_url(event_url: str, odds_key: str) -> str:
        parsed = urlparse(event_url)
        new_path = posixpath.join(parsed.path, "odds", odds_key)
        parsed = parsed._replace(path=new_path, query="", fragment="")
        return urlunparse(parsed)

    @staticmethod
    def build_event_info_url(event_url: str, url_path: str) -> str:
        parsed = urlparse(event_url)
        base_path = parsed.path.rstrip("/") + "/"
        new_path = posixpath.join(base_path, url_path)
        parsed = parsed._replace(path=new_path, fragment="")
        return urlunparse(parsed)

    @staticmethod
    def build_league_url(sport: str, league: str, section: str) -> str:
        """Builds https://www.flashscore.com/<sport>/<league>/<section>/ from example 'germany/bundesliga' or a full league URL."""
        path = urlparse(league).path if "://" in league else league
        segments = [segment for segment in path.split("/") if segment]
        if segments and segments[0] == sport:
            segments = segments[1:]
        if segments and segments[-1] in LEAGUE_SECTIONS:
            segments = segments[:-1]
        return f"{FLASHSCORE_URL}/" + "/".join([sport, *segments, section]) + "/"
