"""CLI argument parsing and main entry point."""

import argparse
import sys

from sheerid_verifier import __version__, console
from sheerid_verifier.services.http_client import HttpxClient
from sheerid_verifier.services.stats import Stats
from sheerid_verifier.services.verifier import Verifier


def create_parser() -> argparse.ArgumentParser:
    """Create CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="sheerid",
        description="SheerID Student Verification Tool for Google One (Gemini)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  sheerid "https://services.sheerid.com/verify/...?verificationId=abc123"
  sheerid --proxy socks5://localhost:1080 "https://..."
  sheerid --proxy http://user:pass@host:port "https://..."
""",
    )

    parser.add_argument(
        "url",
        nargs="?",
        help="SheerID verification URL",
    )

    parser.add_argument(
        "--proxy",
        metavar="URL",
        help="Proxy server URL (http://, socks5://)",
    )

    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Suppress progress output",
    )

    parser.add_argument(
        "--version",
        "-V",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    return parser


def main() -> int:
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args()

    # Print header
    if not args.quiet:
        console.print_header()

    # Get URL
    url = args.url
    if not url:
        url = console.console.input("   Enter verification URL: ").strip()

    if not url or "sheerid.com" not in url:
        console.print_error("Invalid URL. Must contain sheerid.com")
        return 1

    # Show proxy info
    if args.proxy and not args.quiet:
        console.print_info(f"Using proxy: {args.proxy}")

    if not args.quiet:
        console.print_info("Processing...")

    # Create services with dependency injection
    stats = Stats()

    with HttpxClient(proxy=args.proxy) as client:
        verifier = Verifier(client, stats, verbose=not args.quiet)

        # Check link first
        check = verifier.check_link(url)
        if not check.get("valid"):
            console.print_error(f"Link Error: {check.get('error')}")
            return 1

        # Run verification
        result = verifier.verify(url)

    # Print result
    console.print_result(result.get("success", False), result)

    # Print stats
    if not args.quiet:
        console.print_stats_table(
            stats.total,
            stats.success_count,
            stats.failed_count,
            stats.get_rate(),
        )

    return 0 if result.get("success") else 1


if __name__ == "__main__":
    sys.exit(main())
