from tests.scraper.test_scraper_service_stats import EVENT_URL, STATS_URL, _read_fixture, _service


class TestScraperServiceEventUrl:
    def test_event_contains_event_url(self) -> None:
        service, _ = _service("football", {EVENT_URL: _read_fixture("event.html")})
        result = service.fetch_and_parse_event(EVENT_URL)
        assert result["event_url"] == EVENT_URL

    def test_event_with_stats_contains_event_url(self) -> None:
        service, _ = _service("football", {EVENT_URL: _read_fixture("event.html"), STATS_URL: _read_fixture("stats.html")})
        result = service.fetch_and_parse_event_with_stats(EVENT_URL)
        assert result["event_url"] == EVENT_URL
        assert "stats" in result

    def test_event_info_without_tabs_contains_event_url(self) -> None:
        service, _ = _service("football", {EVENT_URL: "<html></html>"})
        assert service.fetch_and_parse_event_info(EVENT_URL) == {"event_url": EVENT_URL}

    def test_event_fetch_error_keeps_error_payload(self) -> None:
        service, _ = _service("football", {})
        result = service.fetch_and_parse_event(EVENT_URL)
        assert "event_url" not in result
        assert result["url"] == EVENT_URL
        assert "error" in result
