import posixpath
from urllib.parse import urlparse, urlunparse


class FlashscoreUrlBuilder:
    @staticmethod
    def build_odds_url(event_url: str, odds_key: str) -> str:
        parsed = urlparse(event_url)
        new_path = posixpath.join(parsed.path, "odds", odds_key)
        parsed = parsed._replace(path=new_path, query="", fragment="")
        return urlunparse(parsed)
