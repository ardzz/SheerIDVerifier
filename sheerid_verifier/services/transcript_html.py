"""
Official Academic Transcript HTML Generator.

This module generates realistic-looking official academic transcript HTML documents
for the purpose of creating verification images. The output resembles a scanned
paper transcript with:
- University letterhead and seal
- Formal document structure
- Registrar signature block
- Watermark for authenticity appearance
- Traditional serif typography

NO web portal elements (nav bars, buttons, links, status badges).
"""

import datetime
import html
from typing import Any, Dict, List


def generate_transcript_html(
    school_name: str,
    student_name: str,
    student_id: str,
    major: str,
    semesters: List[Dict[str, Any]],
    cumulative_gpa: float,
    total_credits: int,
) -> str:
    """
    Generate official academic transcript HTML document.

    Args:
        school_name: University name (e.g., "University of California, Los Angeles")
        student_name: Student's full name
        student_id: Student ID number
        major: Academic program/major
        semesters: List of semester dicts, each containing:
            - semester_name: str (e.g., "Fall 2023")
            - courses: list of course dicts with:
                - code: str (e.g., "CS201")
                - title: str (e.g., "Data Structures")
                - credits: int/float
                - grade: str (e.g., "A", "B+")
        cumulative_gpa: Calculated GPA
        total_credits: Total credits earned

    Returns:
        Complete HTML string ready for Playwright screenshot
    """
    # Escape inputs for safety
    safe_school = html.escape(school_name)
    safe_student = html.escape(student_name)
    safe_id = html.escape(student_id)
    safe_major = html.escape(major)

    # Document dates
    now = datetime.datetime.now()
    issue_date = now.strftime("%B %d, %Y")

    # Generate semester sections
    semesters_html = _generate_semesters_html(semesters)

    # Calculate total semesters for academic standing
    num_semesters = len(semesters)
    class_standing = _get_class_standing(total_credits)

    # Build the complete HTML document
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Official Academic Transcript</title>
    <style>
        /* Page Setup */
        @page {{
            size: 8.5in 11in;
            margin: 0;
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            font-family: "Times New Roman", Times, Georgia, serif;
            background-color: #FEFEFE;
            color: #000000;
            width: 8.5in;
            min-height: 11in;
            margin: 0 auto;
            padding: 0.6in 0.75in;
            line-height: 1.4;
            position: relative;
        }}

        /* Watermark */
        .watermark {{
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%) rotate(-45deg);
            font-size: 60px;
            font-family: "Times New Roman", Times, serif;
            color: rgba(0, 0, 0, 0.035);
            white-space: nowrap;
            pointer-events: none;
            z-index: 1000;
            letter-spacing: 12px;
            font-weight: normal;
            text-transform: uppercase;
        }}

        /* University Letterhead */
        .letterhead {{
            display: flex;
            align-items: flex-start;
            gap: 20px;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 2px solid #000;
        }}

        .seal {{
            flex-shrink: 0;
        }}

        .seal svg {{
            width: 75px;
            height: 75px;
        }}

        .university-info {{
            flex: 1;
        }}

        .university-name {{
            font-size: 22px;
            font-weight: bold;
            text-transform: uppercase;
            letter-spacing: 2px;
            margin-bottom: 4px;
            color: #000;
        }}

        .registrar-office {{
            font-size: 13px;
            font-style: italic;
            margin-bottom: 2px;
            color: #333;
        }}

        .university-address {{
            font-size: 11px;
            color: #444;
        }}

        /* Document Title */
        .document-title {{
            text-align: center;
            font-size: 16px;
            font-weight: bold;
            text-transform: uppercase;
            letter-spacing: 4px;
            margin: 25px 0 20px 0;
            padding: 8px 0;
            border-top: 1px solid #000;
            border-bottom: 1px solid #000;
        }}

        /* Student Information */
        .student-info {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 8px 40px;
            margin-bottom: 25px;
            padding: 12px 15px;
            background-color: #FAFAFA;
            border: 1px solid #DDD;
        }}

        .info-row {{
            display: flex;
            font-size: 11px;
        }}

        .info-label {{
            font-weight: bold;
            width: 110px;
            flex-shrink: 0;
        }}

        .info-value {{
            flex: 1;
        }}

        /* Academic Record Section */
        .academic-record {{
            margin-bottom: 20px;
        }}

        .section-title {{
            font-size: 12px;
            font-weight: bold;
            text-transform: uppercase;
            letter-spacing: 2px;
            margin-bottom: 15px;
            padding-bottom: 5px;
            border-bottom: 1px solid #999;
        }}

        /* Semester Block */
        .semester-block {{
            margin-bottom: 18px;
            page-break-inside: avoid;
        }}

        .semester-header {{
            font-size: 11px;
            font-weight: bold;
            background-color: #F0F0F0;
            padding: 5px 10px;
            border: 1px solid #CCC;
            border-bottom: none;
        }}

        /* Course Table */
        .course-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 10px;
            border: 1px solid #CCC;
        }}

        .course-table th {{
            background-color: #F8F8F8;
            border-bottom: 2px solid #999;
            text-align: left;
            padding: 5px 8px;
            font-weight: bold;
            font-size: 9px;
            text-transform: uppercase;
        }}

        .course-table td {{
            border-bottom: 1px solid #DDD;
            padding: 4px 8px;
            vertical-align: top;
        }}

        .course-table tr:last-child td {{
            border-bottom: none;
        }}

        .course-code {{
            font-weight: 500;
            white-space: nowrap;
        }}

        .course-title {{
            /* Normal weight, no special styling */
        }}

        .course-credits,
        .course-grade {{
            text-align: center;
        }}

        .course-grade {{
            font-weight: bold;
        }}

        /* Term Summary */
        .term-summary {{
            display: flex;
            justify-content: flex-end;
            gap: 30px;
            font-size: 10px;
            padding: 5px 10px;
            background-color: #FAFAFA;
            border: 1px solid #CCC;
            border-top: none;
        }}

        .term-stat {{
            display: flex;
            gap: 5px;
        }}

        .term-stat-label {{
            font-weight: bold;
        }}

        /* Cumulative Summary */
        .cumulative-summary {{
            margin: 25px 0;
            padding: 15px;
            border: 2px solid #000;
            background-color: #FAFAFA;
        }}

        .summary-title {{
            font-size: 11px;
            font-weight: bold;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 10px;
            text-align: center;
        }}

        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 15px;
            text-align: center;
        }}

        .summary-item {{
            display: flex;
            flex-direction: column;
            gap: 3px;
        }}

        .summary-label {{
            font-size: 9px;
            text-transform: uppercase;
            color: #555;
        }}

        .summary-value {{
            font-size: 14px;
            font-weight: bold;
        }}

        /* Signature Block */
        .signature-block {{
            display: flex;
            justify-content: space-between;
            margin-top: 40px;
            padding-top: 20px;
        }}

        .signature-area {{
            text-align: center;
            width: 200px;
        }}

        .signature-line {{
            border-top: 1px solid #000;
            margin-bottom: 5px;
            height: 30px;
        }}

        .signature-label {{
            font-size: 10px;
            font-style: italic;
        }}

        /* Document Footer */
        .document-footer {{
            margin-top: 30px;
            padding-top: 15px;
            border-top: 1px solid #999;
            font-size: 9px;
            color: #555;
        }}

        .footer-text {{
            text-align: center;
            margin-bottom: 5px;
            font-style: italic;
        }}

        .page-number {{
            text-align: right;
            font-size: 9px;
        }}

        /* Grading Scale Legend */
        .grading-legend {{
            margin-top: 15px;
            padding: 8px 12px;
            background-color: #F8F8F8;
            border: 1px solid #DDD;
            font-size: 8px;
        }}

        .legend-title {{
            font-weight: bold;
            font-size: 9px;
            margin-bottom: 5px;
        }}

        .legend-items {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }}

        .legend-item {{
            white-space: nowrap;
        }}

        /* End of Transcript Marker */
        .end-marker {{
            text-align: center;
            margin-top: 20px;
            font-size: 10px;
            font-style: italic;
            color: #666;
        }}
    </style>
</head>
<body>

    <!-- Watermark -->
    <div class="watermark">Official Transcript</div>

    <!-- University Letterhead -->
    <header class="letterhead">
        <div class="seal">
            <svg viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg">
                <circle cx="40" cy="40" r="38" fill="none" stroke="#000" stroke-width="2"/>
                <circle cx="40" cy="40" r="33" fill="none" stroke="#000" stroke-width="1"/>
                <circle cx="40" cy="40" r="28" fill="none" stroke="#000" stroke-width="0.5"/>
                <text x="40" y="25" text-anchor="middle" font-size="6" font-family="Times New Roman, serif" font-weight="bold">OFFICIAL</text>
                <text x="40" y="38" text-anchor="middle" font-size="8" font-family="Times New Roman, serif" font-weight="bold">UNIVERSITY</text>
                <text x="40" y="50" text-anchor="middle" font-size="8" font-family="Times New Roman, serif" font-weight="bold">SEAL</text>
                <text x="40" y="62" text-anchor="middle" font-size="5" font-family="Times New Roman, serif">ESTABLISHED</text>
                <path d="M 15 40 A 25 25 0 0 1 65 40" fill="none" stroke="#000" stroke-width="0.5"/>
                <path d="M 15 40 A 25 25 0 0 0 65 40" fill="none" stroke="#000" stroke-width="0.5"/>
            </svg>
        </div>
        <div class="university-info">
            <div class="university-name">{safe_school}</div>
            <div class="registrar-office">Office of the University Registrar</div>
            <div class="university-address">Academic Records Division | Student Services Building</div>
        </div>
    </header>

    <!-- Document Title -->
    <h1 class="document-title">Official Academic Transcript</h1>

    <!-- Student Information -->
    <section class="student-info">
        <div class="info-row">
            <span class="info-label">Student Name:</span>
            <span class="info-value">{safe_student}</span>
        </div>
        <div class="info-row">
            <span class="info-label">Student ID:</span>
            <span class="info-value">{safe_id}</span>
        </div>
        <div class="info-row">
            <span class="info-label">Degree Program:</span>
            <span class="info-value">{safe_major}</span>
        </div>
        <div class="info-row">
            <span class="info-label">Date Issued:</span>
            <span class="info-value">{issue_date}</span>
        </div>
        <div class="info-row">
            <span class="info-label">Classification:</span>
            <span class="info-value">{class_standing}</span>
        </div>
        <div class="info-row">
            <span class="info-label">Enrollment Status:</span>
            <span class="info-value">Currently Enrolled</span>
        </div>
    </section>

    <!-- Academic Record -->
    <section class="academic-record">
        <h2 class="section-title">Academic Record</h2>
        {semesters_html}
    </section>

    <!-- Cumulative Summary -->
    <section class="cumulative-summary">
        <div class="summary-title">Cumulative Academic Summary</div>
        <div class="summary-grid">
            <div class="summary-item">
                <span class="summary-label">Total Credits</span>
                <span class="summary-value">{total_credits:.1f}</span>
            </div>
            <div class="summary-item">
                <span class="summary-label">Cumulative GPA</span>
                <span class="summary-value">{cumulative_gpa:.2f}</span>
            </div>
            <div class="summary-item">
                <span class="summary-label">Terms Completed</span>
                <span class="summary-value">{num_semesters}</span>
            </div>
            <div class="summary-item">
                <span class="summary-label">Academic Standing</span>
                <span class="summary-value">Good</span>
            </div>
        </div>
    </section>

    <!-- Grading Scale Legend -->
    <div class="grading-legend">
        <div class="legend-title">Grading Scale:</div>
        <div class="legend-items">
            <span class="legend-item">A = 4.0</span>
            <span class="legend-item">A- = 3.7</span>
            <span class="legend-item">B+ = 3.3</span>
            <span class="legend-item">B = 3.0</span>
            <span class="legend-item">B- = 2.7</span>
            <span class="legend-item">C+ = 2.3</span>
            <span class="legend-item">C = 2.0</span>
            <span class="legend-item">C- = 1.7</span>
            <span class="legend-item">D+ = 1.3</span>
            <span class="legend-item">D = 1.0</span>
            <span class="legend-item">F = 0.0</span>
        </div>
    </div>

    <!-- Signature Block -->
    <section class="signature-block">
        <div class="signature-area">
            <div class="signature-line"></div>
            <div class="signature-label">University Registrar</div>
        </div>
        <div class="signature-area">
            <div class="signature-line"></div>
            <div class="signature-label">Date of Issue</div>
        </div>
        <div class="signature-area">
            <div class="signature-line"></div>
            <div class="signature-label">Official Seal</div>
        </div>
    </section>

    <!-- Document Footer -->
    <footer class="document-footer">
        <p class="footer-text">
            This transcript is official only when bearing the signature of the University Registrar and the embossed seal of the institution.
            Any alteration or erasure renders this document void.
        </p>
        <p class="page-number">Page 1 of 1</p>
    </footer>

    <!-- End of Transcript -->
    <p class="end-marker">*** End of Academic Record ***</p>

</body>
</html>
"""


def _generate_semesters_html(semesters: List[Dict[str, Any]]) -> str:
    """
    Generate HTML for all semester blocks.

    Args:
        semesters: List of semester dictionaries with courses

    Returns:
        HTML string for all semester sections
    """
    semesters_html = ""

    for sem in semesters:
        sem_name = html.escape(sem.get("semester_name", "Unknown Term"))
        courses = sem.get("courses", [])

        # Calculate term statistics
        term_credits = sum(float(c.get("credits", 0)) for c in courses)
        term_gpa = _calculate_term_gpa(courses)

        # Build course rows
        rows_html = ""
        for course in courses:
            code = html.escape(str(course.get("code", "")))
            title = html.escape(str(course.get("title", "")))
            credits = course.get("credits", "")
            grade = html.escape(str(course.get("grade", "")))

            # Format credits
            credits_str = f"{float(credits):.1f}" if credits else ""

            rows_html += f"""
                <tr>
                    <td class="course-code">{code}</td>
                    <td class="course-title">{title}</td>
                    <td class="course-credits">{credits_str}</td>
                    <td class="course-grade">{grade}</td>
                </tr>"""

        semesters_html += f"""
        <div class="semester-block">
            <div class="semester-header">{sem_name}</div>
            <table class="course-table">
                <thead>
                    <tr>
                        <th style="width: 15%;">Course</th>
                        <th style="width: 55%;">Course Title</th>
                        <th style="width: 15%;">Credits</th>
                        <th style="width: 15%;">Grade</th>
                    </tr>
                </thead>
                <tbody>
                    {rows_html}
                </tbody>
            </table>
            <div class="term-summary">
                <div class="term-stat">
                    <span class="term-stat-label">Term Credits:</span>
                    <span>{term_credits:.1f}</span>
                </div>
                <div class="term-stat">
                    <span class="term-stat-label">Term GPA:</span>
                    <span>{term_gpa:.2f}</span>
                </div>
            </div>
        </div>"""

    return semesters_html


def _calculate_term_gpa(courses: List[Dict[str, Any]]) -> float:
    """
    Calculate GPA for a single term.

    Args:
        courses: List of course dictionaries with grade and credits

    Returns:
        Term GPA as float
    """
    grade_points = {
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

    total_points = 0.0
    total_credits = 0.0

    for course in courses:
        grade = course.get("grade", "")
        credits = float(course.get("credits", 0))

        if grade in grade_points and credits > 0:
            total_points += grade_points[grade] * credits
            total_credits += credits

    if total_credits == 0:
        return 0.0

    return total_points / total_credits


def _get_class_standing(total_credits: int) -> str:
    """
    Determine class standing based on total credits.

    Args:
        total_credits: Total credits earned

    Returns:
        Class standing string
    """
    if total_credits < 30:
        return "Freshman"
    elif total_credits < 60:
        return "Sophomore"
    elif total_credits < 90:
        return "Junior"
    else:
        return "Senior"


if __name__ == "__main__":
    # Test data
    sample_semesters = [
        {
            "semester_name": "Fall 2023",
            "courses": [
                {
                    "code": "CS 101",
                    "title": "Introduction to Computer Science",
                    "credits": 4,
                    "grade": "A",
                },
                {"code": "MATH 151", "title": "Calculus I", "credits": 4, "grade": "A-"},
                {"code": "ENGL 101", "title": "College Composition", "credits": 3, "grade": "B+"},
                {"code": "HIST 110", "title": "World Civilizations", "credits": 3, "grade": "A"},
            ],
        },
        {
            "semester_name": "Spring 2024",
            "courses": [
                {
                    "code": "CS 201",
                    "title": "Data Structures and Algorithms",
                    "credits": 3,
                    "grade": "A-",
                },
                {"code": "MATH 152", "title": "Calculus II", "credits": 4, "grade": "B+"},
                {"code": "PHYS 101", "title": "General Physics I", "credits": 4, "grade": "A"},
                {"code": "COMM 100", "title": "Public Speaking", "credits": 3, "grade": "A"},
            ],
        },
        {
            "semester_name": "Fall 2024",
            "courses": [
                {
                    "code": "CS 251",
                    "title": "Algorithm Design and Analysis",
                    "credits": 3,
                    "grade": "A",
                },
                {"code": "CS 301", "title": "Operating Systems", "credits": 3, "grade": "B+"},
                {
                    "code": "STAT 201",
                    "title": "Probability and Statistics",
                    "credits": 3,
                    "grade": "A-",
                },
                {"code": "PHIL 200", "title": "Ethics in Technology", "credits": 3, "grade": "A"},
            ],
        },
    ]

    html_output = generate_transcript_html(
        school_name="University of California, Berkeley",
        student_name="Jane Marie Doe",
        student_id="30847592",
        major="Bachelor of Science in Computer Science",
        semesters=sample_semesters,
        cumulative_gpa=3.72,
        total_credits=47,
    )

    with open("test_official_transcript.html", "w", encoding="utf-8") as f:
        f.write(html_output)

    print("Generated test_official_transcript.html")
