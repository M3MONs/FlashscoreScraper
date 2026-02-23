import importlib
import pkgutil
import logging
from pathlib import Path
from typing import Callable, Dict, Type, TypeVar
from enum import Enum

class BaseOdds(Enum):
    """Base class for all odds enums."""
    pass

TBaseOdds = TypeVar("TBaseOdds", bound=BaseOdds)

_odds_registry: Dict[str, Type[BaseOdds]] = {}


def register_odds(sport_type: str) -> Callable[[Type[TBaseOdds]], Type[TBaseOdds]]:
    """Decorator to register an odds enum class for a specific sport type."""
    def decorator(enum_cls: Type[TBaseOdds]) -> Type[TBaseOdds]:
        _odds_registry[sport_type] = enum_cls
        return enum_cls
    return decorator


def get_odds_enum(sport_type: str) -> Type[BaseOdds]:
    """Factory method to retrieve the odds enum class based on sport type."""
    if sport_type in _odds_registry:
        return _odds_registry[sport_type]
    else:
        raise ValueError(f"Unsupported sport type: {sport_type}")
    

def _load_odds() -> None:
    """Dynamically load all odds enum modules in the current package."""
    current_file_stem = Path(__file__).stem
    package_dir = Path(__file__).parent

    for _, module_name, _ in pkgutil.iter_modules([str(package_dir)]):
        # Skip the current file
        if module_name == current_file_stem:
            continue

        try:
            importlib.import_module(f".{module_name}", package=__package__)
        except ImportError as e:
            logging.error(f"Failed to import engine module '{module_name}': {e}")
        except Exception as e:
            logging.exception(f"Unexpected error during engine module loading '{module_name}': {e}")

_load_odds()
        