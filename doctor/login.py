# ============================================================
# HOSPITAL RECEPTION SYSTEM
# FILE: doctor/login.py
# PURPOSE: Doctor Login and Authentication
# DATABASE: SQLite3
# GUI: CustomTkinter
# OS: Ubuntu Linux
# ============================================================

import hashlib
import hmac
import secrets
import sqlite3

import customtkinter as ctk

from config import (
    BACKGROUND_COLOR,
    CARD_COLOR,
    PRIMARY_COLOR,
    PRIMARY_HOVER_COLOR,
    TEXT_COLOR,
    MUTED_TEXT_COLOR,
    BORDER_COLOR,
    ERROR_COLOR,
    SUCCESS_COLOR,
    FONT_FAMILY
)

from database import fetch_one, insert_record


# ============================================================
# 1. PASSWORD SECURITY
# ============================================================

def hash_password(password):
    """
    Create a secure password hash using PBKDF2-SHA256.
    """

    salt = secrets.token_hex(16)

    iterations = 600000

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        bytes.fromhex(salt),
        iterations
    ).hex()

    return f"pbkdf2_sha256${iterations}${salt}${password_hash}"


def verify_password(password, stored_hash):
    """
    Verify a password against the stored password hash.
    """

    try:

        algorithm, iterations, salt, expected_hash = (
            stored_hash.split("$")
        )

        if algorithm != "pbkdf2_sha256":
            return False

        calculated_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            bytes.fromhex(salt),
            int(iterations)
        ).hex()

        return hmac.compare_digest(
            calculated_hash,
            expected_hash
        )

    except (ValueError, TypeError):
        return False


# ============================================================
# 2. CREATE DOCTOR ACCOUNT
# ============================================================

def create_doctor(name, email, password):
    """
    Create a doctor account in SQLite.

    Password is stored securely as a hash.
    """

    name = name.strip()
    email = email.strip().lower()

    if not name:
        raise ValueError("Doctor name is required.")

    if not email or "@" not in email:
        raise ValueError("Valid email is required.")

    if len(password) < 8:
        raise ValueError(
            "Password must contain at least 8 characters."
        )

    existing_doctor = fetch_one(
        """
        SELECT id
        FROM doctors
        WHERE email = ?
        """,
        (email,)
    )

    if existing_doctor:
        raise ValueError(
            "A doctor account with this email already exists."
        )

    password_hash = hash_password(password)

    doctor_id = insert_record(
        """
        INSERT INTO doctors (
            name,
            email,
            password_hash,
            status
        )
        VALUES (?, ?, ?, 'Active')
        """,
        (
            name,
            email,
            password_hash
        )
    )

    return doctor_id


# ============================================================
# 3. DOCTOR LOGIN SCREEN
# ============================================================

class LoginScreen(ctk.CTkFrame):

    def __init__(self, parent, app):

        super().__init__(
            parent,
            fg_color=BACKGROUND_COLOR,
            corner_radius=0
        )

        self.app = app

        self.password_visible = False

        self.create_widgets()

    # ========================================================
    # 4. CREATE GUI
    # ========================================================

    def create_widgets(self):

        # ----------------------------------------------------
        # CENTER LOGIN CARD
        # ----------------------------------------------------

        self.login_card = ctk.CTkFrame(
            self,
            width=450,
            height=540,
            fg_color=CARD_COLOR,
            corner_radius=12,
            border_width=1,
            border_color=BORDER_COLOR
        )

        self.login_card.place(
            relx=0.5,
            rely=0.5,
            anchor="center"
        )

        self.login_card.pack_propagate(False)

        # ----------------------------------------------------
        # HOSPITAL ICON
        # ----------------------------------------------------

        self.icon_label = ctk.CTkLabel(
            self.login_card,
            text="✚",
            font=ctk.CTkFont(
                family=FONT_FAMILY,
                size=60,
                weight="bold"
            ),
            text_color=PRIMARY_COLOR
        )

        self.icon_label.pack(
            pady=(30, 5)
        )

        # ----------------------------------------------------
        # HEADING
        # ----------------------------------------------------

        self.title_label = ctk.CTkLabel(
            self.login_card,
            text="DOCTOR LOGIN",
            font=ctk.CTkFont(
                family=FONT_FAMILY,
                size=28,
                weight="bold"
            ),
            text_color=TEXT_COLOR
        )

        self.title_label.pack(
            pady=(5, 5)
        )

        self.subtitle_label = ctk.CTkLabel(
            self.login_card,
            text="Hospital Reception System",
            font=ctk.CTkFont(
                family=FONT_FAMILY,
                size=15
            ),
            text_color=MUTED_TEXT_COLOR
        )

        self.subtitle_label.pack(
            pady=(0, 30)
        )

        # ----------------------------------------------------
        # EMAIL LABEL
        # ----------------------------------------------------

        self.email_label = ctk.CTkLabel(
            self.login_card,
            text="Email Address",
            font=ctk.CTkFont(
                family=FONT_FAMILY,
                size=16,
                weight="bold"
            ),
            text_color=TEXT_COLOR
        )

        self.email_label.pack(
            anchor="w",
            padx=50,
            pady=(0, 5)
        )

        # Email field
        self.email_entry = ctk.CTkEntry(
            self.login_card,
            width=350,
            height=48,
            placeholder_text="Enter email address",
            font=ctk.CTkFont(
                family=FONT_FAMILY,
                size=15
            ),
            border_color=BORDER_COLOR,
            corner_radius=8
        )

        self.email_entry.pack(
            pady=(0, 20)
        )

        # ----------------------------------------------------
        # PASSWORD LABEL
        # ----------------------------------------------------

        self.password_label = ctk.CTkLabel(
            self.login_card,
            text="Password",
            font=ctk.CTkFont(
                family=FONT_FAMILY,
                size=16,
                weight="bold"
            ),
            text_color=TEXT_COLOR
        )

        self.password_label.pack(
            anchor="w",
            padx=50,
            pady=(0, 5)
        )

        # Password field
        self.password_entry = ctk.CTkEntry(
            self.login_card,
            width=350,
            height=48,
            placeholder_text="Enter password",
            show="●",
            font=ctk.CTkFont(
                family=FONT_FAMILY,
                size=15
            ),
            border_color=BORDER_COLOR,
            corner_radius=8
        )

        self.password_entry.pack(
            pady=(0, 10)
        )

        # ----------------------------------------------------
        # SHOW PASSWORD
        # ----------------------------------------------------

        self.show_password_checkbox = ctk.CTkCheckBox(
            self.login_card,
            text="Show Password",
            font=ctk.CTkFont(
                family=FONT_FAMILY,
                size=14
            ),
            text_color=TEXT_COLOR,
            fg_color=PRIMARY_COLOR,
            hover_color=PRIMARY_HOVER_COLOR,
            command=self.toggle_password
        )

        self.show_password_checkbox.pack(
            anchor="w",
            padx=50,
            pady=(0, 15)
        )

        # ----------------------------------------------------
        # ERROR MESSAGE
        # ----------------------------------------------------

        self.message_label = ctk.CTkLabel(
            self.login_card,
            text="",
            font=ctk.CTkFont(
                family=FONT_FAMILY,
                size=14
            ),
            text_color=ERROR_COLOR,
            wraplength=350,
            height=30
        )

        self.message_label.pack(
            pady=(0, 10)
        )

        # ----------------------------------------------------
        # LOGIN BUTTON
        # ----------------------------------------------------

        self.login_button = ctk.CTkButton(
            self.login_card,
            text="LOGIN",
            width=350,
            height=52,
            fg_color=PRIMARY_COLOR,
            hover_color=PRIMARY_HOVER_COLOR,
            font=ctk.CTkFont(
                family=FONT_FAMILY,
                size=18,
                weight="bold"
            ),
            corner_radius=8,
            command=self.login
        )

        self.login_button.pack(
            pady=(0, 15)
        )

        # ----------------------------------------------------
        # KEYBOARD SHORTCUT
        # ----------------------------------------------------

        self.email_entry.bind(
            "<Return>",
            lambda event: self.password_entry.focus_set()
        )

        self.password_entry.bind(
            "<Return>",
            lambda event: self.login()
        )

        # Focus on email field
        self.email_entry.focus_set()

    # ========================================================
    # 5. SHOW / HIDE PASSWORD
    # ========================================================

    def toggle_password(self):

        self.password_visible = (
            self.show_password_checkbox.get() == 1
        )

        if self.password_visible:

            self.password_entry.configure(
                show=""
            )

        else:

            self.password_entry.configure(
                show="●"
            )

    # ========================================================
    # 6. DISPLAY MESSAGE
    # ========================================================

    def show_message(self, message, success=False):

        self.message_label.configure(
            text=message,
            text_color=(
                SUCCESS_COLOR if success else ERROR_COLOR
            )
        )

    # ========================================================
    # 7. LOGIN VALIDATION
    # ========================================================

    def validate_login(self):

        email = self.email_entry.get().strip().lower()

        password = self.password_entry.get()

        if not email:

            self.show_message(
                "Please enter your email address."
            )

            return None

        if "@" not in email:

            self.show_message(
                "Please enter a valid email address."
            )

            return None

        if not password:

            self.show_message(
                "Please enter your password."
            )

            return None

        return email, password

    # ========================================================
    # 8. AUTHENTICATE DOCTOR
    # ========================================================

    def login(self):

        self.message_label.configure(text="")

        credentials = self.validate_login()

        if credentials is None:
            return

        email, password = credentials

        self.login_button.configure(
            state="disabled",
            text="Please Wait..."
        )

        self.update_idletasks()

        try:

            # -----------------------------------------------
            # SEARCH DOCTOR IN SQLITE
            # -----------------------------------------------

            doctor = fetch_one(
                """
                SELECT
                    id,
                    name,
                    email,
                    password_hash,
                    status

                FROM doctors

                WHERE email = ?
                """,
                (email,)
            )

            # -----------------------------------------------
            # INVALID EMAIL OR PASSWORD
            # -----------------------------------------------

            if not doctor:

                self.show_message(
                    "Invalid email or password."
                )

                return

            if not verify_password(
                password,
                doctor["password_hash"]
            ):

                self.show_message(
                    "Invalid email or password."
                )

                return

            # -----------------------------------------------
            # CHECK ACCOUNT STATUS
            # -----------------------------------------------

            if doctor["status"] != "Active":

                self.show_message(
                    "Your account is inactive. Contact the administrator."
                )

                return

            # -----------------------------------------------
            # LOGIN SUCCESS
            # -----------------------------------------------

            self.show_message(
                "Login successful.",
                success=True
            )

            doctor_data = {
                "id": doctor["id"],
                "name": doctor["name"],
                "email": doctor["email"]
            }

            self.app.login_success(doctor_data)

        except sqlite3.Error as error:

            print("Doctor login database error:", error)

            self.show_message(
                "Database error. Please try again."
            )

        finally:

            if self.winfo_exists():

                self.login_button.configure(
                    state="normal",
                    text="LOGIN"
                )


# ============================================================
# 9. CREATE DOCTOR ACCOUNT FROM TERMINAL
# ============================================================

if __name__ == "__main__":

    import getpass

    from database import initialize_database

    print("=" * 55)
    print("HOSPITAL RECEPTION SYSTEM")
    print("Create Doctor Account")
    print("=" * 55)

    if not initialize_database():

        print("Database initialization failed.")

        raise SystemExit(1)

    name = input("\nDoctor Name: ").strip()

    email = input("Doctor Email: ").strip()

    password = getpass.getpass("Password: ")

    confirm_password = getpass.getpass(
        "Confirm Password: "
    )

    if password != confirm_password:

        print("\nPasswords do not match.")

        raise SystemExit(1)

    try:

        doctor_id = create_doctor(
            name,
            email,
            password
        )

        print("\nDoctor account created successfully!")
        print(f"Doctor ID: {doctor_id}")
        print(f"Doctor Name: {name}")
        print(f"Doctor Email: {email}")

    except (ValueError, sqlite3.Error) as error:

        print(f"\nError: {error}")
