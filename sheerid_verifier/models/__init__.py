"""Data models for SheerID Verifier."""

from sheerid_verifier.models.student import Student
from sheerid_verifier.models.university import UNIVERSITIES, University, select_university

__all__ = ["University", "UNIVERSITIES", "select_university", "Student"]
