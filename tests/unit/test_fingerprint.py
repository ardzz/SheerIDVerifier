"""Unit tests for fingerprint.py - FingerprintGenerator and data models."""

import pytest

from sheerid_verifier.utils.fingerprint import (
    DEFAULT_FINGERPRINT_CONFIG,
    FingerprintComponents,
    FingerprintConfig,
    FingerprintGenerator,
    HardwareConfig,
    MD5FingerprintStrategy,
    NavigatorConfig,
    ScreenConfig,
    SHA256FingerprintStrategy,
    TimezoneConfig,
    generate_fingerprint,
)


class TestScreenConfig:
    """Tests for ScreenConfig dataclass."""

    def test_default_values(self) -> None:
        """Test default screen configuration."""
        config = ScreenConfig()
        assert len(config.resolutions) > 0
        assert "1920x1080" in config.resolutions
        assert len(config.color_depths) > 0
        assert len(config.pixel_ratios) > 0

    def test_frozen(self) -> None:
        """Test that ScreenConfig is immutable."""
        config = ScreenConfig()
        with pytest.raises(Exception):  # FrozenInstanceError
            config.resolutions = ()  # type: ignore[misc]


class TestHardwareConfig:
    """Tests for HardwareConfig dataclass."""

    def test_default_values(self) -> None:
        """Test default hardware configuration."""
        config = HardwareConfig()
        assert len(config.cpu_cores) > 0
        assert len(config.memory_gb) > 0
        assert len(config.touch_support) > 0


class TestNavigatorConfig:
    """Tests for NavigatorConfig dataclass."""

    def test_default_values(self) -> None:
        """Test default navigator configuration."""
        config = NavigatorConfig()
        assert "Win32" in config.platforms
        assert "Google Inc." in config.vendors
        assert "en-US" in config.languages


class TestTimezoneConfig:
    """Tests for TimezoneConfig dataclass."""

    def test_default_values(self) -> None:
        """Test default timezone configuration."""
        config = TimezoneConfig()
        assert -8 in config.offsets  # PST
        assert 0 in config.offsets  # UTC


class TestFingerprintConfig:
    """Tests for FingerprintConfig dataclass."""

    def test_default_factory(self) -> None:
        """Test default config creates all sub-configs."""
        config = FingerprintConfig()
        assert isinstance(config.screen, ScreenConfig)
        assert isinstance(config.hardware, HardwareConfig)
        assert isinstance(config.navigator, NavigatorConfig)
        assert isinstance(config.timezone, TimezoneConfig)


class TestFingerprintComponents:
    """Tests for FingerprintComponents dataclass."""

    def test_to_string(self) -> None:
        """Test string serialization."""
        components = FingerprintComponents(
            timestamp=1234567890,
            random_seed=0.5,
            resolution="1920x1080",
            timezone_offset=-8,
            language="en-US",
            platform="Win32",
            vendor="Google Inc.",
            cpu_cores=8,
            memory_gb=16,
            touch_support=False,
            session_id="test-uuid",
        )
        result = components.to_string()

        assert "1234567890" in result
        assert "0.5" in result
        assert "1920x1080" in result
        assert "-8" in result
        assert "en-US" in result
        assert "Win32" in result
        assert "|" in result  # Delimiter


class TestMD5FingerprintStrategy:
    """Tests for MD5FingerprintStrategy."""

    def test_hash_returns_32_chars(self) -> None:
        """Test MD5 hash is correct length."""
        strategy = MD5FingerprintStrategy()
        components = FingerprintComponents(
            timestamp=1234567890,
            random_seed=0.5,
            resolution="1920x1080",
            timezone_offset=-8,
            language="en-US",
            platform="Win32",
            vendor="Google Inc.",
            cpu_cores=8,
            memory_gb=16,
            touch_support=False,
            session_id="test-uuid",
        )
        result = strategy.hash(components)

        assert len(result) == 32
        assert all(c in "0123456789abcdef" for c in result)

    def test_hash_deterministic(self) -> None:
        """Test same input produces same hash."""
        strategy = MD5FingerprintStrategy()
        components = FingerprintComponents(
            timestamp=1234567890,
            random_seed=0.5,
            resolution="1920x1080",
            timezone_offset=-8,
            language="en-US",
            platform="Win32",
            vendor="Google Inc.",
            cpu_cores=8,
            memory_gb=16,
            touch_support=False,
            session_id="test-uuid",
        )
        assert strategy.hash(components) == strategy.hash(components)


class TestSHA256FingerprintStrategy:
    """Tests for SHA256FingerprintStrategy."""

    def test_hash_returns_64_chars(self) -> None:
        """Test SHA256 hash is correct length."""
        strategy = SHA256FingerprintStrategy()
        components = FingerprintComponents(
            timestamp=1234567890,
            random_seed=0.5,
            resolution="1920x1080",
            timezone_offset=-8,
            language="en-US",
            platform="Win32",
            vendor="Google Inc.",
            cpu_cores=8,
            memory_gb=16,
            touch_support=False,
            session_id="test-uuid",
        )
        result = strategy.hash(components)

        assert len(result) == 64
        assert all(c in "0123456789abcdef" for c in result)


class TestFingerprintGenerator:
    """Tests for FingerprintGenerator class."""

    def test_generate_default(self) -> None:
        """Test default generator produces valid fingerprint."""
        generator = FingerprintGenerator()
        result = generator.generate()

        # MD5 produces 32 hex chars
        assert len(result) == 32
        assert all(c in "0123456789abcdef" for c in result)

    def test_generate_unique(self) -> None:
        """Test generator produces unique fingerprints."""
        generator = FingerprintGenerator()
        fp1 = generator.generate()
        fp2 = generator.generate()

        # Should be different due to random components
        assert fp1 != fp2

    def test_custom_strategy(self) -> None:
        """Test generator with custom strategy."""
        generator = FingerprintGenerator(strategy=SHA256FingerprintStrategy())
        result = generator.generate()

        # SHA256 produces 64 hex chars
        assert len(result) == 64

    def test_custom_config(self) -> None:
        """Test generator with custom configuration."""
        config = FingerprintConfig(
            screen=ScreenConfig(resolutions=("800x600",)),
            hardware=HardwareConfig(cpu_cores=(2,), memory_gb=(4,), touch_support=(False,)),
            navigator=NavigatorConfig(
                platforms=("TestPlatform",),
                vendors=("TestVendor",),
                languages=("test-lang",),
            ),
            timezone=TimezoneConfig(offsets=(0,)),
        )
        generator = FingerprintGenerator(config=config)
        result = generator.generate()

        assert len(result) == 32  # Still MD5 default


class TestGenerateFingerprint:
    """Tests for backwards-compatible generate_fingerprint function."""

    def test_returns_string(self) -> None:
        """Test that function returns a string."""
        result = generate_fingerprint()
        assert isinstance(result, str)

    def test_returns_32_chars(self) -> None:
        """Test that function returns MD5 hash length."""
        result = generate_fingerprint()
        assert len(result) == 32

    def test_returns_hex(self) -> None:
        """Test that function returns hex string."""
        result = generate_fingerprint()
        assert all(c in "0123456789abcdef" for c in result)


class TestDefaultConfig:
    """Tests for default configuration."""

    def test_default_fingerprint_config_exists(self) -> None:
        """Test that default config is properly initialized."""
        assert DEFAULT_FINGERPRINT_CONFIG is not None
        assert DEFAULT_FINGERPRINT_CONFIG.screen is not None
        assert DEFAULT_FINGERPRINT_CONFIG.hardware is not None
        assert DEFAULT_FINGERPRINT_CONFIG.navigator is not None
        assert DEFAULT_FINGERPRINT_CONFIG.timezone is not None
