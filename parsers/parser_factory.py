import importlib
import pkgutil
import logging
from pathlib import Path
from typing import Callable, Dict, Type
from parsers.base_parser import BaseParser


_registry: Dict[str, Type[BaseParser]] = {}


def register_parser(sport_type: str) -> Callable[..., type[BaseParser]]:
    """Decorator to register a parser class for a specific sport type"""
    def decorator(cls: Type[BaseParser]) -> Type[BaseParser]:
        _registry[sport_type] = cls
        return cls

    return decorator


def create_parser(sport_type: str) -> BaseParser:
    """Factory method to create parser instances based on sport type"""
    if sport_type in _registry:
        return _registry[sport_type]()
    else:
        raise ValueError(f"Unsupported sport type: {sport_type}")


def _load_parsers() -> None:
    """Dynamically load all parser modules in the current package"""
    current_file_stem = Path(__file__).stem
    package_dir = Path(__file__).parent
    
    for _, module_name, _ in pkgutil.iter_modules([str(package_dir)]):
        # Skip the current file
        if module_name == current_file_stem:
            continue

        try:
            importlib.import_module(f".{module_name}", package=__package__)
        except ImportError as e:
            logging.error(f"Failed to import parser module '{module_name}': {e}")
        except Exception as e:
            logging.exception(f"Unexpected error during module loading '{module_name}': {e}")

_load_parsers()
