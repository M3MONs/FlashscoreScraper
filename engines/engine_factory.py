from .base_engine import BaseEngine
from .curl_engine import CurlEngine


def create_engine(engine_type: str, timeout: int = 10) -> BaseEngine:
    if engine_type.lower() == "curl":
        return CurlEngine(timeout)
    else:
        raise ValueError(f"Unknown engine type: {engine_type}. Available types: 'curl'")