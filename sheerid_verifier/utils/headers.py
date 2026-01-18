"""HTTP header generation utilities using fake-useragent.

Implements Factory pattern with data-driven configuration following SOLID principles.
"""

from __future__ import annotations

import base64
import json
import random
import time
import uuid
from dataclasses import dataclass, field
from typing import Protocol

from fake_useragent import UserAgent

# Initialize UserAgent with fallback
_ua = UserAgent(
    fallback="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36"
)


# =============================================================================
# Data Models (DRY & SOLID)
# =============================================================================


@dataclass(frozen=True)
class BrowserBrand:
    """Browser brand for sec-ch-ua header."""

    name: str  # e.g., "Google Chrome", "Chromium"
    version: str  # e.g., "132"

    def to_sec_ch_ua(self) -> str:
        """Format as sec-ch-ua brand string."""
        return f'"{self.name}";v="{self.version}"'


@dataclass(frozen=True)
class PlatformConfig:
    """Platform configuration for HTTP headers."""

    os_name: str  # "Windows", "macOS", "Linux"
    sec_ch_ua_platform: str  # '"Windows"' (quoted for header)
    navigator_platform: str  # "Win32", "MacIntel", "Linux x86_64"
    brands: tuple[BrowserBrand, ...] = field(default_factory=tuple)

    def get_sec_ch_ua(self) -> str:
        """Get formatted sec-ch-ua header value."""
        return ", ".join(brand.to_sec_ch_ua() for brand in self.brands)


@dataclass(frozen=True)
class LanguageConfig:
    """Language preference configuration."""

    primary: str  # "en-US"
    accept_language: str  # "en-US,en;q=0.9"


@dataclass
class HeaderConfig:
    """Complete header configuration."""

    platforms: list[PlatformConfig]
    languages: list[LanguageConfig]
    chrome_versions: list[int]  # e.g., [131, 132, 133]
    client_version: str  # SheerID client version
    client_name: str  # SheerID client name


# =============================================================================
# Default Configuration Data
# =============================================================================

# Chrome versions to rotate through
DEFAULT_CHROME_VERSIONS = [131, 132, 133]


def _create_brands(chrome_version: int) -> tuple[BrowserBrand, ...]:
    """Create browser brands for a given Chrome version."""
    return (
        BrowserBrand(name="Chromium", version=str(chrome_version)),
        BrowserBrand(name="Google Chrome", version=str(chrome_version)),
        BrowserBrand(name="Not-A.Brand", version="24"),
    )


# Default platform configurations
DEFAULT_PLATFORMS: list[PlatformConfig] = [
    PlatformConfig(
        os_name="Windows",
        sec_ch_ua_platform='"Windows"',
        navigator_platform="Win32",
        brands=_create_brands(132),
    ),
    PlatformConfig(
        os_name="Windows",
        sec_ch_ua_platform='"Windows"',
        navigator_platform="Win32",
        brands=_create_brands(131),
    ),
    PlatformConfig(
        os_name="macOS",
        sec_ch_ua_platform='"macOS"',
        navigator_platform="MacIntel",
        brands=_create_brands(132),
    ),
    PlatformConfig(
        os_name="Linux",
        sec_ch_ua_platform='"Linux"',
        navigator_platform="Linux x86_64",
        brands=_create_brands(132),
    ),
]

# Default language configurations
DEFAULT_LANGUAGES: list[LanguageConfig] = [
    LanguageConfig(primary="en-US", accept_language="en-US,en;q=0.9"),
    LanguageConfig(primary="en-US", accept_language="en-US,en;q=0.9,es;q=0.8"),
    LanguageConfig(primary="en-GB", accept_language="en-GB,en;q=0.9"),
    LanguageConfig(primary="en-CA", accept_language="en-CA,en;q=0.9"),
    LanguageConfig(primary="en-AU", accept_language="en-AU,en;q=0.9"),
]

# Default header configuration
DEFAULT_HEADER_CONFIG = HeaderConfig(
    platforms=DEFAULT_PLATFORMS,
    languages=DEFAULT_LANGUAGES,
    chrome_versions=DEFAULT_CHROME_VERSIONS,
    client_version="2.158.0",
    client_name="jslib",
)


# =============================================================================
# Protocol (Dependency Inversion)
# =============================================================================


class HeaderGenerator(Protocol):
    """Protocol for header generation strategies."""

    def generate(self, *, for_sheerid: bool = True) -> dict[str, str]:
        """Generate HTTP headers."""
        ...


# =============================================================================
# NewRelic Header Generation
# =============================================================================


def generate_newrelic_headers() -> dict[str, str]:
    """
    Generate NewRelic tracking headers required by SheerID API.

    These headers make requests appear to come from real browsers
    instrumented with NewRelic monitoring.

    Returns:
        Dictionary with newrelic, traceparent, and tracestate headers
    """
    trace_id = (uuid.uuid4().hex + uuid.uuid4().hex[:8])[:32]
    span_id = uuid.uuid4().hex[:16]
    timestamp = int(time.time() * 1000)

    payload = {
        "v": [0, 1],
        "d": {
            "ty": "Browser",
            "ac": "364029",
            "ap": "134291347",
            "id": span_id,
            "tr": trace_id,
            "ti": timestamp,
        },
    }

    return {
        "newrelic": base64.b64encode(json.dumps(payload).encode()).decode(),
        "traceparent": f"00-{trace_id}-{span_id}-01",
        "tracestate": f"364029@nr=0-1-364029-134291347-{span_id}----{timestamp}",
    }


# =============================================================================
# Header Factory (Factory Pattern)
# =============================================================================


class HeaderFactory:
    """Factory for generating browser-like HTTP headers.

    Uses data-driven configuration for platforms, languages, and browser versions.
    Follows Open/Closed principle - extend by adding config, not modifying code.
    """

    def __init__(self, config: HeaderConfig | None = None) -> None:
        """Initialize factory with configuration.

        Args:
            config: Header configuration. Uses DEFAULT_HEADER_CONFIG if None.
        """
        self._config = config or DEFAULT_HEADER_CONFIG

    def create(self, *, for_sheerid: bool = True) -> dict[str, str]:
        """Generate browser-like HTTP headers.

        Args:
            for_sheerid: If True, include SheerID-specific headers and NewRelic tracking

        Returns:
            Dictionary of HTTP headers
        """
        ua = _ua.random
        platform = random.choice(self._config.platforms)
        language = random.choice(self._config.languages)

        # Base headers (proper ordering like real browser)
        headers = {
            "accept": "application/json, text/plain, */*",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": language.accept_language,
            "cache-control": "no-cache",
            "pragma": "no-cache",
            "sec-ch-ua": platform.get_sec_ch_ua(),
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": platform.sec_ch_ua_platform,
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": ua,
        }

        if for_sheerid:
            nr_headers = generate_newrelic_headers()
            headers.update(
                {
                    "content-type": "application/json",
                    "clientversion": self._config.client_version,
                    "clientname": self._config.client_name,
                    "origin": "https://services.sheerid.com",
                    "referer": "https://services.sheerid.com/",
                    **nr_headers,
                }
            )

        return headers


# =============================================================================
# Backwards-Compatible Functions
# =============================================================================

# Default factory instance
_default_factory = HeaderFactory()


def get_random_user_agent() -> str:
    """
    Get a random User-Agent string using fake-useragent library.

    Returns:
        Random browser User-Agent string
    """
    return _ua.random


def get_headers(*, for_sheerid: bool = True) -> dict[str, str]:
    """
    Generate browser-like HTTP headers with proper ordering.

    This is a backwards-compatible wrapper around HeaderFactory.

    Args:
        for_sheerid: If True, include SheerID-specific headers and NewRelic tracking

    Returns:
        Dictionary of HTTP headers
    """
    return _default_factory.create(for_sheerid=for_sheerid)
