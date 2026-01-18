"""
Class Schedule HTML Generator.

Generates a realistic student portal class schedule view for the current semester.
This format is often more effective for verification than transcripts because:
- Shows current term explicitly
- Simple, focused format
- Common document type students submit
"""

import datetime
import html
import random
from typing import Any, Dict, List


def get_current_semester() -> tuple[str, int]:
    """
    Get the current academic semester based on today's date.

    Returns:
        Tuple of (semester_name, year) e.g. ("Spring", 2026)
    """
    now = datetime.datetime.now()
    month = now.month
    year = now.year

    # Academic calendar:
    # Spring: January - May
    # Summer: June - July
    # Fall: August - December
    if month >= 1 and month <= 5:
        return ("Spring", year)
    elif month >= 6 and month <= 7:
        return ("Summer", year)
    else:  # August - December
        return ("Fall", year)


def get_semester_dates(semester: str, year: int) -> tuple[str, str]:
    """
    Get start and end dates for a semester.

    Args:
        semester: "Spring", "Summer", or "Fall"
        year: Academic year

    Returns:
        Tuple of (start_date, end_date) as formatted strings
    """
    if semester == "Spring":
        start = datetime.date(year, 1, 13)  # Mid-January
        end = datetime.date(year, 5, 10)  # Early May
    elif semester == "Summer":
        start = datetime.date(year, 6, 3)  # Early June
        end = datetime.date(year, 7, 26)  # Late July
    else:  # Fall
        start = datetime.date(year, 8, 26)  # Late August
        end = datetime.date(year, 12, 13)  # Mid-December

    return (start.strftime("%B %d, %Y"), end.strftime("%B %d, %Y"))


def generate_class_times() -> tuple[List[tuple[str, str]], List[str]]:
    """Generate realistic class meeting times."""
    time_slots = [
        ("8:00 AM", "9:15 AM"),
        ("9:30 AM", "10:45 AM"),
        ("11:00 AM", "12:15 PM"),
        ("12:30 PM", "1:45 PM"),
        ("2:00 PM", "3:15 PM"),
        ("3:30 PM", "4:45 PM"),
        ("5:00 PM", "6:15 PM"),
        ("6:30 PM", "7:45 PM"),
    ]

    day_patterns = [
        "MWF",  # Monday, Wednesday, Friday
        "TR",  # Tuesday, Thursday
        "MW",  # Monday, Wednesday
        "MF",  # Monday, Friday
        "W",  # Wednesday only
    ]

    return time_slots, day_patterns


def generate_sample_courses(num_courses: int = 5) -> List[Dict[str, Any]]:
    """Generate sample courses for testing."""
    sample_courses = [
        {"code": "CS 301", "title": "Data Structures and Algorithms", "credits": 3},
        {"code": "CS 350", "title": "Operating Systems", "credits": 3},
        {"code": "MATH 301", "title": "Linear Algebra", "credits": 3},
        {"code": "PHYS 202", "title": "Physics II: Electricity and Magnetism", "credits": 4},
        {"code": "ENGL 201", "title": "Technical Writing", "credits": 3},
        {"code": "CS 401", "title": "Software Engineering", "credits": 3},
        {"code": "CS 320", "title": "Database Systems", "credits": 3},
        {"code": "STAT 301", "title": "Probability and Statistics", "credits": 3},
    ]

    return random.sample(sample_courses, min(num_courses, len(sample_courses)))


def _generate_schedule_courses(num_courses: int = 5) -> List[Dict[str, Any]]:
    """
    Generate courses with full schedule information.

    Returns list of courses with code, title, credits, days, time, location, instructor.
    """
    time_slots, day_patterns = generate_class_times()

    # Course pool with diverse departments
    course_pool = [
        {"code": "CS 301", "title": "Data Structures and Algorithms", "credits": 3},
        {"code": "CS 350", "title": "Operating Systems", "credits": 3},
        {"code": "CS 320", "title": "Database Systems", "credits": 3},
        {"code": "CS 401", "title": "Software Engineering", "credits": 3},
        {"code": "CS 410", "title": "Machine Learning", "credits": 3},
        {"code": "MATH 301", "title": "Linear Algebra", "credits": 3},
        {"code": "MATH 320", "title": "Differential Equations", "credits": 3},
        {"code": "PHYS 202", "title": "Physics II: Electricity and Magnetism", "credits": 4},
        {"code": "ENGL 201", "title": "Technical Writing", "credits": 3},
        {"code": "STAT 301", "title": "Probability and Statistics", "credits": 3},
        {"code": "ECON 201", "title": "Microeconomics", "credits": 3},
        {"code": "PSYC 101", "title": "Introduction to Psychology", "credits": 3},
    ]

    # Buildings for locations
    buildings = [
        "Science Hall",
        "Engineering Building",
        "Math Sciences",
        "Liberal Arts",
        "Technology Center",
        "Main Hall",
    ]

    # Instructor last names
    instructors = [
        "Smith",
        "Johnson",
        "Williams",
        "Brown",
        "Jones",
        "Garcia",
        "Miller",
        "Davis",
        "Rodriguez",
        "Martinez",
        "Anderson",
        "Taylor",
    ]

    selected = random.sample(course_pool, min(num_courses, len(course_pool)))
    used_slots: set[tuple[str, str]] = set()  # (days, time) to avoid conflicts

    result = []
    for course in selected:
        # Find non-conflicting time slot
        days = random.choice(day_patterns)
        time_slot = random.choice(time_slots)
        time_str = f"{time_slot[0]} - {time_slot[1]}"

        for _ in range(20):
            # Check for conflicts (same days with overlapping times)
            conflict = False
            for used_days, used_time in used_slots:
                if any(d in used_days for d in days):
                    if used_time == time_str:
                        conflict = True
                        break

            if not conflict:
                used_slots.add((days, time_str))
                break

            # Try different slot
            days = random.choice(day_patterns)
            time_slot = random.choice(time_slots)
            time_str = f"{time_slot[0]} - {time_slot[1]}"

        # Generate location
        building = random.choice(buildings)
        room = random.randint(100, 450)
        location = f"{building} {room}"

        # Generate instructor
        instructor = f"Dr. {random.choice(instructors)}"

        result.append(
            {
                "code": course["code"],
                "title": course["title"],
                "credits": course["credits"],
                "days": days,
                "time": time_str,
                "location": location,
                "instructor": instructor,
            }
        )

    return result


def generate_class_schedule_html(
    school_name: str,
    student_name: str,
    student_id: str,
    courses: List[Dict[str, Any]] | None = None,
    num_courses: int = 5,
) -> str:
    """
    Generate HTML for a student portal class schedule.

    This produces a realistic "My Schedule" page that students would screenshot
    from their university portal. Includes current term dates prominently.

    Args:
        school_name: University/college name
        student_name: Student's full name
        student_id: Student ID number
        courses: Optional list of course dicts. If None, generates random courses.
        num_courses: Number of courses to generate if courses is None

    Returns:
        Complete HTML string ready for rendering
    """
    # Get current semester info
    semester, year = get_current_semester()
    start_date, end_date = get_semester_dates(semester, year)

    # Generate courses if not provided
    if courses is None:
        courses = _generate_schedule_courses(num_courses)

    # Calculate total credits
    total_credits = sum(c["credits"] for c in courses)

    # Current timestamp
    now = datetime.datetime.now()
    generated_date = now.strftime("%B %d, %Y")
    generated_time = now.strftime("%I:%M %p")

    # Escape all user inputs
    school_name_safe = html.escape(school_name)
    student_name_safe = html.escape(student_name)
    student_id_safe = html.escape(student_id)

    # Build course rows
    course_rows = ""
    for course in courses:
        course_rows += f"""
            <tr>
                <td class="course-code">{html.escape(course["code"])}</td>
                <td class="course-title">{html.escape(course["title"])}</td>
                <td class="course-credits">{course["credits"]}</td>
                <td class="course-days">{html.escape(course["days"])}</td>
                <td class="course-time">{html.escape(course["time"])}</td>
                <td class="course-location">{html.escape(course["location"])}</td>
                <td class="course-instructor">{html.escape(course["instructor"])}</td>
            </tr>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Class Schedule - {semester} {year}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background-color: #f5f5f5;
            color: #333;
            line-height: 1.5;
        }}
        
        .container {{
            max-width: 1100px;
            margin: 0 auto;
            background: #fff;
            min-height: 100vh;
        }}
        
        /* Header */
        .header {{
            background: linear-gradient(135deg, #1a365d 0%, #2c5282 100%);
            color: #fff;
            padding: 20px 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .header h1 {{
            font-size: 22px;
            font-weight: 600;
        }}
        
        .header .student-info {{
            text-align: right;
            font-size: 14px;
        }}
        
        .header .student-name {{
            font-weight: 600;
            font-size: 16px;
        }}
        
        /* Term Banner */
        .term-banner {{
            background: #e8f4fd;
            border-left: 4px solid #2b6cb0;
            padding: 15px 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .term-banner h2 {{
            color: #2b6cb0;
            font-size: 18px;
            font-weight: 600;
        }}
        
        .term-banner .term-dates {{
            color: #4a5568;
            font-size: 14px;
        }}
        
        /* Content */
        .content {{
            padding: 25px 30px;
        }}
        
        .schedule-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 1px solid #e2e8f0;
        }}
        
        .schedule-header h3 {{
            font-size: 16px;
            color: #2d3748;
        }}
        
        .enrollment-status {{
            display: inline-flex;
            align-items: center;
            background: #c6f6d5;
            color: #276749;
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 13px;
            font-weight: 600;
        }}
        
        .enrollment-status::before {{
            content: "";
            display: inline-block;
            width: 8px;
            height: 8px;
            background: #276749;
            border-radius: 50%;
            margin-right: 8px;
        }}
        
        /* Schedule Table */
        .schedule-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
        }}
        
        .schedule-table thead {{
            background: #f7fafc;
        }}
        
        .schedule-table th {{
            text-align: left;
            padding: 12px 10px;
            font-weight: 600;
            color: #4a5568;
            border-bottom: 2px solid #e2e8f0;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .schedule-table td {{
            padding: 14px 10px;
            border-bottom: 1px solid #e2e8f0;
            vertical-align: top;
        }}
        
        .schedule-table tbody tr:hover {{
            background: #f7fafc;
        }}
        
        .course-code {{
            font-weight: 600;
            color: #2b6cb0;
            white-space: nowrap;
        }}
        
        .course-title {{
            color: #2d3748;
        }}
        
        .course-credits {{
            text-align: center;
            font-weight: 500;
        }}
        
        .course-days {{
            font-weight: 500;
            color: #4a5568;
        }}
        
        .course-time {{
            white-space: nowrap;
            color: #4a5568;
        }}
        
        .course-location {{
            color: #718096;
            font-size: 13px;
        }}
        
        .course-instructor {{
            color: #718096;
            font-size: 13px;
        }}
        
        /* Summary */
        .schedule-summary {{
            margin-top: 25px;
            padding: 20px;
            background: #f7fafc;
            border-radius: 8px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .summary-item {{
            text-align: center;
        }}
        
        .summary-item .label {{
            font-size: 12px;
            color: #718096;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .summary-item .value {{
            font-size: 24px;
            font-weight: 700;
            color: #2d3748;
            margin-top: 4px;
        }}
        
        .summary-item .value.credits {{
            color: #2b6cb0;
        }}
        
        /* Footer */
        .footer {{
            margin-top: 30px;
            padding: 15px 0;
            border-top: 1px solid #e2e8f0;
            font-size: 12px;
            color: #a0aec0;
            display: flex;
            justify-content: space-between;
        }}
        
        .footer .generated {{
            color: #718096;
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>{school_name_safe}</h1>
            <div class="student-info">
                <div class="student-name">{student_name_safe}</div>
                <div>ID: {student_id_safe}</div>
            </div>
        </div>
        
        <!-- Term Banner -->
        <div class="term-banner">
            <h2>{semester} {year} - Registered Classes</h2>
            <div class="term-dates">{start_date} - {end_date}</div>
        </div>
        
        <!-- Content -->
        <div class="content">
            <div class="schedule-header">
                <h3>My Class Schedule</h3>
                <span class="enrollment-status">Enrolled</span>
            </div>
            
            <!-- Schedule Table -->
            <table class="schedule-table">
                <thead>
                    <tr>
                        <th>Course</th>
                        <th>Title</th>
                        <th>Credits</th>
                        <th>Days</th>
                        <th>Time</th>
                        <th>Location</th>
                        <th>Instructor</th>
                    </tr>
                </thead>
                <tbody>
                    {course_rows}
                </tbody>
            </table>
            
            <!-- Summary -->
            <div class="schedule-summary">
                <div class="summary-item">
                    <div class="label">Total Courses</div>
                    <div class="value">{len(courses)}</div>
                </div>
                <div class="summary-item">
                    <div class="label">Total Credits</div>
                    <div class="value credits">{total_credits}</div>
                </div>
                <div class="summary-item">
                    <div class="label">Academic Standing</div>
                    <div class="value">Good</div>
                </div>
                <div class="summary-item">
                    <div class="label">Enrollment Status</div>
                    <div class="value">Full-Time</div>
                </div>
            </div>
            
            <!-- Footer -->
            <div class="footer">
                <span>Student Information System</span>
                <span class="generated">Generated: {generated_date} at {generated_time}</span>
            </div>
        </div>
    </div>
</body>
</html>"""
