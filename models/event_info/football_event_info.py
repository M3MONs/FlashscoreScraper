from models.base_event_info import BaseEventInfo
from models.event_info.event_info_factory import register_event_info
from utils.detect_sport import Sports


@register_event_info(Sports.FOOTBALL.value)
class FootballEventInfo(BaseEventInfo):
    STANDINGS = ("standings", "standings/standings/overall/")
    DRAW = ("draw", "draw/draw/")

    @property
    def tab_label(self) -> str:
        return self.value[0]

    @property
    def url_path(self) -> str:
        return self.value[1]
