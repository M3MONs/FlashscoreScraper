from dataclasses import dataclass, field
from typing import Any, Generic, TypeVar


T = TypeVar("T")


@dataclass
class EventInfoData(Generic[T]):
    info_type: str
    data: T
    metadata: dict[str, Any] = field(default_factory=dict)
