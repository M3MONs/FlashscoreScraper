import importlib
import pkgutil
import logging
from pathlib import Path
from typing import Callable, Dict, Type
from .base_engine import BaseEngine


_registry: Dict[str, Type[BaseEngine]] = {}


def register_engine(engine_type: str) -> Callable[..., type[BaseEngine]]:
    """Decorator to register an engine class for a specific engine type"""

    def decorator(cls: Type[BaseEngine]) -> Type[BaseEngine]:
        _registry[engine_type] = cls
        return cls

    return decorator


def create_engine(engine_type: str, timeout: int = 10) -> BaseEngine:
    """Factory method to create engine instances based on engine type"""
    if engine_type in _registry:
        return _registry[engine_type](timeout)
    else:
        raise ValueError(f"Unknown engine type: {engine_type}. Available types: 'curl'")


def _load_engines() -> None:
    """Dynamically load all engine modules in the current package"""
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


_load_engines()
