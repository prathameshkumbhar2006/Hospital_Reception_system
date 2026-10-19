# ============================================================
# HOSPITAL RECEPTION SYSTEM
# FILE: patient/mobile.py
# PURPOSE: Mobile Number Entry and Patient Identification
# GUI: CustomTkinter + Pillow
# DATABASE: SQLite3
# OS: Ubuntu Linux
# ============================================================

import sqlite3
import logging
from tkinter import messagebox

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
    FONT_FAMILY,
    MOBILE_NUMBER_LENGTH
)

from database import fetch_one
from patient.keypad import NumericKeypad
from patient.welcome import render_marathi_text
from models.token_model import TokenModel


logger = logging.getLogger(__name__)


class MobileScreen(ctk.CTkFrame):

    # ========================================================
    # 1. INITIALIZATION
    # ========================================================

    def __init__(self, parent, app):

        super().__init__(
            parent,
            fg_color=BACKGROUND_COLOR,
            corner_radius=0
        )

        self.app = app
        self.is_processing = False

        self.marathi_images = []

        self.create_widgets()

    # ========================================================
    # 2. LANGUAGE HELPERS
    # ========================================================

    def is_marathi(self):

        return self.app.language == "मराठी"

    def text(self, english, marathi):

        return marathi if self.is_marathi() else english

    # ========================================================
    # 3. PILLOW MARATHI IMAGE
    # ========================================================

    def create_marathi_image(
        self,
        text,
        size=20,
        color=TEXT_COLOR,
        bold=False
    ):

        pil_image = render_marathi_text(
            text=text,
            size=size,
            color=color,
            bold=bold
        )

        image = ctk.CTkImage(
            light_image=pil_image,
            dark_image=pil_image,
            size=pil_image.size
        )

        self.marathi_images.append(image)

        return image

    # ========================================================
    # 4. CREATE LABEL
    # ========================================================

    def create_label(
        self,
        parent,
        english,
        marathi,
        size=18,
        bold=False,
        color=TEXT_COLOR
    ):

        if self.is_marathi():

            image = self.create_marathi_image(
                text=marathi,
                size=size,
                color=color,
                bold=bold
            )

            return ctk.CTkLabel(
                parent,
                text="",
                image=image,
                fg_color="transparent"
            )

        return ctk.CTkLabel(
            parent,
            text=english,
            font=ctk.CTkFont(
                family=FONT_FAMILY,
                size=size,
                weight="bold" if bold else "normal"
            ),
            text_color=color
        )

    # ========================================================
    # 5. CREATE BUTTON
    # ========================================================

    def create_button(
        self,
        parent,
        english,
        marathi,
        command,
        width=250,
        height=55,
        color=PRIMARY_COLOR,
        hover=PRIMARY_HOVER_COLOR,
        text_color="white",
        font_size=20
    ):

        if self.is_marathi():

            image = self.create_marathi_image(
                text=marathi,
                size=font_size,
                color=text_color,
                bold=True
            )

            return ctk.CTkButton(
                parent,
                text=" ",
                image=image,
                compound="left",
                width=width,
                height=height,
                fg_color=color,
                hover_color=hover,
                corner_radius=8,
                command=command
            )

        return ctk.CTkButton(
            parent,
            text=english,
            width=width,
            height=height,
            font=ctk.CTkFont(
                family=FONT_FAMILY,
                size=font_size,
                weight="bold"
            ),
            fg_color=color,
            hover_color=hover,
            text_color=text_color,
            corner_radius=8,
            command=command
        )

    # ========================================================
    # 6. CREATE SCREEN
    # ========================================================

    def create_widgets(self):

        self.container = ctk.CTkFrame(
            self,
            fg_color="transparent",
            corner_radius=0
        )

        self.container.pack(
            fill="both",
            expand=True,
            padx=25,
            pady=15
        )

        # ----------------------------------------------------
        # HEADER
        # ----------------------------------------------------

        header = ctk.CTkFrame(
            self.container,
            fg_color="transparent"
        )

        header.pack(
            fill="x",
            pady=(0, 10)
        )

        self.back_button = self.create_button(
            header,
            english="← Back",
            marathi="← मागे",
            command=self.go_back,
            width=125,
            height=45,
            color="#E5E7EB",
            hover="#D1D5DB",
            text_color=TEXT_COLOR,
            font_size=17
        )

        self.back_button.pack(side="left")

        self.header_title = self.create_label(
            header,
            english="Hospital Reception System",
            marathi="रुग्णालय नोंदणी प्रणाली",
            size=21,
            bold=True,
            color=PRIMARY_COLOR
        )

        self.header_title.pack(
            side="right",
            padx=10
        )

        # ----------------------------------------------------
        # MAIN CARD
        # ----------------------------------------------------

        self.card = ctk.CTkFrame(
            self.container,
            fg_color=CARD_COLOR,
            corner_radius=12,
            border_width=1,
            border_color=BORDER_COLOR
        )

        self.card.pack(
            expand=True,
            padx=15,
            pady=10
        )

        # ----------------------------------------------------
        # TITLE
        # ----------------------------------------------------

        self.title_label = self.create_label(
            self.card,
            english="Enter Mobile Number",
            marathi="मोबाईल नंबर प्रविष्ट करा",
            size=29,
            bold=True
        )

        self.title_label.pack(
            padx=40,
            pady=(22, 12)
        )

        # ----------------------------------------------------
        # MOBILE NUMBER INPUT
        # ----------------------------------------------------

        self.mobile_entry = ctk.CTkEntry(
            self.card,
            width=350,
            height=60,
            font=ctk.CTkFont(
                family=FONT_FAMILY,
                size=29,
                weight="bold"
            ),
            justify="center",
            placeholder_text="XXXXXXXXXX",
            border_color=BORDER_COLOR,
            border_width=2,
            corner_radius=8
        )

        self.mobile_entry.pack(
            padx=25,
            pady=(5, 10)
        )

        # Restore previous mobile number.
        previous_mobile = str(
            self.app.mobile_number or ""
        ).strip()

        if (
            previous_mobile.isascii()
            and previous_mobile.isdigit()
            and len(previous_mobile) <= MOBILE_NUMBER_LENGTH
        ):

            self.mobile_entry.insert(
                0,
                previous_mobile
            )

        # ----------------------------------------------------
        # VALIDATION MESSAGE
        # ----------------------------------------------------

        self.message_label = ctk.CTkLabel(
            self.card,
            text="",
            height=25,
            text_color=ERROR_COLOR
        )

        self.message_label.pack(
            padx=20,
            pady=(0, 5)
        )

        # ----------------------------------------------------
        # NUMERIC KEYPAD
        # ----------------------------------------------------

        self.keypad = NumericKeypad(
            self.card,
            self.mobile_entry,
            max_length=MOBILE_NUMBER_LENGTH
        )

        self.keypad.pack(
            padx=20,
            pady=5
        )

        # ----------------------------------------------------
        # CONTINUE BUTTON
        # ----------------------------------------------------

        self.continue_button = self.create_button(
            self.card,
            english="CONTINUE",
            marathi="पुढे जा",
            command=self.check_mobile,
            width=320,
            height=58,
            font_size=22
        )

        self.continue_button.pack(
            pady=(15, 10)
        )

        # ----------------------------------------------------
        # HELP TEXT
        # ----------------------------------------------------

        self.help_label = self.create_label(
            self.card,
            english=(
                "Enter your 10-digit mobile "
                "number to continue"
            ),
            marathi=(
                "पुढे जाण्यासाठी १० अंकी "
                "मोबाईल नंबर प्रविष्ट करा"
            ),
            size=15,
            color=MUTED_TEXT_COLOR
        )

        self.help_label.pack(
            padx=20,
            pady=(0, 18)
        )

        # ----------------------------------------------------
        # KEYBOARD SUPPORT
        # ----------------------------------------------------

        self.mobile_entry.bind(
            "<Return>",
            self.on_enter
        )

    # ========================================================
    # 7. PHYSICAL ENTER KEY
    # ========================================================

    def on_enter(self, event=None):

        self.check_mobile()

    # ========================================================
    # 8. BACK BUTTON
    # ========================================================

    def go_back(self):

        if self.is_processing:
            return

        self.app.show_welcome()

    # ========================================================
    # 9. DISPLAY ERROR MESSAGE
    # ========================================================

    def show_error(self, english, marathi=None):

        if not self.winfo_exists():
            return

        if self.is_marathi():

            message = marathi or english

            image = self.create_marathi_image(
                text=message,
                size=15,
                color=ERROR_COLOR
            )

            self.message_label.configure(
                text="",
                image=image
            )

        else:

            self.message_label.configure(
                text=english,
                image=None,
                text_color=ERROR_COLOR
            )

    # ========================================================
    # 10. CLEAR ERROR
    # ========================================================

    def clear_error(self):

        if self.winfo_exists():

            self.message_label.configure(
                text="",
                image=None
            )

    # ========================================================
    # 11. VALIDATE MOBILE NUMBER
    # ========================================================

    def validate_mobile(self, mobile):

        if not mobile:

            self.show_error(
                "Please enter your mobile number.",
                "कृपया मोबाईल नंबर प्रविष्ट करा."
            )

            return False

        if (
            len(mobile) != MOBILE_NUMBER_LENGTH
            or not mobile.isascii()
            or not mobile.isdigit()
        ):

            self.show_error(
                "Please enter a valid 10-digit mobile number.",
                "कृपया योग्य १० अंकी मोबाईल नंबर प्रविष्ट करा."
            )

            return False

        return True

    # ========================================================
    # 12. PROCESSING STATE
    # ========================================================

    def set_processing(self, processing):

        self.is_processing = processing

        if not self.winfo_exists():
            return

        if self.is_marathi():

            image = self.create_marathi_image(
                text=(
                    "कृपया थांबा..."
                    if processing
                    else "पुढे जा"
                ),
                size=20,
                color="white",
                bold=True
            )

            self.continue_button.configure(
                state=(
                    "disabled"
                    if processing
                    else "normal"
                ),
                image=image,
                text=" "
            )

        else:

            self.continue_button.configure(
                state=(
                    "disabled"
                    if processing
                    else "normal"
                ),
                text=(
                    "Please Wait..."
                    if processing
                    else "CONTINUE"
                )
            )

    # ========================================================
    # 13. CHECK MOBILE NUMBER
    # ========================================================

    def check_mobile(self):

        if self.is_processing:
            return

        mobile = self.mobile_entry.get().strip()

        self.clear_error()

        if not self.validate_mobile(mobile):
            return

        self.app.mobile_number = mobile

        self.set_processing(True)

        try:

            patient = fetch_one(
                """
                SELECT
                    id,
                    name,
                    mobile,
                    gender
                FROM patients
                WHERE mobile = ?
                LIMIT 1
                """,
                (mobile,)
            )

            if patient:

                self.existing_patient(patient)

            else:

                self.new_patient()

        except sqlite3.Error:

            logger.exception(
                "Patient mobile lookup failed"
            )

            self.show_error(
                "Database error. Please try again.",
                "डेटाबेसमध्ये त्रुटी आली."
            )

        except Exception:

            logger.exception(
                "Mobile screen processing failed"
            )

            self.show_error(
                "Unable to process your request.",
                "प्रक्रिया पूर्ण होऊ शकली नाही."
            )

        finally:

            if self.winfo_exists():

                self.set_processing(False)

    # ========================================================
    # 14. EXISTING PATIENT
    # ========================================================

    def existing_patient(self, patient):

        self.app.patient_id = patient["id"]
        self.app.patient_name = patient["name"]
        self.app.gender = patient["gender"] or ""
        self.app.token_number = ""

        # Standard Tkinter message boxes do not render Marathi
        # correctly on this Ubuntu system. Use English in dialogs
        # until a Pillow-based dialog is implemented.

        confirmation = messagebox.askyesno(
            "Existing Patient",
            (
                "This mobile number is already registered.\n\n"
                f"Patient: {patient['name']}\n\n"
                "Would you like to generate a token?"
            ),
            parent=self
        )

        if confirmation:

            self.generate_existing_token()

    # ========================================================
    # 15. NEW PATIENT
    # ========================================================

    def new_patient(self):

        self.app.patient_id = None
        self.app.patient_name = ""
        self.app.gender = ""
        self.app.token_number = ""

        self.app.show_register()

    # ========================================================
    # 16. GENERATE EXISTING PATIENT TOKEN
    # ========================================================

    def generate_existing_token(self):

        if not self.app.patient_id:

            self.show_error(
                "Patient information not found.",
                "रुग्णाची माहिती सापडली नाही."
            )

            return

        try:

            token = TokenModel.create_token(
                patient_id=self.app.patient_id
            )

            if not token:

                raise ValueError(
                    "Token could not be generated."
                )

            self.app.token_number = token["token_number"]

            print(
                "Patient token:",
                self.app.token_number
            )

            self.app.show_token()

        except Exception:

            logger.exception(
                "Existing patient token generation failed"
            )

            self.show_error(
                "Unable to generate token. Please try again.",
                "टोकन तयार करता आले नाही."
            )


# ============================================================
# END OF FILE
# ============================================================
