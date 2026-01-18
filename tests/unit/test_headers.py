"""Unit tests for headers.py - HeaderFactory and data models."""

import pytest

from sheerid_verifier.utils.headers import (
    DEFAULT_HEADER_CONFIG,
    BrowserBrand,
    HeaderConfig,
    HeaderFactory,
    LanguageConfig,
    PlatformConfig,
    generate_newrelic_headers,
    get_headers,
)


class TestBrowserBrand:
    """Tests for BrowserBrand dataclass."""

    def test_to_sec_ch_ua(self) -> None:
        """Test sec-ch-ua formatting."""
        brand = BrowserBrand(name="Google Chrome", version="132")
        assert brand.to_sec_ch_ua() == '"Google Chrome";v="132"'

    def test_frozen(self) -> None:
        """Test that BrowserBrand is immutable."""
        brand = BrowserBrand(name="Chrome", version="132")
        with pytest.raises(Exception):  # FrozenInstanceError
            brand.name = "Firefox"  # type: ignore[misc]


class TestPlatformConfig:
    """Tests for PlatformConfig dataclass."""

    def test_get_sec_ch_ua(self) -> None:
        """Test sec-ch-ua generation from brands."""
        platform = PlatformConfig(
            os_name="Windows",
            sec_ch_ua_platform='"Windows"',
            navigator_platform="Win32",
            brands=(
                BrowserBrand("Chromium", "132"),
                BrowserBrand("Google Chrome", "132"),
            ),
        )
        result = platform.get_sec_ch_ua()
        assert '"Chromium";v="132"' in result
        assert '"Google Chrome";v="132"' in result


class TestLanguageConfig:
    """Tests for LanguageConfig dataclass."""

    def test_attributes(self) -> None:
        """Test language config attributes."""
        lang = LanguageConfig(primary="en-US", accept_language="en-US,en;q=0.9")
        assert lang.primary == "en-US"
        assert lang.accept_language == "en-US,en;q=0.9"


class TestHeaderFactory:
    """Tests for HeaderFactory class."""

    def test_create_default_headers(self) -> None:
        """Test creating headers with default config."""
        factory = HeaderFactory()
        headers = factory.create()

        # Check required SheerID headers
        assert "user-agent" in headers
        assert "sec-ch-ua" in headers
        assert "sec-ch-ua-platform" in headers
        assert "accept-language" in headers
        assert "newrelic" in headers
        assert "traceparent" in headers
        assert "clientversion" in headers
        assert "clientname" in headers

    def test_create_non_sheerid_headers(self) -> None:
        """Test creating headers without SheerID-specific fields."""
        factory = HeaderFactory()
        headers = factory.create(for_sheerid=False)

        # Should NOT have SheerID-specific headers
        assert "newrelic" not in headers
        assert "clientversion" not in headers
        assert "clientname" not in headers

        # Should still have browser headers
        assert "user-agent" in headers
        assert "sec-ch-ua" in headers

    def test_custom_config(self) -> None:
        """Test factory with custom configuration."""
        config = HeaderConfig(
            platforms=[
                PlatformConfig(
                    os_name="TestOS",
                    sec_ch_ua_platform='"TestOS"',
                    navigator_platform="Test",
                    brands=(BrowserBrand("TestBrowser", "1"),),
                )
            ],
            languages=[LanguageConfig(primary="test", accept_language="test;q=1")],
            chrome_versions=[999],
            client_version="1.0.0",
            client_name="test",
        )
        factory = HeaderFactory(config)
        headers = factory.create()

        assert headers["sec-ch-ua-platform"] == '"TestOS"'
        assert headers["accept-language"] == "test;q=1"
        assert headers["clientversion"] == "1.0.0"


class TestNewRelicHeaders:
    """Tests for NewRelic header generation."""

    def test_generate_newrelic_headers(self) -> None:
        """Test NewRelic header structure."""
        headers = generate_newrelic_headers()

        assert "newrelic" in headers
        assert "traceparent" in headers
        assert "tracestate" in headers

        # Check traceparent format: 00-<trace_id>-<span_id>-01
        assert headers["traceparent"].startswith("00-")
        assert headers["traceparent"].endswith("-01")

    def test_newrelic_headers_unique(self) -> None:
        """Test that NewRelic headers are unique each call."""
        h1 = generate_newrelic_headers()
        h2 = generate_newrelic_headers()

        assert h1["traceparent"] != h2["traceparent"]
        assert h1["newrelic"] != h2["newrelic"]


class TestGetHeaders:
    """Tests for backwards-compatible get_headers function."""

    def test_get_headers_returns_dict(self) -> None:
        """Test that get_headers returns a dictionary."""
        headers = get_headers()
        assert isinstance(headers, dict)
        assert len(headers) > 0

    def test_get_headers_for_sheerid(self) -> None:
        """Test get_headers with SheerID mode."""
        headers = get_headers(for_sheerid=True)
        assert "newrelic" in headers

    def test_get_headers_not_for_sheerid(self) -> None:
        """Test get_headers without SheerID mode."""
        headers = get_headers(for_sheerid=False)
        assert "newrelic" not in headers


class TestDefaultConfig:
    """Tests for default configuration."""

    def test_default_header_config_exists(self) -> None:
        """Test that default config is properly initialized."""
        assert DEFAULT_HEADER_CONFIG is not None
        assert len(DEFAULT_HEADER_CONFIG.platforms) > 0
        assert len(DEFAULT_HEADER_CONFIG.languages) > 0
        assert len(DEFAULT_HEADER_CONFIG.chrome_versions) > 0
