import importlib
import pkgutil
import logging


def _load_all_parsers() -> None:
    import parsers  # noqa: F401
    package = importlib.import_module(__name__)
    for _, name, _ in pkgutil.walk_packages(package.__path__, package.__name__ + "."):
        try:
            importlib.import_module(name)
        except Exception as e:
            logging.exception(f"Failed to import {name}: {e}")

_load_all_parsers()