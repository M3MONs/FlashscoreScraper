from models.sports import Sports


# TODO: Improve sport detection logic to handle more sports and edge cases
def detect_sport_from_url(url: str) -> str:
    """Detects the sport type from the given URL."""
    for sport in Sports:
        if sport.value in url.lower():
            return sport.value
    raise ValueError(f"Cannot detect sport type from URL: {url}")
