"""Document generation service with Playwright/Pillow backends.

This module generates fake academic documents (transcripts, student IDs) for
verification purposes. It supports two rendering backends:

1. Playwright (default): Renders HTML template to PNG using headless Chromium.
   Produces high-quality, realistic "student portal" screenshots.

2. Pillow (fallback): Generates simpler images using PIL/Pillow.
   Used when Playwright is not available.

The backend is auto-detected: Playwright is tried first, with automatic
fallback to Pillow if unavailable.

Document Caching:
- Generated documents can be cached to disk for inspection
- Cache location: ./cache/documents/
- Files older than DOCUMENT_CACHE_MAX_AGE_DAYS are auto-cleaned
- Use return_info=True to get DocumentResult with cache path and method info
"""

from __future__ import annotations

import logging
import random
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from io import BytesIO
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal, overload

from PIL import Image, ImageDraw, ImageFont

from sheerid_verifier.config import (
    DOCUMENT_CACHE_DIR,
    DOCUMENT_CACHE_ENABLED,
    DOCUMENT_CACHE_MAX_AGE_DAYS,
    ID_CARD_HEIGHT,
    ID_CARD_WIDTH,
    TRANSCRIPT_HEIGHT,
    TRANSCRIPT_VIEWPORT_HEIGHT,
    TRANSCRIPT_VIEWPORT_WIDTH,
    TRANSCRIPT_WIDTH,
)
from sheerid_verifier.data.transcript import Transcript
from sheerid_verifier.data.transcript import generate_transcript as generate_transcript_data

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


# =============================================================================
# Data Classes
# =============================================================================


@dataclass
class DocumentResult:
    """Result of document generation with metadata.

    Attributes:
        data: The generated PNG image as bytes
        method: Rendering method used ("playwright" or "pillow")
        doc_type: Document type ("transcript" or "id_card")
        cached_path: Path where document was cached, or None if caching disabled
    """

    data: bytes
    method: str
    doc_type: str
    cached_path: Path | None


# =============================================================================
# Cache Helpers
# =============================================================================


def _ensure_cache_dir() -> Path:
    """Ensure cache directory exists and return its path."""
    cache_dir = Path(DOCUMENT_CACHE_DIR)
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def _cleanup_old_cache(max_age_days: int = DOCUMENT_CACHE_MAX_AGE_DAYS) -> int:
    """Delete cached documents older than max_age_days.

    Args:
        max_age_days: Maximum age in days before files are deleted

    Returns:
        Number of files deleted
    """
    cache_dir = Path(DOCUMENT_CACHE_DIR)
    if not cache_dir.exists():
        return 0

    cutoff = datetime.now() - timedelta(days=max_age_days)
    deleted = 0

    try:
        for file_path in cache_dir.glob("*.png"):
            try:
                mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                if mtime < cutoff:
                    file_path.unlink()
                    deleted += 1
                    logger.debug(f"Deleted old cache file: {file_path}")
            except OSError as e:
                logger.warning(f"Failed to delete cache file {file_path}: {e}")
    except OSError as e:
        logger.warning(f"Failed to cleanup cache directory: {e}")

    if deleted > 0:
        logger.info(f"Cleaned up {deleted} old cached document(s)")

    return deleted


def _cache_document(
    data: bytes,
    doc_type: str,
    verification_id: str | None = None,
) -> Path:
    """Save document to cache directory.

    Args:
        data: PNG image bytes to cache
        doc_type: Document type ("transcript" or "id_card")
        verification_id: Optional verification ID for filename

    Returns:
        Path where document was cached
    """
    cache_dir = _ensure_cache_dir()

    # Generate filename: {doc_type}_{YYYYMMDD}_{HHMMSS}_{vid_prefix}.png
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    vid_suffix = f"_{verification_id[:8]}" if verification_id else ""
    filename = f"{doc_type}_{timestamp}{vid_suffix}.png"

    file_path = cache_dir / filename
    file_path.write_bytes(data)

    logger.info(f"Cached document: {file_path}")
    return file_path


def _is_playwright_available() -> bool:
    """Check if Playwright backend is available."""
    try:
        from sheerid_verifier.services.html_renderer import is_playwright_available

        return is_playwright_available()
    except ImportError:
        return False


# =============================================================================
# Transcript Generation
# =============================================================================


@overload
def generate_transcript(
    first_name: str,
    last_name: str,
    school_name: str,
    birth_date: str,
    *,
    return_info: Literal[False] = False,
    verification_id: str | None = None,
) -> bytes: ...


@overload
def generate_transcript(
    first_name: str,
    last_name: str,
    school_name: str,
    birth_date: str,
    *,
    return_info: Literal[True],
    verification_id: str | None = None,
) -> DocumentResult: ...


def generate_transcript(
    first_name: str,
    last_name: str,
    school_name: str,
    birth_date: str,
    *,
    return_info: bool = False,
    verification_id: str | None = None,
) -> bytes | DocumentResult:
    """
    Generate a fake academic transcript image.

    Uses Playwright (HTML→PNG) by default for high-quality output.
    Falls back to Pillow if Playwright is not available.

    Args:
        first_name: Student's first name
        last_name: Student's last name
        school_name: University/college name
        birth_date: Student's birth date (YYYY-MM-DD)
        return_info: If True, return DocumentResult with metadata; otherwise return bytes
        verification_id: Optional verification ID for cache filename

    Returns:
        PNG image data as bytes, or DocumentResult if return_info=True
    """
    # Cleanup old cache files (non-blocking)
    if DOCUMENT_CACHE_ENABLED:
        _cleanup_old_cache()

    # Generate dynamic transcript data
    transcript = generate_transcript_data(performance="good")
    student_id = str(random.randint(10000000, 99999999))

    method: str = "pillow"
    data: bytes

    # Try Playwright first, fall back to Pillow
    if _is_playwright_available():
        try:
            data = _generate_transcript_playwright(
                first_name=first_name,
                last_name=last_name,
                school_name=school_name,
                transcript=transcript,
                student_id=student_id,
            )
            method = "playwright"
            logger.info(f"Generated transcript using Playwright ({len(data)} bytes)")
        except Exception as e:
            logger.warning(f"Playwright rendering failed, falling back to Pillow: {e}")
            data = _generate_transcript_pillow(
                first_name=first_name,
                last_name=last_name,
                school_name=school_name,
                birth_date=birth_date,
                transcript=transcript,
                student_id=student_id,
            )
            method = "pillow"
            logger.info(f"Generated transcript using Pillow ({len(data)} bytes)")
    else:
        # Pillow fallback
        data = _generate_transcript_pillow(
            first_name=first_name,
            last_name=last_name,
            school_name=school_name,
            birth_date=birth_date,
            transcript=transcript,
            student_id=student_id,
        )
        logger.info(f"Generated transcript using Pillow ({len(data)} bytes)")

    # Cache document if enabled
    cached_path: Path | None = None
    if DOCUMENT_CACHE_ENABLED:
        cached_path = _cache_document(data, "transcript", verification_id)

    if return_info:
        return DocumentResult(
            data=data,
            method=method,
            doc_type="transcript",
            cached_path=cached_path,
        )

    return data


@overload
async def generate_transcript_async(
    first_name: str,
    last_name: str,
    school_name: str,
    birth_date: str,
    *,
    return_info: Literal[False] = False,
    verification_id: str | None = None,
) -> bytes: ...


@overload
async def generate_transcript_async(
    first_name: str,
    last_name: str,
    school_name: str,
    birth_date: str,
    *,
    return_info: Literal[True],
    verification_id: str | None = None,
) -> DocumentResult: ...


async def generate_transcript_async(
    first_name: str,
    last_name: str,
    school_name: str,
    birth_date: str,
    *,
    return_info: bool = False,
    verification_id: str | None = None,
) -> bytes | DocumentResult:
    """
    Generate a fake academic transcript image (async version).

    Uses Playwright async API for non-blocking rendering.
    Falls back to sync Pillow if Playwright is not available.

    Args:
        first_name: Student's first name
        last_name: Student's last name
        school_name: University/college name
        birth_date: Student's birth date (YYYY-MM-DD)
        return_info: If True, return DocumentResult with metadata; otherwise return bytes
        verification_id: Optional verification ID for cache filename

    Returns:
        PNG image data as bytes, or DocumentResult if return_info=True
    """
    # Cleanup old cache files (non-blocking)
    if DOCUMENT_CACHE_ENABLED:
        _cleanup_old_cache()

    # Generate dynamic transcript data
    transcript = generate_transcript_data(performance="good")
    student_id = str(random.randint(10000000, 99999999))

    method: str = "pillow"
    data: bytes

    # Try Playwright async first
    if _is_playwright_available():
        try:
            data = await _generate_transcript_playwright_async(
                first_name=first_name,
                last_name=last_name,
                school_name=school_name,
                transcript=transcript,
                student_id=student_id,
            )
            method = "playwright"
            logger.info(f"Generated transcript using Playwright async ({len(data)} bytes)")
        except Exception as e:
            logger.warning(f"Playwright async rendering failed, falling back to Pillow: {e}")
            data = _generate_transcript_pillow(
                first_name=first_name,
                last_name=last_name,
                school_name=school_name,
                birth_date=birth_date,
                transcript=transcript,
                student_id=student_id,
            )
            method = "pillow"
            logger.info(f"Generated transcript using Pillow ({len(data)} bytes)")
    else:
        # Pillow fallback (sync, but still works in async context)
        data = _generate_transcript_pillow(
            first_name=first_name,
            last_name=last_name,
            school_name=school_name,
            birth_date=birth_date,
            transcript=transcript,
            student_id=student_id,
        )
        logger.info(f"Generated transcript using Pillow ({len(data)} bytes)")

    # Cache document if enabled
    cached_path: Path | None = None
    if DOCUMENT_CACHE_ENABLED:
        cached_path = _cache_document(data, "transcript", verification_id)

    if return_info:
        return DocumentResult(
            data=data,
            method=method,
            doc_type="transcript",
            cached_path=cached_path,
        )

    return data


def _generate_transcript_playwright(
    first_name: str,
    last_name: str,
    school_name: str,
    transcript: Transcript,
    student_id: str,
) -> bytes:
    """Generate transcript using Playwright HTML renderer."""
    from sheerid_verifier.services.html_renderer import render_html_to_png
    from sheerid_verifier.services.transcript_html import generate_transcript_html

    # Generate HTML from template
    html_content = generate_transcript_html(
        school_name=school_name,
        student_name=f"{first_name} {last_name}",
        student_id=student_id,
        major=transcript.major.name,
        semesters=transcript.get_courses_by_semester(),
        cumulative_gpa=transcript.gpa,
        total_credits=transcript.total_credits,
    )

    # Render to PNG
    return render_html_to_png(
        html_content=html_content,
        viewport_width=TRANSCRIPT_VIEWPORT_WIDTH,
        viewport_height=TRANSCRIPT_VIEWPORT_HEIGHT,
        full_page=True,
    )


async def _generate_transcript_playwright_async(
    first_name: str,
    last_name: str,
    school_name: str,
    transcript: Transcript,
    student_id: str,
) -> bytes:
    """Generate transcript using Playwright HTML renderer (async)."""
    from sheerid_verifier.services.html_renderer import render_html_to_png_async
    from sheerid_verifier.services.transcript_html import generate_transcript_html

    # Generate HTML from template
    html_content = generate_transcript_html(
        school_name=school_name,
        student_name=f"{first_name} {last_name}",
        student_id=student_id,
        major=transcript.major.name,
        semesters=transcript.get_courses_by_semester(),
        cumulative_gpa=transcript.gpa,
        total_credits=transcript.total_credits,
    )

    # Render to PNG (async)
    return await render_html_to_png_async(
        html_content=html_content,
        viewport_width=TRANSCRIPT_VIEWPORT_WIDTH,
        viewport_height=TRANSCRIPT_VIEWPORT_HEIGHT,
        full_page=True,
    )


def _generate_transcript_pillow(
    first_name: str,
    last_name: str,
    school_name: str,
    birth_date: str,
    transcript: Transcript,
    student_id: str,
) -> bytes:
    """Generate transcript using Pillow (fallback)."""
    w, h = TRANSCRIPT_WIDTH, TRANSCRIPT_HEIGHT
    img = Image.new("RGB", (w, h), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    font_header, font_title, font_text, font_bold = _get_fonts()

    # Header
    draw.text((w // 2, 50), school_name.upper(), fill=(0, 0, 0), font=font_header, anchor="mm")
    draw.text(
        (w // 2, 90),
        "OFFICIAL ACADEMIC TRANSCRIPT",
        fill=(50, 50, 50),
        font=font_title,
        anchor="mm",
    )
    draw.line([(50, 110), (w - 50, 110)], fill=(0, 0, 0), width=2)

    # Student info
    y = 150
    draw.text((50, y), f"Student Name: {first_name} {last_name}", fill=(0, 0, 0), font=font_bold)
    draw.text((w - 300, y), f"Student ID: {student_id}", fill=(0, 0, 0), font=font_text)
    y += 30
    draw.text((50, y), f"Date of Birth: {birth_date}", fill=(0, 0, 0), font=font_text)
    draw.text(
        (w - 300, y), f"Date Issued: {time.strftime('%Y-%m-%d')}", fill=(0, 0, 0), font=font_text
    )
    y += 25
    draw.text((50, y), f"Major: {transcript.major.name}", fill=(0, 0, 0), font=font_text)
    y += 35

    # Current enrollment status
    draw.rectangle([(50, y), (w - 50, y + 40)], fill=(240, 240, 240))
    draw.text(
        (w // 2, y + 20),
        "CURRENT STATUS: ENROLLED",
        fill=(0, 100, 0),
        font=font_bold,
        anchor="mm",
    )
    y += 60

    # Render courses grouped by semester
    semesters_data = transcript.get_courses_by_semester()

    for semester_info in semesters_data:
        semester_name = semester_info["semester_name"]
        courses = semester_info["courses"]

        # Semester header
        draw.text((50, y), semester_name, font=font_bold, fill=(0, 0, 100))
        y += 25

        # Table header
        draw.text((50, y), "Course", font=font_bold, fill=(0, 0, 0))
        draw.text((150, y), "Title", font=font_bold, fill=(0, 0, 0))
        draw.text((550, y), "Credits", font=font_bold, fill=(0, 0, 0))
        draw.text((650, y), "Grade", font=font_bold, fill=(0, 0, 0))
        y += 18
        draw.line([(50, y), (w - 50, y)], fill=(150, 150, 150), width=1)
        y += 8

        for course in courses:
            code = course["code"]
            title = course["title"]
            # Truncate long titles to fit
            if len(title) > 40:
                title = title[:37] + "..."
            credits = str(course["credits"])
            grade = course["grade"]

            draw.text((50, y), code, font=font_text, fill=(0, 0, 0))
            draw.text((150, y), title, font=font_text, fill=(0, 0, 0))
            draw.text((550, y), credits, font=font_text, fill=(0, 0, 0))
            draw.text((650, y), grade, font=font_text, fill=(0, 0, 0))
            y += 22

        y += 15  # Space between semesters

        # Check if we're running out of space
        if y > h - 150:
            break

    # Summary section at bottom
    y = h - 120
    draw.line([(50, y), (w - 50, y)], fill=(0, 0, 0), width=2)
    y += 20

    draw.text((50, y), f"Cumulative GPA: {transcript.gpa:.2f}", font=font_bold, fill=(0, 0, 0))
    draw.text(
        (300, y), f"Total Credits: {transcript.total_credits}", font=font_bold, fill=(0, 0, 0)
    )
    draw.text((550, y), "Standing: Good", font=font_bold, fill=(0, 100, 0))

    # Footer
    draw.text(
        (w // 2, h - 40),
        "This document is electronically generated and valid without signature.",
        fill=(100, 100, 100),
        font=font_text,
        anchor="mm",
    )

    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def _get_fonts() -> tuple[Any, ...]:
    """
    Load fonts with fallback to default.

    Returns:
        Tuple of (header, title, text, bold) fonts
    """
    try:
        font_header = ImageFont.truetype("arial.ttf", 32)
        font_title = ImageFont.truetype("arial.ttf", 24)
        font_text = ImageFont.truetype("arial.ttf", 16)
        font_bold = ImageFont.truetype("arialbd.ttf", 16)
    except OSError:
        default = ImageFont.load_default()
        font_header = font_title = font_text = font_bold = default

    return font_header, font_title, font_text, font_bold


# =============================================================================
# Student ID Card Generation
# =============================================================================


@overload
def generate_student_id(
    first_name: str,
    last_name: str,
    school_name: str,
    *,
    return_info: Literal[False] = False,
    verification_id: str | None = None,
) -> bytes: ...


@overload
def generate_student_id(
    first_name: str,
    last_name: str,
    school_name: str,
    *,
    return_info: Literal[True],
    verification_id: str | None = None,
) -> DocumentResult: ...


def generate_student_id(
    first_name: str,
    last_name: str,
    school_name: str,
    *,
    return_info: bool = False,
    verification_id: str | None = None,
) -> bytes | DocumentResult:
    """
    Generate a fake student ID card image.

    Uses Pillow for image generation.

    Args:
        first_name: Student's first name
        last_name: Student's last name
        school_name: University/college name
        return_info: If True, return DocumentResult with metadata; otherwise return bytes
        verification_id: Optional verification ID for cache filename

    Returns:
        PNG image data as bytes, or DocumentResult if return_info=True
    """
    # Cleanup old cache files (non-blocking)
    if DOCUMENT_CACHE_ENABLED:
        _cleanup_old_cache()

    data = _generate_student_id_pillow(first_name, last_name, school_name)
    method = "pillow"
    logger.info(f"Generated student ID card using Pillow ({len(data)} bytes)")

    # Cache document if enabled
    cached_path: Path | None = None
    if DOCUMENT_CACHE_ENABLED:
        cached_path = _cache_document(data, "id_card", verification_id)

    if return_info:
        return DocumentResult(
            data=data,
            method=method,
            doc_type="id_card",
            cached_path=cached_path,
        )

    return data


def _generate_student_id_pillow(
    first_name: str,
    last_name: str,
    school_name: str,
) -> bytes:
    """Generate student ID card using Pillow."""
    w, h = ID_CARD_WIDTH, ID_CARD_HEIGHT

    # Randomize background color slightly
    bg_color = (
        random.randint(240, 255),
        random.randint(240, 255),
        random.randint(240, 255),
    )
    img = Image.new("RGB", (w, h), bg_color)
    draw = ImageDraw.Draw(img)

    try:
        font_lg = ImageFont.truetype("arial.ttf", 26)
        font_md = ImageFont.truetype("arial.ttf", 18)
        font_sm = ImageFont.truetype("arial.ttf", 14)
        font_bold = ImageFont.truetype("arialbd.ttf", 20)
    except OSError:
        default = ImageFont.load_default()
        font_lg = font_md = font_sm = font_bold = default

    # Header with school color
    header_color = (
        random.randint(0, 50),
        random.randint(0, 50),
        random.randint(50, 150),
    )
    draw.rectangle([(0, 0), (w, 80)], fill=header_color)
    draw.text((w // 2, 40), school_name.upper(), fill=(255, 255, 255), font=font_lg, anchor="mm")

    # Photo placeholder
    draw.rectangle([(30, 100), (160, 280)], outline=(100, 100, 100), width=2, fill=(220, 220, 220))
    draw.text((95, 190), "PHOTO", fill=(150, 150, 150), font=font_md, anchor="mm")

    # Student info
    x_info = 190
    y = 110
    draw.text((x_info, y), f"{first_name} {last_name}", fill=(0, 0, 0), font=font_bold)

    y += 40
    draw.text((x_info, y), "Student ID:", fill=(100, 100, 100), font=font_sm)
    draw.text(
        (x_info + 80, y), str(random.randint(10000000, 99999999)), fill=(0, 0, 0), font=font_md
    )

    y += 30
    draw.text((x_info, y), "Role:", fill=(100, 100, 100), font=font_sm)
    draw.text((x_info + 80, y), "Student", fill=(0, 0, 0), font=font_md)

    y += 30
    draw.text((x_info, y), "Valid Thru:", fill=(100, 100, 100), font=font_sm)
    draw.text((x_info + 80, y), f"05/{int(time.strftime('%Y')) + 1}", fill=(0, 0, 0), font=font_md)

    # Barcode strip
    draw.rectangle([(0, 320), (w, 380)], fill=(255, 255, 255))
    for i in range(40):
        x = 50 + i * 14
        if random.random() > 0.3:
            draw.rectangle([(x, 330), (x + 8, 370)], fill=(0, 0, 0))

    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


# =============================================================================
# Class Schedule Generation
# =============================================================================


@overload
def generate_class_schedule(
    first_name: str,
    last_name: str,
    school_name: str,
    *,
    return_info: Literal[False] = False,
    verification_id: str | None = None,
) -> bytes: ...


@overload
def generate_class_schedule(
    first_name: str,
    last_name: str,
    school_name: str,
    *,
    return_info: Literal[True],
    verification_id: str | None = None,
) -> DocumentResult: ...


def generate_class_schedule(
    first_name: str,
    last_name: str,
    school_name: str,
    *,
    return_info: bool = False,
    verification_id: str | None = None,
) -> bytes | DocumentResult:
    """
    Generate a fake class schedule image.

    Uses Playwright (HTML→PNG) by default for high-quality output.
    Falls back to Pillow if Playwright is not available.

    Args:
        first_name: Student's first name
        last_name: Student's last name
        school_name: University/college name
        return_info: If True, return DocumentResult with metadata; otherwise return bytes
        verification_id: Optional verification ID for cache filename

    Returns:
        PNG image data as bytes, or DocumentResult if return_info=True
    """
    # Cleanup old cache files (non-blocking)
    if DOCUMENT_CACHE_ENABLED:
        _cleanup_old_cache()

    student_id = str(random.randint(10000000, 99999999))

    method: str = "pillow"
    data: bytes

    # Try Playwright first, fall back to Pillow
    if _is_playwright_available():
        try:
            data = _generate_class_schedule_playwright(
                first_name=first_name,
                last_name=last_name,
                school_name=school_name,
                student_id=student_id,
            )
            method = "playwright"
            logger.info(f"Generated class schedule using Playwright ({len(data)} bytes)")
        except Exception as e:
            logger.warning(f"Playwright rendering failed, falling back to Pillow: {e}")
            data = _generate_class_schedule_pillow(
                first_name=first_name,
                last_name=last_name,
                school_name=school_name,
                student_id=student_id,
            )
            method = "pillow"
            logger.info(f"Generated class schedule using Pillow ({len(data)} bytes)")
    else:
        # Pillow fallback
        data = _generate_class_schedule_pillow(
            first_name=first_name,
            last_name=last_name,
            school_name=school_name,
            student_id=student_id,
        )
        logger.info(f"Generated class schedule using Pillow ({len(data)} bytes)")

    # Cache document if enabled
    cached_path: Path | None = None
    if DOCUMENT_CACHE_ENABLED:
        cached_path = _cache_document(data, "class_schedule", verification_id)

    if return_info:
        return DocumentResult(
            data=data,
            method=method,
            doc_type="class_schedule",
            cached_path=cached_path,
        )

    return data


def _generate_class_schedule_playwright(
    first_name: str,
    last_name: str,
    school_name: str,
    student_id: str,
) -> bytes:
    """Generate class schedule using Playwright HTML renderer."""
    from sheerid_verifier.services.html_renderer import render_html_to_png
    from sheerid_verifier.services.class_schedule_html import generate_class_schedule_html

    # Generate HTML from template
    html_content = generate_class_schedule_html(
        school_name=school_name,
        student_name=f"{first_name} {last_name}",
        student_id=student_id,
    )

    # Render to PNG
    return render_html_to_png(
        html_content=html_content,
        viewport_width=TRANSCRIPT_VIEWPORT_WIDTH,
        viewport_height=TRANSCRIPT_VIEWPORT_HEIGHT,
        full_page=True,
    )


def _generate_class_schedule_pillow(
    first_name: str,
    last_name: str,
    school_name: str,
    student_id: str,
) -> bytes:
    """Generate class schedule using Pillow (fallback)."""
    from sheerid_verifier.services.class_schedule_html import (
        get_current_semester,
        get_semester_dates,
        _generate_schedule_courses,
    )

    w, h = TRANSCRIPT_WIDTH, 700
    img = Image.new("RGB", (w, h), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    font_header, font_title, font_text, font_bold = _get_fonts()

    # Get current semester info
    semester, year = get_current_semester()
    start_date, end_date = get_semester_dates(semester, year)

    # Header
    draw.rectangle([(0, 0), (w, 80)], fill=(26, 54, 93))
    draw.text(
        (w // 2, 40), school_name.upper(), fill=(255, 255, 255), font=font_header, anchor="mm"
    )

    # Term banner
    draw.rectangle([(0, 80), (w, 120)], fill=(232, 244, 253))
    draw.text(
        (30, 100), f"{semester} {year} - Registered Classes", fill=(43, 108, 176), font=font_bold
    )
    draw.text((w - 200, 100), f"{start_date} - {end_date}", fill=(74, 85, 104), font=font_text)

    # Student info
    y = 140
    draw.text((30, y), f"Student: {first_name} {last_name}", fill=(0, 0, 0), font=font_bold)
    draw.text((w - 200, y), f"ID: {student_id}", fill=(0, 0, 0), font=font_text)
    y += 30

    # Enrollment status
    draw.rectangle([(30, y), (130, y + 25)], fill=(198, 246, 213))
    draw.text((80, y + 12), "Enrolled", fill=(39, 103, 73), font=font_text, anchor="mm")
    y += 45

    # Table header
    draw.line([(30, y), (w - 30, y)], fill=(226, 232, 240), width=2)
    y += 10
    headers = ["Course", "Title", "Cr", "Days", "Time", "Location"]
    x_positions = [30, 100, 380, 420, 480, 600]
    for i, header in enumerate(headers):
        draw.text((x_positions[i], y), header, fill=(74, 85, 104), font=font_bold)
    y += 25
    draw.line([(30, y), (w - 30, y)], fill=(226, 232, 240), width=1)
    y += 10

    # Generate courses
    courses = _generate_schedule_courses(5)

    for course in courses:
        draw.text((30, y), course["code"], fill=(43, 108, 176), font=font_bold)
        title = course["title"]
        if len(title) > 28:
            title = title[:25] + "..."
        draw.text((100, y), title, fill=(45, 55, 72), font=font_text)
        draw.text((380, y), str(course["credits"]), fill=(0, 0, 0), font=font_text)
        draw.text((420, y), course["days"], fill=(74, 85, 104), font=font_text)
        draw.text((480, y), course["time"][:15], fill=(74, 85, 104), font=font_text)
        location = course["location"]
        if len(location) > 20:
            location = location[:17] + "..."
        draw.text((600, y), location, fill=(113, 128, 150), font=font_text)
        y += 28

    # Summary
    y += 20
    total_credits = sum(c["credits"] for c in courses)
    draw.rectangle([(30, y), (w - 30, y + 50)], fill=(247, 250, 252))
    draw.text(
        (60, y + 25),
        f"Total Courses: {len(courses)}",
        fill=(45, 55, 72),
        font=font_bold,
        anchor="lm",
    )
    draw.text(
        (250, y + 25),
        f"Total Credits: {total_credits}",
        fill=(43, 108, 176),
        font=font_bold,
        anchor="lm",
    )
    draw.text((450, y + 25), "Status: Full-Time", fill=(45, 55, 72), font=font_bold, anchor="lm")

    # Footer
    draw.text(
        (w // 2, h - 30),
        f"Generated: {time.strftime('%B %d, %Y at %I:%M %p')}",
        fill=(160, 174, 192),
        font=font_text,
        anchor="mm",
    )

    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()
