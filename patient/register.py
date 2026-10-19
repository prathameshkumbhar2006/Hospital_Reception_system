# ============================================================
# HOSPITAL RECEPTION SYSTEM
# FILE: patient/register.py
# PURPOSE: New Patient Registration and Token Generation
# GUI: CustomTkinter + Pillow
# DATABASE: SQLite3
# OS: Ubuntu Linux
# ============================================================

import logging
import sqlite3
from datetime import datetime

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
    FONT_FAMILY,
    TOKEN_PREFIX,
    TOKEN_DIGITS
)

from database import get_connection
from patient.welcome import render_marathi_text


logger = logging.getLogger(__name__)


class RegisterScreen(ctk.CTkFrame):

    def __init__(self, parent, app):

        super().__init__(
            parent,
            fg_color=BACKGROUND_COLOR,
            corner_radius=0
        )

        self.app = app
        self.is_processing = False

        self.selected_gender = (
            app.gender
            if app.gender in ("Male", "Female", "Other")
            else None
        )

        self.gender_buttons = {}
        self.marathi_images = []

        self.create_widgets()

    # ========================================================
    # 1. LANGUAGE HELPERS
    # ========================================================

    def is_marathi(self):
        return self.app.language == "मराठी"

    def text(self, english, marathi):
        return marathi if self.is_marathi() else english

    # ========================================================
    # 2. PILLOW IMAGE RENDERING
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
    # 3. CREATE MULTILINGUAL LABEL
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
    # 4. CREATE MULTILINGUAL BUTTON
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
        font_size=19
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
    # 5. CREATE REGISTRATION SCREEN
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

        self.hospital_label = self.create_label(
            header,
            english="Hospital Reception System",
            marathi="रुग्णालय नोंदणी प्रणाली",
            size=21,
            bold=True,
            color=PRIMARY_COLOR
        )

        self.hospital_label.pack(
            side="right",
            padx=10
        )

        # ----------------------------------------------------
        # SCROLLABLE CONTENT
        # ----------------------------------------------------

        self.scroll_frame = ctk.CTkScrollableFrame(
            self.container,
            fg_color="transparent",
            corner_radius=0
        )

        self.scroll_frame.pack(
            fill="both",
            expand=True
        )

        # ----------------------------------------------------
        # REGISTRATION CARD
        # ----------------------------------------------------

        self.card = ctk.CTkFrame(
            self.scroll_frame,
            fg_color=CARD_COLOR,
            corner_radius=12,
            border_width=1,
            border_color=BORDER_COLOR
        )

        self.card.pack(
            padx=20,
            pady=10,
            ipadx=35,
            ipady=15
        )

        # ----------------------------------------------------
        # TITLE
        # ----------------------------------------------------

        self.title_label = self.create_label(
            self.card,
            english="New Patient Registration",
            marathi="नवीन रुग्ण नोंदणी",
            size=29,
            bold=True
        )

        self.title_label.pack(
            padx=20,
            pady=(15, 10)
        )

        # ----------------------------------------------------
        # INSTRUCTION
        # ----------------------------------------------------

        self.info_label = self.create_label(
            self.card,
            english=(
                "Enter patient details to generate a token"
            ),
            marathi=(
                "टोकन मिळवण्यासाठी रुग्णाची माहिती भरा"
            ),
            size=16,
            color=MUTED_TEXT_COLOR
        )

        self.info_label.pack(
            pady=(0, 18)
        )

        # ----------------------------------------------------
        # MOBILE NUMBER LABEL
        # ----------------------------------------------------

        self.mobile_label = self.create_label(
            self.card,
            english="Mobile Number",
            marathi="मोबाईल नंबर",
            size=18,
            bold=True
        )

        self.mobile_label.pack(
            pady=(5, 5)
        )

        # ----------------------------------------------------
        # MOBILE NUMBER FIELD
        # ----------------------------------------------------

        self.mobile_entry = ctk.CTkEntry(
            self.card,
            width=380,
            height=55,
            font=ctk.CTkFont(
                family=FONT_FAMILY,
                size=22
            ),
            justify="center",
            border_color=BORDER_COLOR
        )

        self.mobile_entry.pack(
            pady=(0, 20)
        )

        self.mobile_entry.insert(
            0,
            str(self.app.mobile_number)
        )

        self.mobile_entry.configure(
            state="disabled"
        )

        # ----------------------------------------------------
        # PATIENT NAME LABEL
        # ----------------------------------------------------

        self.name_label = self.create_label(
            self.card,
            english="Patient Full Name",
            marathi="रुग्णाचे पूर्ण नाव",
            size=18,
            bold=True
        )

        self.name_label.pack(
            pady=(5, 5)
        )

        # ----------------------------------------------------
        # PATIENT NAME INPUT
        # ----------------------------------------------------
        # Physical keyboard is used for entering the name.
        # Marathi placeholder is avoided because Tk cannot
        # render Devanagari correctly in an Entry widget.
        # ----------------------------------------------------

        self.name_entry = ctk.CTkEntry(
            self.card,
            width=380,
            height=55,
            font=ctk.CTkFont(
                family=FONT_FAMILY,
                size=20
            ),
            placeholder_text="Enter patient full name",
            border_color=BORDER_COLOR,
            corner_radius=8
        )

        self.name_entry.pack(
            pady=(0, 20)
        )

        if self.app.patient_name:

            self.name_entry.insert(
                0,
                self.app.patient_name
            )

        # ----------------------------------------------------
        # GENDER LABEL
        # ----------------------------------------------------

        self.gender_label = self.create_label(
            self.card,
            english="Select Gender",
            marathi="लिंग निवडा",
            size=20,
            bold=True
        )

        self.gender_label.pack(
            pady=(5, 15)
        )

        # ----------------------------------------------------
        # GENDER BUTTON FRAME
        # ----------------------------------------------------

        self.gender_frame = ctk.CTkFrame(
            self.card,
            fg_color="transparent"
        )

        self.gender_frame.pack(
            pady=(0, 20)
        )

        gender_options = [
            ("Male", "पुरुष"),
            ("Female", "महिला"),
            ("Other", "इतर")
        ]

        for column, (gender, marathi) in enumerate(
            gender_options
        ):

            button = self.create_button(
                self.gender_frame,
                english=gender,
                marathi=marathi,
                command=lambda g=gender: self.select_gender(g),
                width=125,
                height=65,
                color="#E5E7EB",
                hover="#D1D5DB",
                text_color=TEXT_COLOR,
                font_size=19
            )

            button.configure(
                border_width=1,
                border_color=BORDER_COLOR
            )

            button.grid(
                row=0,
                column=column,
                padx=7,
                pady=5
            )

            self.gender_buttons[gender] = button

        # ----------------------------------------------------
        # MESSAGE LABEL
        # ----------------------------------------------------

        self.message_label = ctk.CTkLabel(
            self.card,
            text="",
            font=ctk.CTkFont(
                family=FONT_FAMILY,
                size=15
            ),
            text_color=ERROR_COLOR,
            height=35
        )

        self.message_label.pack(
            padx=20,
            pady=(5, 10)
        )

        # ----------------------------------------------------
        # GENERATE TOKEN BUTTON
        # ----------------------------------------------------

        self.generate_button = self.create_button(
            self.card,
            english="REGISTER & GENERATE TOKEN",
            marathi="नोंदणी करा आणि टोकन मिळवा",
            command=self.register_patient,
            width=350,
            height=65,
            font_size=20
        )

        self.generate_button.pack(
            pady=(5, 20)
        )

        # ----------------------------------------------------
        # FOOTER
        # ----------------------------------------------------

        self.footer_label = self.create_label(
            self.container,
            english=(
                "Patient Self-Registration & Token System"
            ),
            marathi=(
                "रुग्ण स्व-नोंदणी आणि टोकन प्रणाली"
            ),
            size=14,
            color=MUTED_TEXT_COLOR
        )

        self.footer_label.pack(
            side="bottom",
            pady=5
        )

        # ----------------------------------------------------
        # RESTORE GENDER SELECTION
        # ----------------------------------------------------

        self.update_gender_buttons()

        self.name_entry.focus_set()

    # ========================================================
    # 6. GENDER SELECTION
    # ========================================================

    def select_gender(self, gender):

        if gender not in self.gender_buttons:
            return

        self.selected_gender = gender

        self.app.gender = gender

        self.update_gender_buttons()

        self.clear_message()

    # ========================================================
    # 7. UPDATE GENDER BUTTONS
    # ========================================================

    def update_gender_buttons(self):

        gender_translations = {
            "Male": "पुरुष",
            "Female": "महिला",
            "Other": "इतर"
        }

        for gender, button in self.gender_buttons.items():

            selected = gender == self.selected_gender

            bg_color = (
                PRIMARY_COLOR
                if selected
                else "#E5E7EB"
            )

            hover_color = (
                PRIMARY_HOVER_COLOR
                if selected
                else "#D1D5DB"
            )

            fg_color = (
                "white"
                if selected
                else TEXT_COLOR
            )

            button.configure(
                fg_color=bg_color,
                hover_color=hover_color,
                text_color=fg_color,
                border_color=(
                    PRIMARY_COLOR
                    if selected
                    else BORDER_COLOR
                )
            )

            if self.is_marathi():

                image = self.create_marathi_image(
                    text=gender_translations[gender],
                    size=19,
                    color=fg_color,
                    bold=True
                )

                button.configure(
                    text=" ",
                    image=image
                )

    # ========================================================
    # 8. SHOW VALIDATION MESSAGE
    # ========================================================

    def show_message(
        self,
        english,
        marathi=None,
        success=False
    ):

        if not self.winfo_exists():
            return

        color = (
            SUCCESS_COLOR
            if success
            else ERROR_COLOR
        )

        if self.is_marathi():

            image = self.create_marathi_image(
                text=marathi or english,
                size=15,
                color=color
            )

            self.message_label.configure(
                text="",
                image=image
            )

        else:

            self.message_label.configure(
                text=english,
                image=None,
                text_color=color
            )

    # ========================================================
    # 9. CLEAR MESSAGE
    # ========================================================

    def clear_message(self):

        if self.winfo_exists():

            self.message_label.configure(
                text="",
                image=None
            )

    # ========================================================
    # 10. VALIDATE PATIENT DETAILS
    # ========================================================

    def validate_details(self):

        name = " ".join(
            self.name_entry.get().strip().split()
        )

        mobile = str(
            self.app.mobile_number or ""
        ).strip()

        gender = self.selected_gender

        # ----------------------------------------------------
        # VALIDATE NAME
        # ----------------------------------------------------

        if not name:

            self.show_message(
                "Please enter the patient name.",
                "कृपया रुग्णाचे नाव प्रविष्ट करा."
            )

            return None

        if len(name) < 2 or len(name) > 150:

            self.show_message(
                "Patient name must contain 2 to 150 characters.",
                "रुग्णाचे नाव २ ते १५० अक्षरांमध्ये असावे."
            )

            return None

        if not any(
            character.isalpha()
            for character in name
        ):

            self.show_message(
                "Please enter a valid patient name.",
                "कृपया रुग्णाचे योग्य नाव प्रविष्ट करा."
            )

            return None

        if any(
            ord(character) < 32
            for character in name
        ):

            self.show_message(
                "Patient name contains invalid characters.",
                "रुग्णाच्या नावात चुकीची अक्षरे आहेत."
            )

            return None

        # ----------------------------------------------------
        # VALIDATE GENDER
        # ----------------------------------------------------

        if gender not in ("Male", "Female", "Other"):

            self.show_message(
                "Please select gender.",
                "कृपया लिंग निवडा."
            )

            return None

        # ----------------------------------------------------
        # VALIDATE MOBILE
        # ----------------------------------------------------

        if (
            len(mobile) != 10
            or not mobile.isascii()
            or not mobile.isdigit()
        ):

            self.show_message(
                "Invalid mobile number.",
                "मोबाईल नंबर चुकीचा आहे."
            )

            return None

        return {
            "name": name,
            "mobile": mobile,
            "gender": gender
        }

    # ========================================================
    # 11. UPDATE PROCESSING STATE
    # ========================================================

    def set_processing(self, processing):

        self.is_processing = processing

        if not self.winfo_exists():
            return

        if self.is_marathi():

            message = (
                "कृपया थांबा..."
                if processing
                else "नोंदणी करा आणि टोकन मिळवा"
            )

            image = self.create_marathi_image(
                text=message,
                size=20,
                color="white",
                bold=True
            )

            self.generate_button.configure(
                state=(
                    "disabled"
                    if processing
                    else "normal"
                ),
                text=" ",
                image=image
            )

        else:

            self.generate_button.configure(
                state=(
                    "disabled"
                    if processing
                    else "normal"
                ),
                text=(
                    "Please Wait..."
                    if processing
                    else "REGISTER & GENERATE TOKEN"
                )
            )

    # ========================================================
    # 12. REGISTER PATIENT
    # ========================================================

    def register_patient(self):

        if self.is_processing:
            return

        self.clear_message()

        details = self.validate_details()

        if details is None:
            return

        self.set_processing(True)

        connection = None

        try:

            connection = get_connection()

            connection.execute("BEGIN IMMEDIATE")

            # ------------------------------------------------
            # CHECK WHETHER PATIENT ALREADY EXISTS
            # ------------------------------------------------

            patient = connection.execute(
                """
                SELECT
                    id,
                    name,
                    gender
                FROM patients
                WHERE mobile = ?
                LIMIT 1
                """,
                (details["mobile"],)
            ).fetchone()

            if patient:

                patient_id = patient["id"]
                patient_name = patient["name"]
                patient_gender = patient["gender"]

            else:

                # --------------------------------------------
                # INSERT NEW PATIENT
                # --------------------------------------------

                cursor = connection.execute(
                    """
                    INSERT INTO patients (
                        name,
                        mobile,
                        gender
                    )
                    VALUES (?, ?, ?)
                    """,
                    (
                        details["name"],
                        details["mobile"],
                        details["gender"]
                    )
                )

                patient_id = cursor.lastrowid
                patient_name = details["name"]
                patient_gender = details["gender"]

            # ------------------------------------------------
            # CURRENT DATE AND TIME
            # ------------------------------------------------

            now = datetime.now()

            today = now.strftime("%Y-%m-%d")
            current_time = now.strftime("%H:%M:%S")

            # ------------------------------------------------
            # CHECK EXISTING ACTIVE TOKEN
            # ------------------------------------------------

            existing_token = connection.execute(
                """
                SELECT token_number
                FROM visits
                WHERE patient_id = ?
                  AND visit_date = ?
                  AND status IN (
                      'Waiting',
                      'In Progress'
                  )
                ORDER BY id DESC
                LIMIT 1
                """,
                (
                    patient_id,
                    today
                )
            ).fetchone()

            if existing_token:

                token_number = existing_token[
                    "token_number"
                ]

            else:

                # --------------------------------------------
                # INITIALIZE DAILY TOKEN COUNTER
                # --------------------------------------------

                connection.execute(
                    """
                    INSERT INTO daily_token_counters (
                        counter_date,
                        last_sequence
                    )
                    VALUES (?, 0)
                    ON CONFLICT(counter_date) DO NOTHING
                    """,
                    (today,)
                )

                # --------------------------------------------
                # INCREMENT DAILY COUNTER
                # --------------------------------------------

                connection.execute(
                    """
                    UPDATE daily_token_counters
                    SET last_sequence = last_sequence + 1
                    WHERE counter_date = ?
                    """,
                    (today,)
                )

                # --------------------------------------------
                # GET TOKEN SEQUENCE
                # --------------------------------------------

                counter = connection.execute(
                    """
                    SELECT last_sequence
                    FROM daily_token_counters
                    WHERE counter_date = ?
                    """,
                    (today,)
                ).fetchone()

                if counter is None:

                    raise RuntimeError(
                        "Unable to retrieve token sequence."
                    )

                sequence = counter["last_sequence"]

                # --------------------------------------------
                # GENERATE TOKEN NUMBER
                # --------------------------------------------

                token_number = (
                    f"{TOKEN_PREFIX}-"
                    f"{sequence:0{TOKEN_DIGITS}d}"
                )

                # --------------------------------------------
                # SAVE PATIENT VISIT
                # --------------------------------------------

                connection.execute(
                    """
                    INSERT INTO visits (
                        patient_id,
                        token_number,
                        token_sequence,
                        visit_date,
                        visit_time,
                        status
                    )
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        patient_id,
                        token_number,
                        sequence,
                        today,
                        current_time,
                        "Waiting"
                    )
                )

            # ------------------------------------------------
            # COMMIT PATIENT AND TOKEN TRANSACTION
            # ------------------------------------------------

            connection.commit()
            connection.close()
            connection = None

            # ------------------------------------------------
            # UPDATE APPLICATION SESSION
            # ------------------------------------------------

            self.app.patient_id = patient_id
            self.app.patient_name = patient_name
            self.app.mobile_number = details["mobile"]
            self.app.gender = patient_gender or details["gender"]
            self.app.token_number = token_number

            logger.info(
                "Patient registered: ID=%s, Token=%s",
                patient_id,
                token_number
            )

            # ------------------------------------------------
            # OPEN TOKEN SCREEN
            # ------------------------------------------------

            self.app.show_token()

        except Exception:

            if connection is not None:

                try:
                    connection.rollback()
                except sqlite3.Error:
                    pass

            logger.exception(
                "Patient registration or token generation failed"
            )

            self.show_message(
                "Unable to complete registration. Please try again.",
                "नोंदणी पूर्ण होऊ शकली नाही. पुन्हा प्रयत्न करा."
            )

        finally:

            if connection is not None:

                connection.close()

            if self.winfo_exists():

                self.set_processing(False)

    # ========================================================
    # 13. BACK BUTTON
    # ========================================================

    def go_back(self):

        if self.is_processing:
            return

        self.app.patient_name = (
            self.name_entry.get().strip()
        )

        self.app.gender = (
            self.selected_gender or ""
        )

        self.app.show_mobile()


# ============================================================
# END OF FILE
# ============================================================
