import json
from dataclasses import asdict, is_dataclass
from typing import Dict, Any  

class JsonFormatter:
    @staticmethod
    def _convert_to_serializable(obj: Any) -> Any:
        if is_dataclass(obj) and not isinstance(obj, type):
            return asdict(obj)
        elif isinstance(obj, dict):
            return {key: JsonFormatter._convert_to_serializable(value) for key, value in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [JsonFormatter._convert_to_serializable(item) for item in obj]
        else:
            return obj

    @staticmethod
    def to_json(data: Dict[str, Any] | Any) -> str:
        data_dict = JsonFormatter._convert_to_serializable(data)
        return json.dumps(data_dict, indent=2, ensure_ascii=False)
