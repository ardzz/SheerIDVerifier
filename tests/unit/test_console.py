"""Unit tests for console.py - StepLogger and output functions."""

import io
import re

import pytest
from rich.console import Console

from sheerid_verifier.console import (
    LogLevel,
    StepLogger,
    print_detail,
    print_error,
    print_info,
    print_step,
    print_success,
    print_warning,
)


def strip_ansi(text: str) -> str:
    """Remove ANSI escape codes from text."""
    ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
    return ansi_escape.sub("", text)


class TestLogLevel:
    """Tests for LogLevel enum."""

    def test_all_levels_exist(self) -> None:
        """Test all log levels are defined."""
        assert LogLevel.DEBUG.value == "DEBUG"
        assert LogLevel.INFO.value == "INFO"
        assert LogLevel.WARNING.value == "WARNING"
        assert LogLevel.ERROR.value == "ERROR"
        assert LogLevel.SUCCESS.value == "SUCCESS"


class TestStepLogger:
    """Tests for StepLogger class."""

    def test_init_default_console(self) -> None:
        """Test StepLogger initializes with default console."""
        logger = StepLogger()
        assert logger._verbose is True

    def test_init_custom_console(self) -> None:
        """Test StepLogger with custom console."""
        custom_console = Console(file=io.StringIO())
        logger = StepLogger(con=custom_console)
        assert logger._console is custom_console

    def test_init_verbose_false(self) -> None:
        """Test StepLogger with verbose=False."""
        logger = StepLogger(verbose=False)
        assert logger._verbose is False

    def test_step_context_manager(self) -> None:
        """Test step context manager executes code."""
        output = io.StringIO()
        custom_console = Console(file=output, force_terminal=True)
        logger = StepLogger(con=custom_console)

        executed = False
        with logger.step(1, 3, "Test step"):
            executed = True

        assert executed is True
        result = strip_ansi(output.getvalue())
        assert "[1/3]" in result
        assert "Test step" in result
        assert "Done" in result

    def test_step_silent_when_not_verbose(self) -> None:
        """Test step produces no output when verbose=False."""
        output = io.StringIO()
        custom_console = Console(file=output, force_terminal=True)
        logger = StepLogger(con=custom_console, verbose=False)

        with logger.step(1, 3, "Test step"):
            pass

        assert output.getvalue() == ""

    def test_detail_output(self) -> None:
        """Test detail method output."""
        output = io.StringIO()
        custom_console = Console(file=output, force_terminal=True)
        logger = StepLogger(con=custom_console)

        logger.detail("Label", "Value")

        result = strip_ansi(output.getvalue())
        assert "Label" in result
        assert "Value" in result

    def test_success_output(self) -> None:
        """Test success method output."""
        output = io.StringIO()
        custom_console = Console(file=output, force_terminal=True)
        logger = StepLogger(con=custom_console)

        logger.success("Success message")

        result = strip_ansi(output.getvalue())
        assert "[OK]" in result
        assert "Success message" in result

    def test_error_output(self) -> None:
        """Test error method output."""
        output = io.StringIO()
        custom_console = Console(file=output, force_terminal=True)
        logger = StepLogger(con=custom_console)

        logger.error("Error message")

        result = strip_ansi(output.getvalue())
        assert "[FAIL]" in result
        assert "Error message" in result

    def test_warning_output(self) -> None:
        """Test warning method output."""
        output = io.StringIO()
        custom_console = Console(file=output, force_terminal=True)
        logger = StepLogger(con=custom_console)

        logger.warning("Warning message")

        result = strip_ansi(output.getvalue())
        assert "[WARN]" in result
        assert "Warning message" in result

    def test_info_output(self) -> None:
        """Test info method output."""
        output = io.StringIO()
        custom_console = Console(file=output, force_terminal=True)
        logger = StepLogger(con=custom_console)

        logger.info("Info message")

        result = strip_ansi(output.getvalue())
        assert "[INFO]" in result
        assert "Info message" in result


class TestStandaloneFunctions:
    """Tests for standalone console functions."""

    def test_print_success_no_emoji(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test print_success uses text indicator, not emoji."""
        # Note: Rich bypasses capsys, so we just verify no exception
        print_success("Test")

    def test_print_error_no_emoji(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test print_error uses text indicator, not emoji."""
        print_error("Test")

    def test_print_warning_no_emoji(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test print_warning uses text indicator, not emoji."""
        print_warning("Test")

    def test_print_info_no_emoji(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test print_info uses text indicator, not emoji."""
        print_info("Test")

    def test_print_step_format(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test print_step uses [N/M] format."""
        print_step(1, 5, "Test step")

    def test_print_detail_format(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test print_detail with custom bullet."""
        print_detail("Key", "Value", bullet="*")


class TestNoEmoji:
    """Tests to verify emoji removal."""

    def test_console_module_no_emoji_imports(self) -> None:
        """Verify the console module source has no emoji characters."""
        import inspect

        import sheerid_verifier.console as console_module

        source = inspect.getsource(console_module)

        # Common emoji Unicode ranges
        emoji_patterns = [
            "\U0001f600",  # 😀 and similar
            "\U0001f4a1",  # 💡
            "\U0001f4dd",  # 📝
            "\U00002705",  # ✅
            "\U0000274c",  # ❌
            "\U000026a0",  # ⚠
            "\U00002139",  # ℹ
            "\U0001f389",  # 🎉
            "\U0001f4e7",  # 📧
            "\U0001f393",  # 🎓
            "\U0001f3eb",  # 🏫
            "\U0001f382",  # 🎂
            "\U0001f510",  # 🔐
            "\U0001f4c4",  # 📄
            "\U0001f4cd",  # 📍
            "\U0001f916",  # 🤖
            "\U000025b6",  # ▶
        ]

        for emoji in emoji_patterns:
            assert emoji not in source, f"Found emoji {repr(emoji)} in console.py"
