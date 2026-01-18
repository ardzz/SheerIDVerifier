"""Browser fingerprint generation utilities.

Implements Strategy pattern with data-driven configuration following SOLID principles.
"""

from __future__ import annotations

import hashlib
import random
import time
import uuid
from dataclasses import dataclass, field
from typing import Protocol

# =============================================================================
# Data Models (DRY & SOLID)
# =============================================================================


@dataclass(frozen=True)
class ScreenConfig:
    """Screen resolution and display configuration options."""

    resolutions: tuple[str, ...] = (
        "1920x1080",
        "1366x768",
        "1536x864",
        "1440x900",
        "1280x720",
        "2560x1440",
        "1600x900",
        "1680x1050",
        "1280x800",
        "1024x768",
    )
    color_depths: tuple[int, ...] = (24, 30, 32)
    pixel_ratios: tuple[float, ...] = (1.0, 1.5, 2.0)


@dataclass(frozen=True)
class HardwareConfig:
    """Hardware configuration options."""

    cpu_cores: tuple[int, ...] = (2, 4, 6, 8, 12, 16)
    memory_gb: tuple[int, ...] = (4, 8, 16, 32)
    touch_support: tuple[bool, ...] = (False, True)


@dataclass(frozen=True)
class NavigatorConfig:
    """Browser navigator configuration options."""

    platforms: tuple[str, ...] = ("Win32", "MacIntel", "Linux x86_64")
    vendors: tuple[str, ...] = ("Google Inc.", "Apple Computer, Inc.")
    languages: tuple[str, ...] = (
        "en-US",
        "en-GB",
        "en-CA",
        "en-AU",
        "es-ES",
        "fr-FR",
        "de-DE",
        "pt-BR",
    )


@dataclass(frozen=True)
class TimezoneConfig:
    """Timezone configuration options."""

    offsets: tuple[float, ...] = (-8, -7, -6, -5, -4, -3, 0, 1, 2, 3, 5.5, 8, 9, 10)


@dataclass
class FingerprintConfig:
    """Complete fingerprint configuration."""

    screen: ScreenConfig = field(default_factory=ScreenConfig)
    hardware: HardwareConfig = field(default_factory=HardwareConfig)
    navigator: NavigatorConfig = field(default_factory=NavigatorConfig)
    timezone: TimezoneConfig = field(default_factory=TimezoneConfig)


# Default configuration instance
DEFAULT_FINGERPRINT_CONFIG = FingerprintConfig()


# =============================================================================
# Fingerprint Components (intermediate representation)
# =============================================================================


@dataclass
class FingerprintComponents:
    """Generated fingerprint component values.

    This is the intermediate representation before hashing.
    """

    timestamp: int
    random_seed: float
    resolution: str
    timezone_offset: float
    language: str
    platform: str
    vendor: str
    cpu_cores: int
    memory_gb: int
    touch_support: bool
    session_id: str

    def to_string(self) -> str:
        """Convert components to string for hashing."""
        return "|".join(
            [
                str(self.timestamp),
                str(self.random_seed),
                self.resolution,
                str(self.timezone_offset),
                self.language,
                self.platform,
                self.vendor,
                str(self.cpu_cores),
                str(self.memory_gb),
                str(int(self.touch_support)),
                self.session_id,
            ]
        )


# =============================================================================
# Protocol (Strategy Pattern - Dependency Inversion)
# =============================================================================


class FingerprintStrategy(Protocol):
    """Protocol for fingerprint hashing strategies."""

    def hash(self, components: FingerprintComponents) -> str:
        """Hash fingerprint components to produce final fingerprint.

        Args:
            components: Generated fingerprint components

        Returns:
            Fingerprint hash string
        """
        ...


# =============================================================================
# Strategy Implementations
# =============================================================================


class MD5FingerprintStrategy:
    """MD5-based fingerprint hashing strategy.

    This is the default strategy matching the original implementation.
    """

    def hash(self, components: FingerprintComponents) -> str:
        """Hash components using MD5.

        Args:
            components: Generated fingerprint components

        Returns:
            32-character hexadecimal MD5 hash
        """
        return hashlib.md5(components.to_string().encode()).hexdigest()


class SHA256FingerprintStrategy:
    """SHA256-based fingerprint hashing strategy.

    Provides stronger hashing for environments that require it.
    """

    def hash(self, components: FingerprintComponents) -> str:
        """Hash components using SHA256.

        Args:
            components: Generated fingerprint components

        Returns:
            64-character hexadecimal SHA256 hash
        """
        return hashlib.sha256(components.to_string().encode()).hexdigest()


# =============================================================================
# Fingerprint Generator (Factory + Strategy)
# =============================================================================


class FingerprintGenerator:
    """Generator for browser fingerprints.

    Uses Strategy pattern for hashing algorithm and data-driven configuration
    for component generation. Follows Open/Closed principle - extend by adding
    new strategies or config, not modifying code.
    """

    def __init__(
        self,
        config: FingerprintConfig | None = None,
        strategy: FingerprintStrategy | None = None,
    ) -> None:
        """Initialize generator with configuration and strategy.

        Args:
            config: Fingerprint configuration. Uses DEFAULT_FINGERPRINT_CONFIG if None.
            strategy: Hashing strategy. Uses MD5FingerprintStrategy if None.
        """
        self._config = config or DEFAULT_FINGERPRINT_CONFIG
        self._strategy = strategy or MD5FingerprintStrategy()

    def _generate_components(self) -> FingerprintComponents:
        """Generate random fingerprint components from configuration.

        Returns:
            FingerprintComponents with randomly selected values
        """
        return FingerprintComponents(
            timestamp=int(time.time() * 1000),
            random_seed=random.random(),
            resolution=random.choice(self._config.screen.resolutions),
            timezone_offset=random.choice(self._config.timezone.offsets),
            language=random.choice(self._config.navigator.languages),
            platform=random.choice(self._config.navigator.platforms),
            vendor=random.choice(self._config.navigator.vendors),
            cpu_cores=random.choice(self._config.hardware.cpu_cores),
            memory_gb=random.choice(self._config.hardware.memory_gb),
            touch_support=random.choice(self._config.hardware.touch_support),
            session_id=str(uuid.uuid4()),
        )

    def generate(self) -> str:
        """Generate a browser fingerprint hash.

        Combines various browser characteristics into a hash that mimics
        real browser fingerprinting used for fraud detection.

        Returns:
            Fingerprint hash string (format depends on strategy)
        """
        components = self._generate_components()
        return self._strategy.hash(components)


# =============================================================================
# Backwards-Compatible Functions
# =============================================================================

# Default generator instance
_default_generator = FingerprintGenerator()


def generate_fingerprint() -> str:
    """
    Generate a realistic browser fingerprint hash.

    This is a backwards-compatible wrapper around FingerprintGenerator.

    Combines various browser characteristics into an MD5 hash that mimics
    real browser fingerprinting used for fraud detection.

    Returns:
        32-character hexadecimal fingerprint string
    """
    return _default_generator.generate()
