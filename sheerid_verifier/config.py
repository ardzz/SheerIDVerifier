"""Configuration constants for SheerID Verifier."""

# SheerID API Configuration
PROGRAM_ID = "67c8c14f5f17a83b745e3f82"
SHEERID_API_URL = "https://services.sheerid.com/rest/v2"

# Request timing (milliseconds)
MIN_DELAY_MS = 300
MAX_DELAY_MS = 800

# HTTP Client defaults
DEFAULT_TIMEOUT = 30
UPLOAD_TIMEOUT = 60

# Document generation
TRANSCRIPT_WIDTH = 850
TRANSCRIPT_HEIGHT = 1100
ID_CARD_WIDTH = 650
ID_CARD_HEIGHT = 400

# Stats file path (relative to package)
STATS_FILENAME = "stats.json"

# Verification steps
VALID_STEPS = ["collectStudentPersonalInfo", "docUpload", "sso"]

# Transcript Generation Configuration
TRANSCRIPT_MIN_SEMESTERS = 2
TRANSCRIPT_MAX_SEMESTERS = 5
TRANSCRIPT_MIN_COURSES_PER_SEMESTER = 4
TRANSCRIPT_MAX_COURSES_PER_SEMESTER = 6
DEFAULT_PERFORMANCE_PROFILE = "good"  # "excellent", "good", "average"

# HTML to Image Configuration (for Playwright)
TRANSCRIPT_VIEWPORT_WIDTH = 1200
TRANSCRIPT_VIEWPORT_HEIGHT = 900

# Render Backend Configuration
# Backend is auto-detected: tries Playwright first, falls back to Pillow
# Playwright produces high-quality HTML screenshots (requires `playwright` extra)
# Pillow produces simpler images but works without additional dependencies

# Document Caching Configuration
DOCUMENT_CACHE_DIR = "cache/documents"
DOCUMENT_CACHE_ENABLED = True
DOCUMENT_CACHE_MAX_AGE_DAYS = 7  # Auto-cleanup files older than this

# Polling Configuration (for pending verification status)
POLL_INTERVAL_SECONDS = 90  # Poll every 40 seconds
POLL_MAX_ATTEMPTS = 60  # Max ~40 minutes of polling (60 * 40s)

# Document Type Configuration
# Options: "transcript", "class_schedule", "id_card", "random"
# "random" will randomly select between class_schedule (50%), transcript (30%), id_card (20%)
DOCUMENT_TYPE = "random"
