import importlib
import pkgutil
import logging
from pathlib import Path
from typing import Callable, Dict, Type, TypeVar

from models.base_event_info import BaseEventInfo


TBaseEventInfo = TypeVar("TBaseEventInfo", bound=BaseEventInfo)

_event_info_registry: Dict[str, Type[BaseEventInfo]] = {}


def register_event_info(sport_type: str) -> Callable[[Type[TBaseEventInfo]], Type[TBaseEventInfo]]:
    """Decorator to register an event info enum class for a specific sport type."""

    def decorator(enum_cls: Type[TBaseEventInfo]) -> Type[TBaseEventInfo]:
        _event_info_registry[sport_type] = enum_cls
        return enum_cls

    return decorator


def get_event_info_enum(sport_type: str) -> Type[BaseEventInfo]:
    """Factory method to retrieve the event info enum class based on sport type."""
    if sport_type in _event_info_registry:
        return _event_info_registry[sport_type]
    raise ValueError(f"Unsupported sport type for event info: {sport_type}")


def _load_event_info() -> None:
    """Dynamically load all event info enum modules in the current package."""
    current_file_stem = Path(__file__).stem
    package_dir = Path(__file__).parent

    for _, module_name, _ in pkgutil.iter_modules([str(package_dir)]):
        # Skip the current file
        if module_name == current_file_stem:
            continue

        try:
            importlib.import_module(f".{module_name}", package=__package__)
        except ImportError as e:
            logging.error(f"Failed to import event info module '{module_name}': {e}")
        except Exception as e:
            logging.exception(f"Unexpected error during event info module loading '{module_name}': {e}")


_load_event_info()
