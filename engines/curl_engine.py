from engines.base_engine import BaseEngine
from curl_cffi import requests

from engines.engine_factory import register_engine


""" INFO: Not working due to flashscore javascript rendering, but left for reference and future use if needed. """
@register_engine("curl")
class CurlEngine(BaseEngine):
    def __init__(self, timeout: int = 10) -> None:
        super().__init__(timeout)

    def _get_page(self, url: str, wait_for_selector: str | None = None) -> str:
        response = requests.get(url, timeout=self.timeout, impersonate="safari15_3")

        if response.status_code != 200:
            self.logger.warning(f"Received status code {response.status_code} for URL: {url}")

        if response.status_code == 403:
            self.logger.error(f"Error fetching {url}: 403 Forbidden (Cloudflare block)")

        return response.text

    def _get_pages(self, urls: dict[str, str], wait_for_selectors: dict[str, str | None] | None = None) -> dict[str, str]:
        return {key: self._get_page(url, wait_for_selector=wait_for_selectors.get(key) if wait_for_selectors else None) for key, url in urls.items()}

    def _close(self) -> None:
        pass
