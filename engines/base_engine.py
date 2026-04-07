from abc import ABC, abstractmethod
import logging


class BaseEngine(ABC):
    def __init__(self, timeout: int = 10) -> None:
        self.timeout = timeout
        self.logger = logging.getLogger(self.__class__.__name__)

    def get_page(self, url: str, wait_for_selector: str | None = None) -> str:
        self.logger.debug(f"Fetching page: {url} with timeout: {self.timeout}")
        result = self._get_page(url, wait_for_selector)
        self.logger.debug(f"Successfully fetched page: {url}")
        return result

    def get_pages(self, urls: dict[str, str], wait_for_selectors: dict[str, str | None] | None = None) -> dict[str, str]:
        self.logger.debug(f"Fetching multiple pages with timeout: {self.timeout}")
        results = self._get_pages(urls, wait_for_selectors)
        self.logger.debug("Successfully fetched multiple pages")
        return results

    def _get_page(self, url: str, wait_for_selector: str | None = None) -> str:
        """Internal method to fetch page content with error handling"""
        raise NotImplementedError("_get_page method must be implemented by subclasses")

    def _get_pages(self, urls: dict[str, str], wait_for_selectors: dict[str, str | None] | None = None) -> dict[str, str]:
        """Internal method to fetch multiple pages with error handling"""
        raise NotImplementedError("_get_pages method must be implemented by subclasses")

    def close(self) -> None:
        self.logger.info(f"Closing {self.__class__.__name__}")
        self._close()

    @abstractmethod
    def _close(self) -> None:
        """Internal method to close resources with error handling"""
        raise NotImplementedError("_close method must be implemented by subclasses")

    def __enter__(self) -> "BaseEngine":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()
