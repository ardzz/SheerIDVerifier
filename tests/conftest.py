"""Pytest fixtures for SheerID Verifier tests."""

import pytest

from sheerid_verifier.models.university import University
from sheerid_verifier.services.stats import Stats


@pytest.fixture
def temp_stats(tmp_path):
    """Create a Stats instance with temporary file."""
    return Stats(stats_file=tmp_path / "test_stats.json")


@pytest.fixture
def sample_university():
    """Create a sample university for testing."""
    return University(
        id=12345,
        name="Test University",
        domain="test.edu",
        weight=50,
    )
