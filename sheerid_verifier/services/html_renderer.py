"""HTML to PNG rendering using Playwright (optional).

This module provides functions to render HTML content to PNG images using
Playwright's headless Chromium browser. If Playwright is not installed or
the browser is not available, functions will raise appropriate exceptions.

Usage:
    # Sync
    from sheerid_verifier.services.html_renderer import render_html_to_png
    png_bytes = render_html_to_png("<html>...</html>")

    # Async
    from sheerid_verifier.services.html_renderer import render_html_to_png_async
    png_bytes = await render_html_to_png_async("<html>...</html>")

    # Check availability
    from sheerid_verifier.services.html_renderer import is_playwright_available
    if is_playwright_available():
        ...
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

# Cache for availability check
_playwright_available: bool | None = None


def is_playwright_available() -> bool:
    """
    Check if Playwright is installed and browser is usable.

    This function caches its result after the first call for performance.
    It attempts to launch and immediately close a headless Chromium browser
    to verify everything is properly installed.

    Returns:
        True if Playwright can be used, False otherwise.
    """
    global _playwright_available

    if _playwright_available is not None:
        return _playwright_available

    try:
        from playwright.sync_api import sync_playwright

        # Quick check: launch and close browser
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            browser.close()

        _playwright_available = True
        logger.debug("Playwright is available")

    except ImportError:
        logger.debug("Playwright not installed")
        _playwright_available = False

    except Exception as e:
        logger.debug(f"Playwright not available: {e}")
        _playwright_available = False

    return _playwright_available


def reset_availability_cache() -> None:
    """Reset the cached availability check (useful for testing)."""
    global _playwright_available
    _playwright_available = None


def render_html_to_png(
    html_content: str,
    viewport_width: int = 1200,
    viewport_height: int = 900,
    full_page: bool = True,
    device_scale_factor: float = 1.0,
) -> bytes:
    """
    Render HTML string to PNG using Playwright (synchronous).

    Launches a headless Chromium browser, loads the HTML content directly
    (no network request), and captures a screenshot.

    Args:
        html_content: Complete HTML document string
        viewport_width: Browser viewport width in pixels
        viewport_height: Browser viewport height in pixels
        full_page: If True, capture full scrollable page; if False, capture viewport only
        device_scale_factor: Device scale factor for high-DPI rendering (1.0 = normal)

    Returns:
        PNG image data as bytes

    Raises:
        ImportError: If Playwright is not installed
        RuntimeError: If Chromium browser is not installed
    """
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        context = browser.new_context(
            viewport={"width": viewport_width, "height": viewport_height},
            device_scale_factor=device_scale_factor,
        )
        page = context.new_page()

        # Load HTML content directly (no network request needed)
        page.set_content(html_content, wait_until="load")

        # Capture screenshot
        png_bytes = page.screenshot(type="png", full_page=full_page)

        browser.close()

        return png_bytes


async def render_html_to_png_async(
    html_content: str,
    viewport_width: int = 1200,
    viewport_height: int = 900,
    full_page: bool = True,
    device_scale_factor: float = 1.0,
) -> bytes:
    """
    Render HTML string to PNG using Playwright (asynchronous).

    Async version of render_html_to_png for use in async contexts.

    Args:
        html_content: Complete HTML document string
        viewport_width: Browser viewport width in pixels
        viewport_height: Browser viewport height in pixels
        full_page: If True, capture full scrollable page; if False, capture viewport only
        device_scale_factor: Device scale factor for high-DPI rendering (1.0 = normal)

    Returns:
        PNG image data as bytes

    Raises:
        ImportError: If Playwright is not installed
        RuntimeError: If Chromium browser is not installed
    """
    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        context = await browser.new_context(
            viewport={"width": viewport_width, "height": viewport_height},
            device_scale_factor=device_scale_factor,
        )
        page = await context.new_page()

        # Load HTML content directly
        await page.set_content(html_content, wait_until="load")

        # Capture screenshot
        png_bytes = await page.screenshot(type="png", full_page=full_page)

        await browser.close()

        return png_bytes
