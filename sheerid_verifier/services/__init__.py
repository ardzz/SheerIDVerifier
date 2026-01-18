"""Service modules for SheerID Verifier."""

from sheerid_verifier.services.document import (
    generate_student_id,
    generate_transcript,
    generate_transcript_async,
)
from sheerid_verifier.services.http_client import HttpClient, HttpxClient
from sheerid_verifier.services.stats import Stats

__all__ = [
    "HttpClient",
    "HttpxClient",
    "Stats",
    "generate_transcript",
    "generate_transcript_async",
    "generate_student_id",
]

# Optional Playwright renderer exports (only available if playwright is installed)
try:
    from sheerid_verifier.services.html_renderer import (  # noqa: F401
        is_playwright_available,
        render_html_to_png,
        render_html_to_png_async,
    )

    __all__.extend(
        [
            "is_playwright_available",
            "render_html_to_png",
            "render_html_to_png_async",
        ]
    )
except ImportError:
    pass
