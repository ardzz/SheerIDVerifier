"""Student data model with Faker integration."""

import random
from dataclasses import dataclass

from faker import Faker

# Initialize Faker with US locale for realistic names
_faker = Faker("en_US")


@dataclass
class Student:
    """Student data for SheerID verification."""

    first_name: str
    last_name: str
    email: str
    birth_date: str
    major: str | None = None

    @classmethod
    def generate(cls, domain: str) -> "Student":
        """
        Generate a random student with realistic data.

        Args:
            domain: University email domain (e.g., "ucla.edu")

        Returns:
            Student instance with randomly generated data
        """
        first_name = _faker.first_name()
        last_name = _faker.last_name()
        email = _generate_email(first_name, last_name, domain)
        birth_date = _generate_birth_date()

        return cls(
            first_name=first_name,
            last_name=last_name,
            email=email,
            birth_date=birth_date,
        )

    @property
    def full_name(self) -> str:
        """Return full name."""
        return f"{self.first_name} {self.last_name}"


def _generate_email(first: str, last: str, domain: str) -> str:
    """
    Generate a realistic student email address.

    Args:
        first: First name
        last: Last name
        domain: University domain

    Returns:
        Generated email address
    """
    patterns = [
        f"{first[0].lower()}{last.lower()}{random.randint(100, 999)}",
        f"{first.lower()}.{last.lower()}{random.randint(10, 99)}",
        f"{last.lower()}{first[0].lower()}{random.randint(100, 999)}",
        f"{first.lower()}{last[0].lower()}{random.randint(10, 99)}",
    ]
    return f"{random.choice(patterns)}@{domain}"


def _generate_birth_date() -> str:
    """
    Generate a birth date for a college-age student.

    Returns:
        Birth date in YYYY-MM-DD format
    """
    year = random.randint(2000, 2006)
    month = random.randint(1, 12)
    day = random.randint(1, 28)  # Safe for all months
    return f"{year}-{month:02d}-{day:02d}"
