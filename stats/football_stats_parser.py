import logging

from bs4 import BeautifulSoup, Tag

from stats.base_stats_parser import BaseStatsParser


class FootballStatsParser(BaseStatsParser):
    url_path = "summary/stats/"
    wait_for_selector = "div[data-testid='wcl-statistics']"

    def __init__(self) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)

    def parse(self, data: str) -> dict[str, list[dict[str, str]]]:
        """Returns stats rows grouped by section header, e.g. {"Top stats": [{"category", "home", "away"}]}."""
        soup = BeautifulSoup(data, "html.parser")
        stats = {}

        for group in soup.find_all("div", attrs={"data-testid": "statGroup"}):
            header = group.find(attrs={"data-testid": "wcl-headerSection-text"})
            rows = self._parse_rows(group.find_all("div", attrs={"data-testid": "wcl-statistics"}))
            if header and rows:
                stats[header.get_text(strip=True)] = rows

        if not stats:
            raise ValueError("No stats available")

        return stats

    def _parse_rows(self, rows: list[Tag]) -> list[dict[str, str]]:
        """Parses each stats row, logging and skipping rows with an unexpected layout."""
        results = []
        for row in rows:
            try:
                results.append(self._parse_row(row))
            except (ValueError, AttributeError) as e:
                self.logger.warning(f"Skipping stats row with unexpected layout: {e}")
        return results

    def _parse_row(self, row: Tag) -> dict[str, str]:
        """Row layout: label row with three cells - home value, category label, away value."""
        label_row = row.find("div")
        assert label_row is not None
        home, label, away = label_row.find_all("div", recursive=False)
        return {
            "category": label.get_text(strip=True),
            "home": home.get_text(" ", strip=True),
            "away": away.get_text(" ", strip=True),
        }
