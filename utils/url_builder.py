import posixpath
from urllib.parse import urlparse, urlunparse


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
        parsed = parsed._replace(path=new_path, query="", fragment="")
        return urlunparse(parsed)
