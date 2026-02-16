from .base_engine import BaseEngine


def create_engine(engine_type: str, timeout: int = 10) -> BaseEngine:
    if engine_type.lower() == "curl":
        from .curl_engine import CurlEngine

        return CurlEngine(timeout)
    else:
        raise ValueError(f"Unknown engine type: {engine_type}. Available types: 'curl'")
