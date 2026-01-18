"""
Grading scales and GPA calculation for US universities.

Provides:
- Standard US 4.0 GPA scale
- Grade distributions by performance profile
- GPA calculation from course list
"""

import random
from typing import Literal

# US 4.0 Standard Scale
GRADE_SCALE: dict[str, float] = {
    "A+": 4.0,
    "A": 4.0,
    "A-": 3.7,
    "B+": 3.3,
    "B": 3.0,
    "B-": 2.7,
    "C+": 2.3,
    "C": 2.0,
    "C-": 1.7,
    "D+": 1.3,
    "D": 1.0,
    "D-": 0.7,
    "F": 0.0,
}

# Grade distribution weights by performance profile
# Higher weight = more likely to be selected
GRADE_DISTRIBUTIONS: dict[str, dict[str, int]] = {
    "excellent": {  # Target GPA ~3.7-4.0
        "A+": 10,
        "A": 45,
        "A-": 30,
        "B+": 12,
        "B": 3,
    },
    "good": {  # Target GPA ~3.2-3.7 (DEFAULT)
        "A": 18,
        "A-": 28,
        "B+": 30,
        "B": 15,
        "B-": 7,
        "C+": 2,
    },
    "average": {  # Target GPA ~2.5-3.2
        "A-": 5,
        "B+": 12,
        "B": 28,
        "B-": 25,
        "C+": 15,
        "C": 10,
        "C-": 5,
    },
}

# Type alias for performance profiles
PerformanceProfile = Literal["excellent", "good", "average"]


def generate_grade(profile: PerformanceProfile = "good") -> str:
    """
    Generate a random grade based on performance profile.

    Args:
        profile: Performance level ("excellent", "good", "average")

    Returns:
        Letter grade string (e.g., "A", "B+", "A-")
    """
    distribution = GRADE_DISTRIBUTIONS.get(profile, GRADE_DISTRIBUTIONS["good"])
    grades = list(distribution.keys())
    weights = list(distribution.values())
    return random.choices(grades, weights=weights, k=1)[0]


def calculate_gpa(courses: list[dict]) -> float:
    """
    Calculate weighted GPA from course list.

    Formula: GPA = Σ(grade_points × credits) / Σ(credits)

    Args:
        courses: List of course dicts with "grade" and "credits" keys

    Returns:
        Calculated GPA rounded to 2 decimal places

    Example:
        >>> courses = [
        ...     {"grade": "A", "credits": 4},
        ...     {"grade": "B+", "credits": 3},
        ... ]
        >>> calculate_gpa(courses)
        3.71
    """
    if not courses:
        return 0.0

    total_points = 0.0
    total_credits = 0.0

    for course in courses:
        grade = course.get("grade", "")
        credits = float(course.get("credits", 0))

        if grade in GRADE_SCALE and credits > 0:
            total_points += GRADE_SCALE[grade] * credits
            total_credits += credits

    if total_credits == 0:
        return 0.0

    return round(total_points / total_credits, 2)


def get_grade_points(grade: str) -> float:
    """
    Get grade points for a letter grade.

    Args:
        grade: Letter grade (e.g., "A", "B+")

    Returns:
        Grade points on 4.0 scale
    """
    return GRADE_SCALE.get(grade, 0.0)
