"""University data model and selection logic."""

import random
from dataclasses import dataclass
from typing import Callable


@dataclass
class University:
    """University data for SheerID verification."""

    id: int
    name: str
    domain: str
    weight: int = 50  # Base weight for selection probability

    @property
    def id_extended(self) -> str:
        """Return ID as string for API compatibility."""
        return str(self.id)

    def to_api_dict(self) -> dict:
        """Convert to dictionary format expected by SheerID API."""
        return {
            "id": self.id,
            "idExtended": self.id_extended,
            "name": self.name,
        }


# University list with weights (higher = more likely to be selected)
# NOTE: As of Jan 2026, new Gemini student sign-ups are US-ONLY
UNIVERSITIES: list[University] = [
    # =========== USA - HIGH PRIORITY ===========
    University(2565, "Pennsylvania State University-Main Campus", "psu.edu", 100),
    University(3499, "University of California, Los Angeles", "ucla.edu", 98),
    University(3491, "University of California, Berkeley", "berkeley.edu", 97),
    University(1953, "Massachusetts Institute of Technology", "mit.edu", 95),
    University(3113, "Stanford University", "stanford.edu", 95),
    University(2285, "New York University", "nyu.edu", 96),
    University(1426, "Harvard University", "harvard.edu", 92),
    University(590759, "Yale University", "yale.edu", 90),
    University(2626, "Princeton University", "princeton.edu", 90),
    University(698, "Columbia University", "columbia.edu", 92),
    University(3508, "University of Chicago", "uchicago.edu", 88),
    University(943, "Duke University", "duke.edu", 88),
    University(751, "Cornell University", "cornell.edu", 90),
    University(2420, "Northwestern University", "northwestern.edu", 88),
    University(3568, "University of Michigan", "umich.edu", 95),
    University(3686, "University of Texas at Austin", "utexas.edu", 94),
    University(1217, "Georgia Institute of Technology", "gatech.edu", 93),
    University(602, "Carnegie Mellon University", "cmu.edu", 92),
    University(3477, "University of California, San Diego", "ucsd.edu", 93),
    University(3600, "University of North Carolina at Chapel Hill", "unc.edu", 90),
    University(3645, "University of Southern California", "usc.edu", 91),
    University(3629, "University of Pennsylvania", "upenn.edu", 90),
    University(1603, "Indiana University Bloomington", "iu.edu", 88),
    University(2506, "Ohio State University", "osu.edu", 90),
    University(2700, "Purdue University", "purdue.edu", 89),
    University(3761, "University of Washington", "uw.edu", 90),
    University(3770, "University of Wisconsin-Madison", "wisc.edu", 88),
    University(3562, "University of Maryland", "umd.edu", 87),
    University(519, "Boston University", "bu.edu", 86),
    University(378, "Arizona State University", "asu.edu", 92),
    University(3521, "University of Florida", "ufl.edu", 90),
    University(3535, "University of Illinois at Urbana-Champaign", "illinois.edu", 91),
    University(3557, "University of Minnesota Twin Cities", "umn.edu", 88),
    University(3483, "University of California, Davis", "ucdavis.edu", 89),
    University(3487, "University of California, Irvine", "uci.edu", 88),
    University(3502, "University of California, Santa Barbara", "ucsb.edu", 87),
    # Community Colleges
    University(2874, "Santa Monica College", "smc.edu", 85),
    University(2350, "Northern Virginia Community College", "nvcc.edu", 84),
    # =========== OTHER COUNTRIES (Lower priority) ===========
    # Canada
    University(328355, "University of Toronto", "utoronto.ca", 40),
    University(328315, "University of British Columbia", "ubc.ca", 38),
    # UK
    University(273409, "University of Oxford", "ox.ac.uk", 35),
    University(273378, "University of Cambridge", "cam.ac.uk", 35),
    # India
    University(10007277, "Indian Institute of Technology Delhi", "iitd.ac.in", 20),
    University(3819983, "University of Mumbai", "mu.ac.in", 15),
    # Australia
    University(345301, "The University of Melbourne", "unimelb.edu.au", 30),
    University(345303, "The University of Sydney", "sydney.edu.au", 28),
]


def select_university(
    success_rate_getter: Callable[[str], float] | None = None,
) -> University:
    """
    Select a university using weighted random selection.

    Weight is modified by historical success rate if provided.

    Args:
        success_rate_getter: Optional callable that takes university name
                            and returns success rate (0-100). If not provided,
                            only base weights are used.

    Returns:
        Selected University instance
    """
    weights = []
    for uni in UNIVERSITIES:
        weight = uni.weight
        if success_rate_getter:
            # Adjust weight based on success rate (baseline 50%)
            rate = success_rate_getter(uni.name)
            weight = weight * (rate / 50)
        weights.append(max(1.0, weight))

    total = sum(weights)
    r = random.uniform(0, total)

    cumulative = 0.0
    for uni, weight in zip(UNIVERSITIES, weights):
        cumulative += weight
        if r <= cumulative:
            return uni

    # Fallback to first university
    return UNIVERSITIES[0]
