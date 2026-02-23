from engines.base_engine import BaseEngine
from curl_cffi import requests

from engines.engine_factory import register_engine


""" INFO: Not working due to flashscore javascript rendering, but left for reference and future use if needed. """
@register_engine("curl")
class CurlEngine(BaseEngine):
    def __init__(self, timeout: int = 10) -> None:
        super().__init__(timeout)

    def get_page(self, url: str) -> str:
        response = requests.get(url, timeout=self.timeout, impersonate="safari15_3")

        if response.status_code != 200:
            self.logger.warning(f"Received status code {response.status_code} for URL: {url}")

        if response.status_code == 403:
            self.logger.error(f"Error fetching {url}: 403 Forbidden (Cloudflare block)")

        return response.text

    def close(self) -> None:
        pass
