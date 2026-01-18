"""
University course catalog organized by department.

Provides ~100 courses across 15 departments with realistic
course codes, titles, credit hours, and levels.
"""

import random
from dataclasses import dataclass


@dataclass
class Course:
    """Academic course definition."""

    code: str  # e.g., "CS101" (no space)
    title: str  # e.g., "Introduction to Programming"
    credits: int  # 1-4 typical
    level: int  # 100, 200, 300, 400
    department: str  # Department code (e.g., "CS")

    def to_dict(self) -> dict:
        """Convert to dictionary for transcript generation."""
        return {
            "code": self.code,
            "title": self.title,
            "credits": self.credits,
            "level": self.level,
            "department": self.department,
        }


# Department definitions
DEPARTMENTS: dict[str, str] = {
    "CS": "Computer Science",
    "MATH": "Mathematics",
    "PHYS": "Physics",
    "CHEM": "Chemistry",
    "BIO": "Biology",
    "ENG": "English",
    "ECON": "Economics",
    "PSYCH": "Psychology",
    "HIST": "History",
    "POLS": "Political Science",
    "SOC": "Sociology",
    "PHIL": "Philosophy",
    "STAT": "Statistics",
    "COMM": "Communications",
    "BUSN": "Business",
}

# Course catalog - ~100 courses across 15 departments
COURSE_CATALOG: list[Course] = [
    # ===== COMPUTER SCIENCE (CS) - 12 courses =====
    Course("CS101", "Introduction to Programming", 4, 100, "CS"),
    Course("CS102", "Programming Fundamentals", 4, 100, "CS"),
    Course("CS201", "Data Structures", 3, 200, "CS"),
    Course("CS210", "Computer Architecture", 3, 200, "CS"),
    Course("CS251", "Algorithms", 3, 200, "CS"),
    Course("CS260", "Object-Oriented Programming", 3, 200, "CS"),
    Course("CS301", "Operating Systems", 3, 300, "CS"),
    Course("CS310", "Database Systems", 3, 300, "CS"),
    Course("CS320", "Software Engineering", 3, 300, "CS"),
    Course("CS350", "Computer Networks", 3, 300, "CS"),
    Course("CS401", "Machine Learning", 3, 400, "CS"),
    Course("CS410", "Artificial Intelligence", 3, 400, "CS"),
    # ===== MATHEMATICS (MATH) - 10 courses =====
    Course("MATH101", "College Algebra", 3, 100, "MATH"),
    Course("MATH110", "Pre-Calculus", 3, 100, "MATH"),
    Course("MATH151", "Calculus I", 4, 100, "MATH"),
    Course("MATH152", "Calculus II", 4, 100, "MATH"),
    Course("MATH201", "Calculus III", 4, 200, "MATH"),
    Course("MATH220", "Linear Algebra", 3, 200, "MATH"),
    Course("MATH250", "Discrete Mathematics", 3, 200, "MATH"),
    Course("MATH301", "Differential Equations", 3, 300, "MATH"),
    Course("MATH310", "Abstract Algebra", 3, 300, "MATH"),
    Course("MATH350", "Real Analysis", 3, 300, "MATH"),
    # ===== PHYSICS (PHYS) - 7 courses =====
    Course("PHYS101", "General Physics I", 4, 100, "PHYS"),
    Course("PHYS102", "General Physics II", 4, 100, "PHYS"),
    Course("PHYS201", "Modern Physics", 3, 200, "PHYS"),
    Course("PHYS210", "Mechanics", 3, 200, "PHYS"),
    Course("PHYS220", "Electromagnetism", 3, 200, "PHYS"),
    Course("PHYS301", "Thermodynamics", 3, 300, "PHYS"),
    Course("PHYS310", "Quantum Mechanics", 3, 300, "PHYS"),
    # ===== CHEMISTRY (CHEM) - 6 courses =====
    Course("CHEM101", "General Chemistry I", 4, 100, "CHEM"),
    Course("CHEM102", "General Chemistry II", 4, 100, "CHEM"),
    Course("CHEM201", "Organic Chemistry I", 4, 200, "CHEM"),
    Course("CHEM202", "Organic Chemistry II", 4, 200, "CHEM"),
    Course("CHEM301", "Physical Chemistry", 3, 300, "CHEM"),
    Course("CHEM310", "Biochemistry", 3, 300, "CHEM"),
    # ===== BIOLOGY (BIO) - 7 courses =====
    Course("BIO101", "Introduction to Biology", 4, 100, "BIO"),
    Course("BIO102", "Biology II", 4, 100, "BIO"),
    Course("BIO201", "Cell Biology", 3, 200, "BIO"),
    Course("BIO210", "Genetics", 3, 200, "BIO"),
    Course("BIO220", "Ecology", 3, 200, "BIO"),
    Course("BIO301", "Molecular Biology", 3, 300, "BIO"),
    Course("BIO310", "Microbiology", 3, 300, "BIO"),
    # ===== ENGLISH (ENG) - 6 courses =====
    Course("ENG101", "College Writing", 3, 100, "ENG"),
    Course("ENG102", "Academic Writing", 3, 100, "ENG"),
    Course("ENG201", "American Literature", 3, 200, "ENG"),
    Course("ENG210", "British Literature", 3, 200, "ENG"),
    Course("ENG220", "Technical Writing", 3, 200, "ENG"),
    Course("ENG301", "Creative Writing", 3, 300, "ENG"),
    # ===== ECONOMICS (ECON) - 7 courses =====
    Course("ECON101", "Principles of Microeconomics", 3, 100, "ECON"),
    Course("ECON102", "Principles of Macroeconomics", 3, 100, "ECON"),
    Course("ECON201", "Intermediate Microeconomics", 3, 200, "ECON"),
    Course("ECON202", "Intermediate Macroeconomics", 3, 200, "ECON"),
    Course("ECON301", "Econometrics", 3, 300, "ECON"),
    Course("ECON310", "International Economics", 3, 300, "ECON"),
    Course("ECON320", "Financial Economics", 3, 300, "ECON"),
    # ===== PSYCHOLOGY (PSYCH) - 7 courses =====
    Course("PSYCH101", "Introduction to Psychology", 3, 100, "PSYCH"),
    Course("PSYCH110", "Developmental Psychology", 3, 100, "PSYCH"),
    Course("PSYCH201", "Social Psychology", 3, 200, "PSYCH"),
    Course("PSYCH210", "Cognitive Psychology", 3, 200, "PSYCH"),
    Course("PSYCH220", "Abnormal Psychology", 3, 200, "PSYCH"),
    Course("PSYCH301", "Research Methods", 3, 300, "PSYCH"),
    Course("PSYCH310", "Behavioral Neuroscience", 3, 300, "PSYCH"),
    # ===== HISTORY (HIST) - 6 courses =====
    Course("HIST101", "World History I", 3, 100, "HIST"),
    Course("HIST102", "World History II", 3, 100, "HIST"),
    Course("HIST110", "American History", 3, 100, "HIST"),
    Course("HIST201", "European History", 3, 200, "HIST"),
    Course("HIST210", "Modern World History", 3, 200, "HIST"),
    Course("HIST301", "Historical Research Methods", 3, 300, "HIST"),
    # ===== POLITICAL SCIENCE (POLS) - 6 courses =====
    Course("POLS101", "Introduction to Political Science", 3, 100, "POLS"),
    Course("POLS110", "American Government", 3, 100, "POLS"),
    Course("POLS201", "Comparative Politics", 3, 200, "POLS"),
    Course("POLS210", "International Relations", 3, 200, "POLS"),
    Course("POLS301", "Political Theory", 3, 300, "POLS"),
    Course("POLS310", "Public Policy", 3, 300, "POLS"),
    # ===== SOCIOLOGY (SOC) - 5 courses =====
    Course("SOC101", "Introduction to Sociology", 3, 100, "SOC"),
    Course("SOC201", "Social Problems", 3, 200, "SOC"),
    Course("SOC210", "Race and Ethnicity", 3, 200, "SOC"),
    Course("SOC220", "Family and Society", 3, 200, "SOC"),
    Course("SOC301", "Sociological Theory", 3, 300, "SOC"),
    # ===== PHILOSOPHY (PHIL) - 5 courses =====
    Course("PHIL101", "Introduction to Philosophy", 3, 100, "PHIL"),
    Course("PHIL110", "Ethics", 3, 100, "PHIL"),
    Course("PHIL201", "Logic", 3, 200, "PHIL"),
    Course("PHIL210", "Philosophy of Science", 3, 200, "PHIL"),
    Course("PHIL301", "Metaphysics", 3, 300, "PHIL"),
    # ===== STATISTICS (STAT) - 5 courses =====
    Course("STAT101", "Introduction to Statistics", 3, 100, "STAT"),
    Course("STAT201", "Statistical Methods", 3, 200, "STAT"),
    Course("STAT210", "Probability Theory", 3, 200, "STAT"),
    Course("STAT301", "Regression Analysis", 3, 300, "STAT"),
    Course("STAT310", "Statistical Computing", 3, 300, "STAT"),
    # ===== COMMUNICATIONS (COMM) - 6 courses =====
    Course("COMM101", "Public Speaking", 3, 100, "COMM"),
    Course("COMM110", "Interpersonal Communication", 3, 100, "COMM"),
    Course("COMM201", "Mass Media and Society", 3, 200, "COMM"),
    Course("COMM210", "Persuasion", 3, 200, "COMM"),
    Course("COMM220", "Digital Media", 3, 200, "COMM"),
    Course("COMM301", "Organizational Communication", 3, 300, "COMM"),
    # ===== BUSINESS (BUSN) - 8 courses =====
    Course("BUSN101", "Introduction to Business", 3, 100, "BUSN"),
    Course("BUSN110", "Business Communication", 3, 100, "BUSN"),
    Course("BUSN201", "Principles of Management", 3, 200, "BUSN"),
    Course("BUSN210", "Marketing Principles", 3, 200, "BUSN"),
    Course("BUSN220", "Financial Accounting", 3, 200, "BUSN"),
    Course("BUSN230", "Managerial Accounting", 3, 200, "BUSN"),
    Course("BUSN301", "Business Law", 3, 300, "BUSN"),
    Course("BUSN310", "Operations Management", 3, 300, "BUSN"),
]

# Build lookup indexes
_COURSES_BY_DEPT: dict[str, list[Course]] = {}
_COURSES_BY_LEVEL: dict[int, list[Course]] = {}
_COURSES_BY_CODE: dict[str, Course] = {}

for _course in COURSE_CATALOG:
    # By department
    if _course.department not in _COURSES_BY_DEPT:
        _COURSES_BY_DEPT[_course.department] = []
    _COURSES_BY_DEPT[_course.department].append(_course)

    # By level
    if _course.level not in _COURSES_BY_LEVEL:
        _COURSES_BY_LEVEL[_course.level] = []
    _COURSES_BY_LEVEL[_course.level].append(_course)

    # By code
    _COURSES_BY_CODE[_course.code] = _course


def get_courses_by_department(dept: str) -> list[Course]:
    """Get all courses for a department."""
    return _COURSES_BY_DEPT.get(dept, [])


def get_courses_by_level(level: int) -> list[Course]:
    """Get all courses at a specific level (100, 200, 300, 400)."""
    return _COURSES_BY_LEVEL.get(level, [])


def get_course_by_code(code: str) -> Course | None:
    """Get a specific course by code."""
    return _COURSES_BY_CODE.get(code)


def get_random_courses(
    departments: list[str] | None = None,
    level: int | None = None,
    count: int = 5,
    exclude: set[str] | None = None,
) -> list[Course]:
    """
    Get random courses with optional filters.

    Args:
        departments: Limit to these departments (None = all)
        level: Limit to this level (None = all)
        count: Number of courses to return
        exclude: Course codes to exclude

    Returns:
        List of randomly selected Course objects
    """
    exclude = exclude or set()

    # Build candidate pool
    candidates = []
    for course in COURSE_CATALOG:
        if course.code in exclude:
            continue
        if departments and course.department not in departments:
            continue
        if level and course.level != level:
            continue
        candidates.append(course)

    # Return random selection
    if len(candidates) <= count:
        return candidates

    return random.sample(candidates, count)


def get_department_name(code: str) -> str:
    """Get full department name from code."""
    return DEPARTMENTS.get(code, code)
