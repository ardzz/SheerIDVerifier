"""Rich console output abstraction for SheerID Verifier.

Includes StepLogger for contextual step-by-step logging with timing.
"""

from __future__ import annotations

import time
from contextlib import contextmanager
from enum import Enum
from typing import TYPE_CHECKING, Any, Generator

from rich.console import Console
from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, TaskProgressColumn, TextColumn
from rich.table import Table
from rich.text import Text

if TYPE_CHECKING:
    pass

# Global console instance
console = Console(force_terminal=True)


# =============================================================================
# Log Level Enum
# =============================================================================


class LogLevel(Enum):
    """Log level for console output."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    SUCCESS = "SUCCESS"


# =============================================================================
# StepLogger Class (Contextual Logging with Timing)
# =============================================================================


class StepLogger:
    """Contextual logger for step-by-step process logging with timing.

    Provides structured logging with step numbers, descriptions, and
    automatic timing measurement using context managers.

    Example:
        logger = StepLogger(console)
        with logger.step(1, 5, "Generating transcript"):
            # do work
            logger.detail("Size", "45.2 KB")
        # Output:
        # [1/5] Generating transcript...
        #    - Size: 45.2 KB
        #    Done (0.15s)
    """

    def __init__(self, con: Console | None = None, verbose: bool = True) -> None:
        """Initialize StepLogger.

        Args:
            con: Rich Console instance. Uses global console if None.
            verbose: Whether to print output. If False, all methods are no-ops.
        """
        self._console = con or console
        self._verbose = verbose
        self._current_step: int | None = None
        self._current_total: int | None = None

    @contextmanager
    def step(self, num: int, total: int, description: str) -> Generator[None, None, None]:
        """Context manager for a verification step with timing.

        Args:
            num: Current step number (1-based)
            total: Total number of steps
            description: Step description

        Yields:
            None - use the context to perform work

        Example:
            with logger.step(1, 5, "Processing"):
                do_work()
        """
        if not self._verbose:
            yield
            return

        self._current_step = num
        self._current_total = total

        self._console.print(f"[bold blue][{num}/{total}][/bold blue] {description}...")

        start_time = time.perf_counter()
        try:
            yield
        finally:
            elapsed = time.perf_counter() - start_time
            self._console.print(f"   [dim]Done ({elapsed:.2f}s)[/dim]")
            self._current_step = None
            self._current_total = None

    def detail(self, label: str, value: str) -> None:
        """Print a detail line within the current step.

        Args:
            label: Detail label (e.g., "Size", "Student")
            value: Detail value
        """
        if not self._verbose:
            return
        self._console.print(f"   - [dim]{label}:[/dim] {value}")

    def success(self, message: str) -> None:
        """Print a success message.

        Args:
            message: Success message text
        """
        if not self._verbose:
            return
        self._console.print(f"[bold green][OK][/bold green] {message}")

    def error(self, message: str) -> None:
        """Print an error message.

        Args:
            message: Error message text
        """
        if not self._verbose:
            return
        self._console.print(f"[bold red][FAIL][/bold red] {message}")

    def warning(self, message: str) -> None:
        """Print a warning message.

        Args:
            message: Warning message text
        """
        if not self._verbose:
            return
        self._console.print(f"[bold yellow][WARN][/bold yellow] {message}")

    def info(self, message: str) -> None:
        """Print an info message.

        Args:
            message: Info message text
        """
        if not self._verbose:
            return
        self._console.print(f"[cyan][INFO][/cyan] {message}")


# =============================================================================
# Standalone Functions (Backwards Compatible)
# =============================================================================


def print_header() -> None:
    """Print application header panel."""
    header = Text()
    header.append("SheerID Verifier", style="bold cyan")
    header.append("\n")
    header.append("Google One (Gemini) Student Verification", style="dim")

    console.print(Panel(header, border_style="blue", padding=(1, 2)))


def print_success(message: str) -> None:
    """Print success message."""
    console.print(f"[bold green][OK][/bold green] {message}")


def print_error(message: str) -> None:
    """Print error message."""
    console.print(f"[bold red][FAIL][/bold red] {message}")


def print_warning(message: str) -> None:
    """Print warning message."""
    console.print(f"[bold yellow][WARN][/bold yellow] {message}")


def print_info(message: str) -> None:
    """Print info message."""
    console.print(f"[cyan][INFO][/cyan] {message}")


def print_step(step: int, total: int, message: str) -> None:
    """Print step indicator."""
    console.print(f"[bold blue][{step}/{total}][/bold blue] {message}")


def print_detail(label: str, value: str, bullet: str = "-") -> None:
    """Print detail line with label and value."""
    console.print(f"   {bullet} [dim]{label}:[/dim] {value}")


def print_student_info(
    first_name: str,
    last_name: str,
    email: str,
    school: str,
    dob: str,
    verification_id: str,
) -> None:
    """Print student information block."""
    console.print()
    print_detail("Student", f"{first_name} {last_name}")
    print_detail("Email", email)
    print_detail("School", school)
    print_detail("DOB", dob)
    print_detail("ID", f"{verification_id[:20]}...")


def print_stats_table(total: int, success: int, failed: int, success_rate: float) -> None:
    """Print statistics table."""
    table = Table(title="Statistics", show_header=True, header_style="bold cyan")
    table.add_column("Metric", style="dim")
    table.add_column("Value", justify="right")

    table.add_row("Total", str(total))
    table.add_row("Success", f"[green]{success}[/green]")
    table.add_row("Failed", f"[red]{failed}[/red]")
    table.add_row("Success Rate", f"[bold]{success_rate:.1f}%[/bold]")

    console.print()
    console.print(table)


def print_result(success: bool, result: dict[str, Any]) -> None:
    """Print verification result."""
    console.print()
    console.rule()

    if success:
        console.print("[bold green][SUCCESS][/bold green] Verification submitted!")
        if student := result.get("student"):
            console.print(f"   - Student: {student}")
        if email := result.get("email"):
            console.print(f"   - Email: {email}")
        if school := result.get("school"):
            console.print(f"   - School: {school}")
        console.print()
        console.print("[dim]   Wait 24-48 hours for manual review[/dim]")
    else:
        error = result.get("error", "Unknown error")
        console.print(f"[bold red][FAIL][/bold red] {error}")

    console.rule()


def create_progress() -> Progress:
    """Create progress bar for verification steps."""
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
    )


def print_divider() -> None:
    """Print a horizontal divider."""
    console.rule()
