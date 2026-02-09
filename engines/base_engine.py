from abc import ABC, abstractmethod
import logging

class BaseEngine(ABC):
    def __init__(self, timeout: int = 10) -> None:
        self.timeout = timeout
        self.logger = logging.getLogger(self.__class__.__name__)
        
    @abstractmethod
    def get_page(self, url: str) -> str:
        raise NotImplementedError("get_page method must be implemented by subclasses")
    
    @abstractmethod
    def close(self) -> None:
        raise NotImplementedError("close method must be implemented by subclasses")
    
    def __enter__(self) -> "BaseEngine":
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()
