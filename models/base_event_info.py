from enum import Enum


class BaseEventInfo(Enum):
    """Base class for all event info type enums."""

    @property
    def tab_label(self) -> str:
        """Lowercase label of the tab as it appears in the UI."""
        raise NotImplementedError

    @property
    def url_path(self) -> str:
        """URL sub-path to append to the base event URL when fetching this type."""
        raise NotImplementedError

    @property
    def wait_for_selector(self) -> str | None:
        """Optional CSS selector to wait for before capturing page content."""
        return None
