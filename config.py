# ============================================================
# HOSPITAL RECEPTION SYSTEM
# FILE: config.py
# PURPOSE: Application Configuration and GUI Theme
# ============================================================

import os


# ============================================================
# 1. PROJECT PATHS
# ============================================================

# Main project directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# SQLite database file
DATABASE_PATH = os.path.join(BASE_DIR, "hospital.db")

# SQL schema file
SQL_FILE = os.path.join(BASE_DIR, "database.sql")

# Assets folder
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

# Images folder
IMAGES_DIR = os.path.join(ASSETS_DIR, "images")

# Hospital logo
LOGO_PATH = os.path.join(IMAGES_DIR, "logo.png")

# Generated files folder
GENERATED_DIR = os.path.join(BASE_DIR, "generated")

# Receipt storage
RECEIPTS_DIR = os.path.join(GENERATED_DIR, "receipts")

# Report storage
REPORTS_DIR = os.path.join(GENERATED_DIR, "reports")


# ============================================================
# 2. HOSPITAL INFORMATION
# ============================================================

HOSPITAL_NAME = "Hospital Reception System"

HOSPITAL_ADDRESS = "Hospital Address"

HOSPITAL_PHONE = ""

HOSPITAL_EMAIL = ""

RECEIPT_FOOTER = "Thank You! Get Well Soon."


# ============================================================
# 3. APPLICATION SETTINGS
# ============================================================

APP_NAME = "Hospital Reception System"

APP_VERSION = "1.0"

# Patient kiosk
PATIENT_WINDOW_TITLE = "Hospital - Patient Registration"

PATIENT_FULLSCREEN = True

# Doctor application
DOCTOR_WINDOW_TITLE = "Hospital - Doctor Dashboard"

DOCTOR_WINDOW_WIDTH = 1200

DOCTOR_WINDOW_HEIGHT = 750

# Return to welcome screen after token generation
PATIENT_RESET_SECONDS = 15

# Doctor dashboard refresh interval (milliseconds)
DASHBOARD_REFRESH_INTERVAL = 5000


# ============================================================
# 4. GUI THEME
# ============================================================

# CustomTkinter appearance
APPEARANCE_MODE = "light"

# Simple hospital theme
BACKGROUND_COLOR = "#F5F7FA"

CARD_COLOR = "#FFFFFF"

PRIMARY_COLOR = "#2563EB"

PRIMARY_HOVER_COLOR = "#1D4ED8"

SECONDARY_COLOR = "#E5E7EB"

TEXT_COLOR = "#1F2937"

MUTED_TEXT_COLOR = "#6B7280"

SUCCESS_COLOR = "#16A34A"

ERROR_COLOR = "#DC2626"

WARNING_COLOR = "#F59E0B"

BORDER_COLOR = "#D1D5DB"


# ============================================================
# 5. FONT SETTINGS
# ============================================================

# General font
FONT_FAMILY = "Arial"

# Marathi font supported on Ubuntu
MARATHI_FONT_FAMILY = "Noto Sans Devanagari"

TITLE_FONT_SIZE = 30

HEADING_FONT_SIZE = 24

SUBHEADING_FONT_SIZE = 18

NORMAL_FONT_SIZE = 15

SMALL_FONT_SIZE = 12

BUTTON_FONT_SIZE = 20

TOKEN_FONT_SIZE = 60


# ============================================================
# 6. BUTTON SETTINGS
# ============================================================

BUTTON_HEIGHT = 55

BUTTON_CORNER_RADIUS = 8

LARGE_BUTTON_HEIGHT = 85

LARGE_BUTTON_WIDTH = 250


# ============================================================
# 7. TOKEN SETTINGS
# ============================================================

TOKEN_PREFIX = "A"

TOKEN_DIGITS = 3

TOKEN_START_NUMBER = 1

# Example: A-001, A-002, A-003


# ============================================================
# 8. BILLING SETTINGS
# ============================================================

CURRENCY_SYMBOL = "₹"

DEFAULT_CONSULTATION_FEE = 0

DEFAULT_MEDICINE_FEE = 0

DEFAULT_OTHER_CHARGES = 0

PAYMENT_METHODS = [
    "Cash",
    "UPI",
    "Card"
]

PAYMENT_STATUSES = [
    "Paid",
    "Unpaid",
    "Partial"
]


# ============================================================
# 9. PATIENT SETTINGS
# ============================================================

MOBILE_NUMBER_LENGTH = 10

PATIENT_GENDERS = [
    "Male",
    "Female",
    "Other"
]

SUPPORTED_LANGUAGES = [
    "English",
    "मराठी"
]


# ============================================================
# 10. CREATE REQUIRED DIRECTORIES
# ============================================================

def create_directories():
    """
    Creates directories required for receipts and reports.
    """

    os.makedirs(RECEIPTS_DIR, exist_ok=True)

    os.makedirs(REPORTS_DIR, exist_ok=True)


# ============================================================
# 11. GET APPLICATION INFORMATION
# ============================================================

def get_app_info():
    """
    Returns basic application information.
    """

    return {
        "name": APP_NAME,
        "version": APP_VERSION,
        "database": DATABASE_PATH,
        "theme": APPEARANCE_MODE
    }


# ============================================================
# END OF CONFIGURATION
# ============================================================
