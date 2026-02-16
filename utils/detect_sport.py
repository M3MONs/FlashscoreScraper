from enum import Enum

class Sport(Enum):
    FOOTBALL = "football"

# TODO: Improve sport detection logic to handle more sports and edge cases
def detect_sport_from_url(url: str) -> str:
    """Detects the sport type from the given URL."""
    if Sport.FOOTBALL.value in url.lower():
        return Sport.FOOTBALL.value
    else:
        raise ValueError(f"Cannot detect sport type from URL: {url}")
