import asyncio
from typing import Any, Coroutine
from engines.base_engine import BaseEngine
from engines.engine_factory import register_engine
from playwright.async_api import Browser, BrowserContext, Page, Playwright


@register_engine("playwright")
class PlaywrightAsyncEngine(BaseEngine):
    def __init__(self, timeout: int = 10, max_concurrent: int = 4) -> None:
        super().__init__(timeout)
        self.max_concurrent = max_concurrent
        self._playwright: Playwright | None = None
        self._browser: Browser | None = None
        self._semaphore: asyncio.Semaphore = asyncio.Semaphore(max_concurrent)
        self._init_lock: asyncio.Lock = asyncio.Lock()
        self._loop: asyncio.AbstractEventLoop = asyncio.new_event_loop()

    async def _init_browser(self) -> None:
        async with self._init_lock:
            if self._browser is None:
                from playwright.async_api import async_playwright

                self.logger.debug("Starting Playwright and launching browser...")
                self._playwright = await async_playwright().start()
                self._browser = await self._playwright.chromium.launch(
                    headless=True,
                    args=[
                        "--disable-gpu",
                        "--disable-dev-shm-usage",
                        "--disable-extensions",
                        "--disable-background-networking",
                        "--disable-sync",
                        "--no-first-run",
                        "--no-default-browser-check",
                    ],
                )
                self.logger.debug("Browser launched successfully")

    async def _fetch_page_async(self, url: str, wait_for_selector: str | None = None) -> str:
        async with self._semaphore:
            await self._init_browser()
            context: BrowserContext = await self._browser.new_context()  # type: ignore
            page: Page = await context.new_page()

            async def _route_handler(route: Any, request: Any) -> None:
                if request.resource_type in {"image", "media", "font", "stylesheet"}:
                    await route.abort()
                else:
                    await route.continue_()

            await page.route("**/*", _route_handler)

            try:
                self.logger.debug("Fetching page: %s", url)
                wait_until = "load" if wait_for_selector else "networkidle"
                await page.goto(url, wait_until=wait_until, timeout=self.timeout * 1000)
                if wait_for_selector:
                    await page.wait_for_selector(wait_for_selector, timeout=self.timeout * 1000)
                content = await page.content()
                self.logger.debug("Successfully fetched page: %s", url)
                return content
            finally:
                await page.close()
                await context.close()

    async def fetch_pages_async(self, urls: dict[str, str], wait_for_selectors: dict[str, str | None] | None = None) -> dict[str, str]:
        wrap_tasks = [
            self._wrap_task(key, self._fetch_page_async(url, (wait_for_selectors or {}).get(key)))
            for key, url in urls.items()
        ]
        gathered: list[tuple[str, str] | BaseException] = await asyncio.gather(*wrap_tasks, return_exceptions=True)
        results: dict[str, str] = {}
        for item in gathered:
            if not isinstance(item, BaseException):
                key, result = item
                results[key] = result
        return results

    async def _wrap_task(self, key: str, coro: Coroutine[Any, Any, str]) -> tuple[str, str]:
        try:
            return (key, await coro)
        except Exception as e:
            self.logger.error("Failed to fetch %s: %s", key, e)
            return (key, "")

    def _get_page(self, url: str, wait_for_selector: str | None = None) -> str:
        return self._loop.run_until_complete(self._fetch_page_async(url, wait_for_selector))

    def _get_pages(self, urls: dict[str, str], wait_for_selectors: dict[str, str | None] | None = None) -> dict[str, str]:
        return self._loop.run_until_complete(self.fetch_pages_async(urls, wait_for_selectors))

    async def _async_close(self) -> None:
        if self._browser:
            await self._browser.close()
            self._browser = None
        if self._playwright:
            await self._playwright.stop()
            self._playwright = None

    def _close(self) -> None:
        self._loop.run_until_complete(self._async_close())
        self._cancel_pending_tasks()
        self._loop.close()

    def _cancel_pending_tasks(self) -> None:
        pending = asyncio.all_tasks(self._loop)
        for task in pending:
            task.cancel()
        if pending:
            self._loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
