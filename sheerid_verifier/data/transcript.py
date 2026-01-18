"""
Transcript generation with coherent major-based course selection.

Generates realistic academic transcripts with:
- Multiple semesters
- Coherent course progression by major
- Calculated GPA from generated grades
"""

import datetime
import random
from dataclasses import dataclass, field

from sheerid_verifier.data.courses import (
    Course,
    get_courses_by_department,
)
from sheerid_verifier.data.grading import (
    PerformanceProfile,
    calculate_gpa,
    generate_grade,
)
from sheerid_verifier.data.majors import Major, get_random_major


@dataclass
class TranscriptCourse:
    """A course entry on a transcript with grade."""

    code: str
    title: str
    credits: int
    grade: str
    semester: str

    def to_dict(self) -> dict:
        """Convert to dictionary format."""
        return {
            "code": self.code,
            "title": self.title,
            "credits": self.credits,
            "grade": self.grade,
        }


@dataclass
class Transcript:
    """Generated academic transcript."""

    major: Major
    courses: list[TranscriptCourse] = field(default_factory=list)
    semesters: list[str] = field(default_factory=list)

    @property
    def gpa(self) -> float:
        """Calculate cumulative GPA from all courses."""
        course_dicts = [c.to_dict() for c in self.courses]
        return calculate_gpa(course_dicts)

    @property
    def total_credits(self) -> int:
        """Calculate total credits earned."""
        return sum(c.credits for c in self.courses)

    def get_courses_by_semester(self) -> list[dict]:
        """
        Get courses grouped by semester for HTML generation.

        Returns:
            List of semester dicts with courses, e.g.:
            [
                {
                    "semester_name": "Fall 2023",
                    "courses": [{"code": "CS101", "title": "...", ...}, ...]
                },
                ...
            ]
        """
        semester_map: dict[str, list[dict]] = {}

        for course in self.courses:
            if course.semester not in semester_map:
                semester_map[course.semester] = []
            semester_map[course.semester].append(course.to_dict())

        # Return in semester order
        result = []
        for sem in self.semesters:
            if sem in semester_map:
                result.append(
                    {
                        "semester_name": sem,
                        "courses": semester_map[sem],
                    }
                )

        return result


def generate_transcript(
    major: Major | None = None,
    num_semesters: int | None = None,
    courses_per_semester: tuple[int, int] = (4, 6),
    performance: PerformanceProfile = "good",
    start_year: int | None = None,
) -> Transcript:
    """
    Generate a realistic academic transcript.

    Course selection strategy:
    1. First semesters: Intro courses (100-level) + gen-ed
    2. Middle semesters: Mix of major core (200-300) + support
    3. Later semesters: Advanced courses (300-400) + electives

    Args:
        major: Student's major (random if None)
        num_semesters: Number of semesters (2-5 random if None)
        courses_per_semester: (min, max) courses per semester
        performance: Grade distribution profile
        start_year: Starting academic year (calculated from current date if None)

    Returns:
        Complete Transcript with courses and calculated GPA
    """
    # Select major if not provided
    if major is None:
        major = get_random_major()

    # Determine number of semesters (random 2-5 if not specified)
    if num_semesters is None:
        num_semesters = random.randint(2, 5)

    # Calculate start_year dynamically if not provided
    # Work backwards from current semester so the LAST semester is current/recent
    if start_year is None:
        now = datetime.datetime.now()
        current_year = now.year
        current_month = now.month

        # Determine if we're in Fall (Aug-Dec) or Spring (Jan-May) or Summer (Jun-Jul)
        # For transcript purposes, we want the last semester to be "current" or very recent

        # Calculate how many academic half-years to go back
        # Fall -> Spring -> Fall -> Spring pattern
        # Each academic year has 2 main semesters

        # If in Spring (Jan-May), last semester should be "Spring {current_year}" or "Fall {current_year-1}"
        # If in Fall (Aug-Dec), last semester should be "Fall {current_year}" or "Spring {current_year}"

        if current_month >= 8:  # Fall semester (Aug-Dec)
            # Last semester is Fall of current year
            # Work backwards: Fall N, Spring N, Fall N-1, Spring N-1, ...
            # For num_semesters semesters ending at Fall {current_year}:
            # - 1 semester: Fall {current_year}
            # - 2 semesters: Spring {current_year}, Fall {current_year}
            # - 3 semesters: Fall {current_year-1}, Spring {current_year}, Fall {current_year}
            # Start is at Fall if odd, Spring if even
            half_years_back = num_semesters - 1
            if num_semesters % 2 == 1:  # Odd: starts with Fall
                start_year = current_year - (half_years_back // 2)
            else:  # Even: starts with Spring
                start_year = current_year - (half_years_back // 2)
        else:  # Spring semester (Jan-Jul)
            # Last semester is Spring of current year
            # Work backwards: Spring N, Fall N-1, Spring N-1, Fall N-2, ...
            # For num_semesters semesters ending at Spring {current_year}:
            # - 1 semester: Spring {current_year}
            # - 2 semesters: Fall {current_year-1}, Spring {current_year}
            # - 3 semesters: Spring {current_year-1}, Fall {current_year-1}, Spring {current_year}
            half_years_back = num_semesters - 1
            years_back = (half_years_back + 1) // 2
            start_year = current_year - years_back

    # Generate semester labels
    semesters = _generate_semester_labels(num_semesters, start_year)

    # Track taken courses to avoid duplicates
    taken_codes: set[str] = set()

    # Generate courses for each semester
    all_courses: list[TranscriptCourse] = []

    for i, semester in enumerate(semesters):
        # Determine number of courses this semester
        num_courses = random.randint(courses_per_semester[0], courses_per_semester[1])

        # Select courses based on semester progression
        semester_courses = _select_courses_for_semester(
            major=major,
            semester_index=i,
            total_semesters=num_semesters,
            num_courses=num_courses,
            taken_codes=taken_codes,
        )

        # Add grades and create transcript entries
        for course in semester_courses:
            grade = generate_grade(performance)
            taken_codes.add(course.code)

            all_courses.append(
                TranscriptCourse(
                    code=course.code,
                    title=course.title,
                    credits=course.credits,
                    grade=grade,
                    semester=semester,
                )
            )

    return Transcript(
        major=major,
        courses=all_courses,
        semesters=semesters,
    )


def _generate_semester_labels(num_semesters: int, start_year: int) -> list[str]:
    """
    Generate semester labels like 'Fall 2023', 'Spring 2024'.

    Academic year pattern: Fall YYYY -> Spring YYYY+1 -> Fall YYYY+1 -> Spring YYYY+2
    (Spring semester is in the calendar year following the Fall semester)

    Args:
        num_semesters: Number of semesters to generate
        start_year: Starting academic year (year of first Fall semester)

    Returns:
        List of semester label strings
    """
    labels = []
    year = start_year
    is_fall = True  # Start with Fall semester

    for _ in range(num_semesters):
        if is_fall:
            labels.append(f"Fall {year}")
        else:
            # Spring is in the calendar year after Fall
            labels.append(f"Spring {year + 1}")
            year += 1  # Move to next academic year after Spring

        is_fall = not is_fall

    return labels


def _select_courses_for_semester(
    major: Major,
    semester_index: int,
    total_semesters: int,
    num_courses: int,
    taken_codes: set[str],
) -> list[Course]:
    """
    Select appropriate courses based on semester progression.

    Strategy:
    - Early semesters (0-1): 100-level, more gen-ed
    - Middle semesters (1-2): 200-level, mix of core/support
    - Later semesters (3+): 300-400 level, more advanced

    Args:
        major: Student's major
        semester_index: Current semester (0-indexed)
        total_semesters: Total semesters in transcript
        num_courses: Number of courses to select
        taken_codes: Set of already-taken course codes

    Returns:
        List of Course objects for this semester
    """
    selected: list[Course] = []
    progress_ratio = semester_index / max(1, total_semesters - 1)

    # Determine course level distribution based on progress
    if progress_ratio < 0.3:
        # Early: mostly 100-level
        target_levels = [100, 100, 100, 200]
    elif progress_ratio < 0.6:
        # Middle: mix of 100-200
        target_levels = [100, 200, 200, 200, 300]
    else:
        # Later: 200-300-400
        target_levels = [200, 300, 300, 300, 400]

    # Determine department distribution
    # Early semesters: more gen-ed; Later: more core
    if progress_ratio < 0.4:
        # ~50% core/support, ~50% gen-ed
        dept_weights = {
            "core": 2,
            "support": 2,
            "gen_ed": 4,
        }
    else:
        # ~70% core/support, ~30% gen-ed
        dept_weights = {
            "core": 4,
            "support": 3,
            "gen_ed": 2,
        }

    # Select courses
    attempts = 0
    max_attempts = num_courses * 10  # Prevent infinite loops

    while len(selected) < num_courses and attempts < max_attempts:
        attempts += 1

        # Pick department type
        dept_type = random.choices(
            ["core", "support", "gen_ed"],
            weights=[dept_weights["core"], dept_weights["support"], dept_weights["gen_ed"]],
            k=1,
        )[0]

        # Get department list for this type
        if dept_type == "core":
            depts = major.core_departments
        elif dept_type == "support":
            depts = major.support_departments
        else:
            depts = major.gen_ed_departments

        if not depts:
            continue

        # Pick a department
        dept = random.choice(depts)

        # Pick a target level
        target_level = random.choice(target_levels)

        # Get candidate courses
        candidates = get_courses_by_department(dept)
        candidates = [
            c
            for c in candidates
            if c.code not in taken_codes
            and c.code not in {s.code for s in selected}
            and c.level <= target_level + 100  # Allow one level up
            and c.level >= max(100, target_level - 100)  # Allow one level down
        ]

        if candidates:
            # Prefer courses at target level
            at_target = [c for c in candidates if c.level == target_level]
            if at_target:
                selected.append(random.choice(at_target))
            else:
                selected.append(random.choice(candidates))

    return selected
