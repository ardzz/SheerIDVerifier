"""
University major definitions with course requirements.

Defines popular undergraduate majors with:
- Core departments (primary courses)
- Support departments (related courses)
- General education departments (breadth requirements)
"""

import random
from dataclasses import dataclass


@dataclass
class Major:
    """Academic major definition."""

    code: str  # Short code (e.g., "CS")
    name: str  # Full name (e.g., "Computer Science (BS)")
    core_departments: list[str]  # Primary course departments
    support_departments: list[str]  # Secondary/related departments
    gen_ed_departments: list[str]  # General education departments

    def get_all_departments(self) -> list[str]:
        """Get all departments associated with this major."""
        return list(set(self.core_departments + self.support_departments + self.gen_ed_departments))


# Major definitions - 10 popular undergraduate majors
MAJORS: dict[str, Major] = {
    "computer_science": Major(
        code="CS",
        name="Computer Science (BS)",
        core_departments=["CS"],
        support_departments=["MATH", "STAT", "PHYS"],
        gen_ed_departments=["ENG", "HIST", "PHIL", "COMM"],
    ),
    "software_engineering": Major(
        code="SE",
        name="Software Engineering (BS)",
        core_departments=["CS"],
        support_departments=["MATH", "STAT", "BUSN"],
        gen_ed_departments=["ENG", "COMM", "PHIL"],
    ),
    "data_science": Major(
        code="DS",
        name="Data Science (BS)",
        core_departments=["CS", "STAT"],
        support_departments=["MATH", "ECON"],
        gen_ed_departments=["ENG", "COMM", "BUSN"],
    ),
    "business_administration": Major(
        code="BUSN",
        name="Business Administration (BS)",
        core_departments=["BUSN"],
        support_departments=["ECON", "MATH", "STAT"],
        gen_ed_departments=["ENG", "COMM", "PSYCH", "POLS"],
    ),
    "economics": Major(
        code="ECON",
        name="Economics (BA)",
        core_departments=["ECON"],
        support_departments=["MATH", "STAT", "BUSN"],
        gen_ed_departments=["ENG", "HIST", "POLS", "PHIL"],
    ),
    "biology": Major(
        code="BIO",
        name="Biology (BS)",
        core_departments=["BIO"],
        support_departments=["CHEM", "PHYS", "MATH"],
        gen_ed_departments=["ENG", "HIST", "PSYCH"],
    ),
    "psychology": Major(
        code="PSYCH",
        name="Psychology (BA)",
        core_departments=["PSYCH"],
        support_departments=["BIO", "STAT", "SOC"],
        gen_ed_departments=["ENG", "PHIL", "COMM", "HIST"],
    ),
    "engineering": Major(
        code="ENGR",
        name="Engineering (BS)",
        core_departments=["PHYS", "MATH"],
        support_departments=["CS", "CHEM"],
        gen_ed_departments=["ENG", "HIST", "COMM", "ECON"],
    ),
    "political_science": Major(
        code="POLS",
        name="Political Science (BA)",
        core_departments=["POLS"],
        support_departments=["HIST", "ECON", "SOC"],
        gen_ed_departments=["ENG", "PHIL", "COMM", "STAT"],
    ),
    "communications": Major(
        code="COMM",
        name="Communications (BA)",
        core_departments=["COMM"],
        support_departments=["ENG", "PSYCH", "SOC"],
        gen_ed_departments=["HIST", "PHIL", "POLS", "BUSN"],
    ),
}

# List of major keys for random selection
_MAJOR_KEYS = list(MAJORS.keys())


def get_major(key: str) -> Major | None:
    """
    Get a major by its key.

    Args:
        key: Major key (e.g., "computer_science", "biology")

    Returns:
        Major object or None if not found
    """
    return MAJORS.get(key)


def get_random_major() -> Major:
    """
    Select a random major.

    Returns:
        Randomly selected Major object
    """
    key = random.choice(_MAJOR_KEYS)
    return MAJORS[key]


def get_major_by_code(code: str) -> Major | None:
    """
    Find a major by its department code.

    Args:
        code: Department code (e.g., "CS", "BIO")

    Returns:
        Major object or None if not found
    """
    for major in MAJORS.values():
        if major.code == code:
            return major
    return None


def list_major_names() -> list[str]:
    """Get list of all major names for display."""
    return [m.name for m in MAJORS.values()]
