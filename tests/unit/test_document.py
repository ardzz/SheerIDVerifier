"""Tests for document generation and caching functionality."""

from __future__ import annotations

import os
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch

from sheerid_verifier.services.document import (
    DocumentResult,
    _cache_document,
    _cleanup_old_cache,
    _ensure_cache_dir,
    generate_student_id,
    generate_transcript,
)


class TestDocumentResult:
    """Tests for DocumentResult dataclass."""

    def test_document_result_attributes(self) -> None:
        """Test DocumentResult has all expected attributes."""
        result = DocumentResult(
            data=b"test",
            method="pillow",
            doc_type="transcript",
            cached_path=Path("/tmp/test.png"),
        )

        assert result.data == b"test"
        assert result.method == "pillow"
        assert result.doc_type == "transcript"
        assert result.cached_path == Path("/tmp/test.png")

    def test_document_result_none_cached_path(self) -> None:
        """Test DocumentResult with None cached_path."""
        result = DocumentResult(
            data=b"test",
            method="playwright",
            doc_type="id_card",
            cached_path=None,
        )

        assert result.cached_path is None


class TestCacheHelpers:
    """Tests for cache helper functions."""

    def test_ensure_cache_dir_creates_directory(self, tmp_path: Path) -> None:
        """Test _ensure_cache_dir creates directory if not exists."""
        cache_dir = tmp_path / "cache" / "documents"

        with patch("sheerid_verifier.services.document.DOCUMENT_CACHE_DIR", str(cache_dir)):
            result = _ensure_cache_dir()

        assert result.exists()
        assert result.is_dir()

    def test_ensure_cache_dir_existing_directory(self, tmp_path: Path) -> None:
        """Test _ensure_cache_dir works with existing directory."""
        cache_dir = tmp_path / "cache" / "documents"
        cache_dir.mkdir(parents=True)

        with patch("sheerid_verifier.services.document.DOCUMENT_CACHE_DIR", str(cache_dir)):
            result = _ensure_cache_dir()

        assert result.exists()
        assert result == cache_dir

    def test_cache_document_creates_file(self, tmp_path: Path) -> None:
        """Test _cache_document creates file with correct content."""
        cache_dir = tmp_path / "cache" / "documents"
        test_data = b"PNG image data here"

        with patch("sheerid_verifier.services.document.DOCUMENT_CACHE_DIR", str(cache_dir)):
            result = _cache_document(test_data, "transcript", "abc123def456")

        assert result.exists()
        assert result.read_bytes() == test_data
        assert "transcript_" in result.name
        assert "_abc123de" in result.name  # First 8 chars of verification_id
        assert result.suffix == ".png"

    def test_cache_document_without_verification_id(self, tmp_path: Path) -> None:
        """Test _cache_document without verification ID."""
        cache_dir = tmp_path / "cache" / "documents"
        test_data = b"PNG image data here"

        with patch("sheerid_verifier.services.document.DOCUMENT_CACHE_DIR", str(cache_dir)):
            result = _cache_document(test_data, "id_card", None)

        assert result.exists()
        assert "id_card_" in result.name
        # No verification ID suffix - format: id_card_YYYYMMDD_HHMMSS.png
        assert result.name.count("_") == 3  # id, card, date, time

    def test_cleanup_old_cache_deletes_old_files(self, tmp_path: Path) -> None:
        """Test _cleanup_old_cache deletes files older than max_age_days."""
        cache_dir = tmp_path / "cache" / "documents"
        cache_dir.mkdir(parents=True)

        # Create old file (8 days ago)
        old_file = cache_dir / "transcript_old.png"
        old_file.write_bytes(b"old")
        old_time = (datetime.now() - timedelta(days=8)).timestamp()

        os.utime(old_file, (old_time, old_time))

        # Create new file
        new_file = cache_dir / "transcript_new.png"
        new_file.write_bytes(b"new")

        with patch("sheerid_verifier.services.document.DOCUMENT_CACHE_DIR", str(cache_dir)):
            deleted = _cleanup_old_cache(max_age_days=7)

        assert deleted == 1
        assert not old_file.exists()
        assert new_file.exists()

    def test_cleanup_old_cache_no_directory(self, tmp_path: Path) -> None:
        """Test _cleanup_old_cache handles missing directory."""
        cache_dir = tmp_path / "nonexistent"

        with patch("sheerid_verifier.services.document.DOCUMENT_CACHE_DIR", str(cache_dir)):
            deleted = _cleanup_old_cache()

        assert deleted == 0


class TestGenerateTranscript:
    """Tests for generate_transcript function."""

    def test_generate_transcript_returns_bytes(self, tmp_path: Path) -> None:
        """Test generate_transcript returns bytes by default."""
        cache_dir = tmp_path / "cache" / "documents"

        with patch("sheerid_verifier.services.document.DOCUMENT_CACHE_DIR", str(cache_dir)):
            result = generate_transcript(
                first_name="John",
                last_name="Doe",
                school_name="Test University",
                birth_date="2000-01-01",
            )

        assert isinstance(result, bytes)
        assert len(result) > 0
        # PNG magic bytes
        assert result[:8] == b"\x89PNG\r\n\x1a\n"

    def test_generate_transcript_returns_document_result(self, tmp_path: Path) -> None:
        """Test generate_transcript returns DocumentResult when return_info=True."""
        cache_dir = tmp_path / "cache" / "documents"

        with patch("sheerid_verifier.services.document.DOCUMENT_CACHE_DIR", str(cache_dir)):
            result = generate_transcript(
                first_name="John",
                last_name="Doe",
                school_name="Test University",
                birth_date="2000-01-01",
                return_info=True,
            )

        assert isinstance(result, DocumentResult)
        assert result.doc_type == "transcript"
        assert result.method in ("pillow", "playwright")
        assert isinstance(result.data, bytes)
        assert result.cached_path is not None
        assert result.cached_path.exists()

    def test_generate_transcript_with_verification_id(self, tmp_path: Path) -> None:
        """Test generate_transcript includes verification ID in cache filename."""
        cache_dir = tmp_path / "cache" / "documents"

        with patch("sheerid_verifier.services.document.DOCUMENT_CACHE_DIR", str(cache_dir)):
            result = generate_transcript(
                first_name="John",
                last_name="Doe",
                school_name="Test University",
                birth_date="2000-01-01",
                return_info=True,
                verification_id="abc123def456",
            )

        assert result.cached_path is not None
        assert "abc123de" in result.cached_path.name

    def test_generate_transcript_caching_disabled(self, tmp_path: Path) -> None:
        """Test generate_transcript respects DOCUMENT_CACHE_ENABLED=False."""
        cache_dir = tmp_path / "cache" / "documents"

        with (
            patch("sheerid_verifier.services.document.DOCUMENT_CACHE_DIR", str(cache_dir)),
            patch("sheerid_verifier.services.document.DOCUMENT_CACHE_ENABLED", False),
        ):
            result = generate_transcript(
                first_name="John",
                last_name="Doe",
                school_name="Test University",
                birth_date="2000-01-01",
                return_info=True,
            )

        assert result.cached_path is None
        assert not cache_dir.exists() or len(list(cache_dir.glob("*.png"))) == 0


class TestGenerateStudentId:
    """Tests for generate_student_id function."""

    def test_generate_student_id_returns_bytes(self, tmp_path: Path) -> None:
        """Test generate_student_id returns bytes by default."""
        cache_dir = tmp_path / "cache" / "documents"

        with patch("sheerid_verifier.services.document.DOCUMENT_CACHE_DIR", str(cache_dir)):
            result = generate_student_id(
                first_name="Jane",
                last_name="Smith",
                school_name="Test College",
            )

        assert isinstance(result, bytes)
        assert len(result) > 0
        # PNG magic bytes
        assert result[:8] == b"\x89PNG\r\n\x1a\n"

    def test_generate_student_id_returns_document_result(self, tmp_path: Path) -> None:
        """Test generate_student_id returns DocumentResult when return_info=True."""
        cache_dir = tmp_path / "cache" / "documents"

        with patch("sheerid_verifier.services.document.DOCUMENT_CACHE_DIR", str(cache_dir)):
            result = generate_student_id(
                first_name="Jane",
                last_name="Smith",
                school_name="Test College",
                return_info=True,
            )

        assert isinstance(result, DocumentResult)
        assert result.doc_type == "id_card"
        assert result.method == "pillow"  # Student ID always uses Pillow
        assert isinstance(result.data, bytes)
        assert result.cached_path is not None
        assert result.cached_path.exists()

    def test_generate_student_id_with_verification_id(self, tmp_path: Path) -> None:
        """Test generate_student_id includes verification ID in cache filename."""
        cache_dir = tmp_path / "cache" / "documents"

        with patch("sheerid_verifier.services.document.DOCUMENT_CACHE_DIR", str(cache_dir)):
            result = generate_student_id(
                first_name="Jane",
                last_name="Smith",
                school_name="Test College",
                return_info=True,
                verification_id="xyz789abc123",
            )

        assert result.cached_path is not None
        assert "xyz789ab" in result.cached_path.name


class TestMethodLogging:
    """Tests for method logging."""

    def test_transcript_method_is_pillow_when_playwright_unavailable(self, tmp_path: Path) -> None:
        """Test transcript generation uses Pillow when Playwright is unavailable."""
        cache_dir = tmp_path / "cache" / "documents"

        with (
            patch("sheerid_verifier.services.document.DOCUMENT_CACHE_DIR", str(cache_dir)),
            patch(
                "sheerid_verifier.services.document._is_playwright_available", return_value=False
            ),
        ):
            result = generate_transcript(
                first_name="John",
                last_name="Doe",
                school_name="Test University",
                birth_date="2000-01-01",
                return_info=True,
            )

        assert result.method == "pillow"

    def test_student_id_always_uses_pillow(self, tmp_path: Path) -> None:
        """Test student ID generation always uses Pillow."""
        cache_dir = tmp_path / "cache" / "documents"

        with patch("sheerid_verifier.services.document.DOCUMENT_CACHE_DIR", str(cache_dir)):
            result = generate_student_id(
                first_name="Jane",
                last_name="Smith",
                school_name="Test College",
                return_info=True,
            )

        assert result.method == "pillow"
