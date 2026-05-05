from enum import Enum
from typing import NamedTuple


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


class GenericEventInfo(NamedTuple):
    """Fallback type when no sport-specific event info enum is registered."""

    tab_label: str
    url_path: str
    wait_for_selector: str | None = None
