from engines.base_engine import BaseEngine
from engines.engine_factory import register_engine


@register_engine("playwright")
class PlaywrightEngine(BaseEngine):
    def __init__(self, timeout: int = 10) -> None:
        super().__init__(timeout)
        from playwright.sync_api import sync_playwright
        self._playwright = sync_playwright().start()
        self._browser = self._playwright.chromium.launch(headless=True)
        self._page = self._browser.new_page()

    def _get_page(self, url: str) -> str:
        self._page.goto(url, wait_until="networkidle", timeout=self.timeout * 1000)
        return self._page.content()

    def _close(self) -> None:
        self._browser.close()
        self._playwright.stop()