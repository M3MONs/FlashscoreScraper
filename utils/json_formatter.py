import json
from typing import Dict, Any
from models import FetchOddsResponse


class JsonFormatter:
    @staticmethod
    def to_json(data: Dict[str, Any] | FetchOddsResponse) -> str:
        if isinstance(data, FetchOddsResponse):
            data_dict = {
                "event_url": data.event_url,
                "odds_types": {
                    odds_type: {
                        "url": result.url,
                        "data": result.data,
                        "error": result.error
                    }
                    for odds_type, result in data.odds_types.items()
                }
            }
        else:
            data_dict = data
        
        return json.dumps(data_dict, indent=2, ensure_ascii=False)