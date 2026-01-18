"""Statistics tracking service."""

import json
from pathlib import Path
from typing import Any


class Stats:
    """Track verification success rates by organization."""

    def __init__(self, stats_file: Path | None = None) -> None:
        """
        Initialize stats tracker.

        Args:
            stats_file: Path to stats JSON file. Defaults to stats.json in current directory.
        """
        self._file = stats_file or Path("stats.json")
        self._data = self._load()

    def _load(self) -> dict[str, Any]:
        """Load stats from file or create default."""
        if self._file.exists():
            try:
                return json.loads(self._file.read_text())
            except (json.JSONDecodeError, OSError):
                pass
        return {"total": 0, "success": 0, "failed": 0, "orgs": {}}

    def _save(self) -> None:
        """Save stats to file."""
        try:
            self._file.write_text(json.dumps(self._data, indent=2))
        except OSError:
            pass  # Fail silently if we can't write stats

    def record(self, org: str, success: bool) -> None:
        """
        Record a verification attempt.

        Args:
            org: Organization/university name
            success: Whether the verification was successful
        """
        self._data["total"] += 1
        key = "success" if success else "failed"
        self._data[key] += 1

        if org not in self._data["orgs"]:
            self._data["orgs"][org] = {"success": 0, "failed": 0}
        self._data["orgs"][org][key] += 1

        self._save()

    def get_rate(self, org: str | None = None) -> float:
        """
        Get success rate.

        Args:
            org: Organization name, or None for overall rate

        Returns:
            Success rate as percentage (0-100), or 50 if no data
        """
        if org:
            org_data = self._data["orgs"].get(org, {})
            total = org_data.get("success", 0) + org_data.get("failed", 0)
            if total == 0:
                return 50.0  # Default rate for unknown orgs
            return org_data.get("success", 0) / total * 100

        if self._data["total"] == 0:
            return 0.0
        return self._data["success"] / self._data["total"] * 100

    @property
    def total(self) -> int:
        """Total number of verification attempts."""
        return self._data["total"]

    @property
    def success_count(self) -> int:
        """Number of successful verifications."""
        return self._data["success"]

    @property
    def failed_count(self) -> int:
        """Number of failed verifications."""
        return self._data["failed"]
