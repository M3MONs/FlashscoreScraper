import json
from dataclasses import asdict, is_dataclass
from typing import Dict, Any
from models import FetchOddsResponse


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
    def to_json(data: Dict[str, Any] | FetchOddsResponse) -> str:
        if isinstance(data, FetchOddsResponse):
            data_dict = {
                "event_url": data.event_url,
                "odds_types": {
                    odds_type: {
                        "url": result.url,
                        "data": JsonFormatter._convert_to_serializable(result.data),
                        "error": result.error,
                    }
                    for odds_type, result in data.odds_types.items()
                },
            }
        else:
            data_dict = JsonFormatter._convert_to_serializable(data)

        return json.dumps(data_dict, indent=2, ensure_ascii=False)
