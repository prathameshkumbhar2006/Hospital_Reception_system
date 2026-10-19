# ============================================================
# HOSPITAL RECEPTION SYSTEM
# FILE: main.py
# PURPOSE: Main Application Entry Point
# OS: Ubuntu Linux
# ============================================================

import sys
import customtkinter as ctk

from config import (
    APP_NAME,
    APP_VERSION,
    APPEARANCE_MODE,
    PRIMARY_COLOR,
    create_directories
)

from database import initialize_database, check_connection


# ============================================================
# 1. APPLICATION SETUP
# ============================================================

def setup_application():
    """
    Initialize the database and application settings.
    """

    print("=" * 55)
    print(APP_NAME)
    print(f"Version: {APP_VERSION}")
    print("=" * 55)

    # Create required directories
    create_directories()

    # Configure CustomTkinter
    ctk.set_appearance_mode(APPEARANCE_MODE)
    ctk.set_default_color_theme("blue")

    # Initialize SQLite database
    if not initialize_database():
        print("ERROR: Database initialization failed.")
        return False

    # Verify database connection
    if not check_connection():
        print("ERROR: Unable to connect to SQLite database.")
        return False

    print("Application setup completed successfully.")

    return True


# ============================================================
# 2. START PATIENT APPLICATION
# ============================================================

def start_patient():
    """
    Launch the patient touchscreen application.
    """

    try:
        from patient.patient_app import PatientApp

        print("\nStarting Patient Application...")

        app = PatientApp()
        app.mainloop()

    except ImportError as error:
        print(f"Patient application import error: {error}")
        print("Please complete patient/patient_app.py first.")

    except Exception as error:
        print(f"Patient application error: {error}")
        raise


# ============================================================
# 3. START DOCTOR APPLICATION
# ============================================================

def start_doctor():
    """
    Launch the doctor desktop application.
    """

    try:
        from doctor.doctor_app import DoctorApp

        print("\nStarting Doctor Application...")

        app = DoctorApp()
        app.mainloop()

    except ImportError as error:
        print(f"Doctor application import error: {error}")
        print("Please complete doctor/doctor_app.py first.")

    except Exception as error:
        print(f"Doctor application error: {error}")
        raise


# ============================================================
# 4. DISPLAY STARTUP MENU
# ============================================================

def show_menu():
    """
    Display a simple terminal menu to select the application.
    """

    print("\nSelect Application:")
    print("1. Patient Module")
    print("2. Doctor Module")
    print("3. Exit")

    while True:

        choice = input("\nEnter choice (1-3): ").strip()

        if choice == "1":
            start_patient()
            break

        elif choice == "2":
            start_doctor()
            break

        elif choice == "3":
            print("Application closed.")
            break

        else:
            print("Invalid choice. Please enter 1, 2, or 3.")


# ============================================================
# 5. MAIN FUNCTION
# ============================================================

def main():
    """
    Main function for launching the application.
    """

    # Initialize application
    if not setup_application():
        sys.exit(1)

    # Read command-line argument
    if len(sys.argv) > 1:

        mode = sys.argv[1].lower().strip()

        if mode == "patient":
            start_patient()

        elif mode == "doctor":
            start_doctor()

        else:
            print("\nInvalid application mode.")
            print("Available modes: patient, doctor")
            print("\nUsage:")
            print("python main.py patient")
            print("python main.py doctor")
            sys.exit(1)

    else:
        show_menu()


# ============================================================
# 6. APPLICATION ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()
