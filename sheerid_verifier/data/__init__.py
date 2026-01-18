"""
Academic data module for dynamic transcript generation.

This module provides:
- Course catalog with 100+ courses across 15 departments
- Major definitions with coherent course mappings
- GPA calculation and grade distribution
- Transcript generation orchestration
"""

from sheerid_verifier.data.courses import (
    COURSE_CATALOG,
    DEPARTMENTS,
    Course,
    get_courses_by_department,
    get_courses_by_level,
    get_random_courses,
)
from sheerid_verifier.data.grading import (
    GRADE_DISTRIBUTIONS,
    GRADE_SCALE,
    PerformanceProfile,
    calculate_gpa,
    generate_grade,
)
from sheerid_verifier.data.majors import (
    MAJORS,
    Major,
    get_major,
    get_random_major,
)
from sheerid_verifier.data.transcript import (
    Transcript,
    TranscriptCourse,
    generate_transcript,
)

__all__ = [
    # Grading
    "GRADE_SCALE",
    "GRADE_DISTRIBUTIONS",
    "PerformanceProfile",
    "generate_grade",
    "calculate_gpa",
    # Courses
    "Course",
    "COURSE_CATALOG",
    "DEPARTMENTS",
    "get_courses_by_department",
    "get_courses_by_level",
    "get_random_courses",
    # Majors
    "Major",
    "MAJORS",
    "get_major",
    "get_random_major",
    # Transcript
    "TranscriptCourse",
    "Transcript",
    "generate_transcript",
]
