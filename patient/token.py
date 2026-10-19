# ============================================================
# HOSPITAL RECEPTION SYSTEM
# FILE: patient/token.py
# PURPOSE: Patient Token Display and Printing
# GUI: CustomTkinter + Pillow
# DATABASE: SQLite3
# OS: Ubuntu Linux
# ============================================================

import os
import shutil
import subprocess
import tempfile
import logging

from datetime import datetime
from tkinter import messagebox

import customtkinter as ctk

from config import (
    HOSPITAL_NAME,
    BACKGROUND_COLOR,
    CARD_COLOR,
    PRIMARY_COLOR,
    PRIMARY_HOVER_COLOR,
    TEXT_COLOR,
    MUTED_TEXT_COLOR,
    SUCCESS_COLOR,
    BORDER_COLOR,
    TOKEN_FONT_SIZE,
    FONT_FAMILY
)

from database import fetch_one
from patient.welcome import render_marathi_text


logger = logging.getLogger(__name__)


class TokenScreen(ctk.CTkFrame):

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

        self.token_number = app.token_number
        self.patient_id = app.patient_id

        self.marathi_images = []

        self.visit = self.get_visit_details()

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
    # 4. MULTILINGUAL LABEL
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
    # 5. MULTILINGUAL BUTTON
    # ========================================================

    def create_button(
        self,
        parent,
        english,
        marathi,
        command,
        width=220,
        height=60,
        color=PRIMARY_COLOR,
        hover=PRIMARY_HOVER_COLOR,
        font_size=19
    ):

        if self.is_marathi():

            image = self.create_marathi_image(
                text=marathi,
                size=font_size,
                color="white",
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
            text_color="white",
            corner_radius=8,
            command=command
        )

    # ========================================================
    # 6. GET VISIT DETAILS
    # ========================================================

    def get_visit_details(self):

        if not self.token_number or not self.patient_id:
            return None

        return fetch_one(
            """
            SELECT
                v.id,
                v.token_number,
                v.visit_date,
                v.visit_time,
                v.status,
                p.name AS patient_name
            FROM visits v
            JOIN patients p
                ON p.id = v.patient_id
            WHERE v.patient_id = ?
              AND v.token_number = ?
            ORDER BY v.id DESC
            LIMIT 1
            """,
            (
                self.patient_id,
                self.token_number
            )
        )

    # ========================================================
    # 7. CREATE GUI
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

        self.header = ctk.CTkFrame(
            self.container,
            fg_color="transparent"
        )

        self.header.pack(
            fill="x",
            pady=(5, 15)
        )

        self.hospital_label = ctk.CTkLabel(
            self.header,
            text="✚  " + HOSPITAL_NAME,
            font=ctk.CTkFont(
                family=FONT_FAMILY,
                size=23,
                weight="bold"
            ),
            text_color=PRIMARY_COLOR
        )

        self.hospital_label.pack(
            side="left",
            padx=10
        )

        # ----------------------------------------------------
        # TOKEN CARD
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
            padx=20,
            pady=10
        )

        # ----------------------------------------------------
        # SUCCESS SYMBOL
        # ----------------------------------------------------

        self.success_label = ctk.CTkLabel(
            self.card,
            text="✓",
            font=ctk.CTkFont(
                family=FONT_FAMILY,
                size=65,
                weight="bold"
            ),
            text_color=SUCCESS_COLOR
        )

        self.success_label.pack(
            pady=(25, 5)
        )

        # ----------------------------------------------------
        # SUCCESS MESSAGE
        # ----------------------------------------------------

        self.title_label = self.create_label(
            self.card,
            english="Token Generated Successfully",
            marathi="टोकन यशस्वीरित्या तयार झाले",
            size=28,
            bold=True
        )

        self.title_label.pack(
            padx=30,
            pady=(5, 15)
        )

        # ----------------------------------------------------
        # YOUR TOKEN HEADING
        # ----------------------------------------------------

        self.token_title = self.create_label(
            self.card,
            english="YOUR TOKEN NUMBER",
            marathi="तुमचा टोकन क्रमांक",
            size=22,
            bold=True,
            color=PRIMARY_COLOR
        )

        self.token_title.pack(
            pady=(5, 10)
        )

        # ----------------------------------------------------
        # TOKEN NUMBER BOX
        # ----------------------------------------------------

        self.token_box = ctk.CTkFrame(
            self.card,
            fg_color="#EFF6FF",
            corner_radius=10,
            border_width=2,
            border_color=PRIMARY_COLOR
        )

        self.token_box.pack(
            padx=45,
            pady=10
        )

        self.token_label = ctk.CTkLabel(
            self.token_box,
            text=self.token_number,
            font=ctk.CTkFont(
                family=FONT_FAMILY,
                size=TOKEN_FONT_SIZE,
                weight="bold"
            ),
            text_color=PRIMARY_COLOR
        )

        self.token_label.pack(
            padx=60,
            pady=20
        )

        # ----------------------------------------------------
        # DATE AND TIME
        # ----------------------------------------------------

        if self.visit:

            visit_date = self.visit["visit_date"]
            visit_time = self.visit["visit_time"]

        else:

            now = datetime.now()

            visit_date = now.strftime("%Y-%m-%d")
            visit_time = now.strftime("%H:%M:%S")

        self.date_value = visit_date
        self.time_value = visit_time

        self.date_label = self.create_label(
            self.card,
            english=f"Date: {visit_date}",
            marathi=f"दिनांक: {visit_date}",
            size=17,
            color=TEXT_COLOR
        )

        self.date_label.pack(
            pady=(10, 3)
        )

        self.time_label = self.create_label(
            self.card,
            english=f"Time: {visit_time}",
            marathi=f"वेळ: {visit_time}",
            size=17,
            color=TEXT_COLOR
        )

        self.time_label.pack(
            pady=(0, 15)
        )

        # ----------------------------------------------------
        # WAITING MESSAGE
        # ----------------------------------------------------

        self.waiting_label = self.create_label(
            self.card,
            english="Please wait for your turn to see the doctor.",
            marathi="कृपया डॉक्टरांना भेटण्यासाठी आपल्या क्रमांकाची प्रतीक्षा करा.",
            size=18,
            bold=True
        )

        self.waiting_label.pack(
            padx=25,
            pady=(5, 20)
        )

        # ----------------------------------------------------
        # BUTTON FRAME
        # ----------------------------------------------------

        self.button_frame = ctk.CTkFrame(
            self.card,
            fg_color="transparent"
        )

        self.button_frame.pack(
            pady=(5, 15),
            padx=20
        )

        # ----------------------------------------------------
        # PRINT BUTTON
        # ----------------------------------------------------

        self.print_button = self.create_button(
            self.button_frame,
            english="PRINT TOKEN",
            marathi="टोकन प्रिंट करा",
            command=self.print_token,
            width=220,
            height=60,
            color=PRIMARY_COLOR,
            hover=PRIMARY_HOVER_COLOR,
            font_size=19
        )

        self.print_button.grid(
            row=0,
            column=0,
            padx=10,
            pady=5
        )

        # ----------------------------------------------------
        # FINISH BUTTON
        # ----------------------------------------------------

        self.finish_button = self.create_button(
            self.button_frame,
            english="FINISH",
            marathi="पूर्ण करा",
            command=self.finish,
            width=220,
            height=60,
            color=SUCCESS_COLOR,
            hover="#15803D",
            font_size=19
        )

        self.finish_button.grid(
            row=0,
            column=1,
            padx=10,
            pady=5
        )

        # ----------------------------------------------------
        # THANK YOU MESSAGE
        # ----------------------------------------------------

        self.thank_you_label = self.create_label(
            self.card,
            english="Thank You!",
            marathi="धन्यवाद!",
            size=20,
            bold=True,
            color=SUCCESS_COLOR
        )

        self.thank_you_label.pack(
            pady=(10, 5)
        )

        # ----------------------------------------------------
        # FOOTER
        # ----------------------------------------------------

        self.footer_label = self.create_label(
            self.container,
            english="Patient Self-Registration & Token System",
            marathi="रुग्ण स्व-नोंदणी आणि टोकन प्रणाली",
            size=14,
            color=MUTED_TEXT_COLOR
        )

        self.footer_label.pack(
            side="bottom",
            pady=5
        )

    # ========================================================
    # 8. GENERATE PRINT CONTENT
    # ========================================================

    def get_token_print_content(self):

        return f"""
================================
          {HOSPITAL_NAME}
================================

          PATIENT TOKEN

================================

            {self.token_number}

================================

Date: {self.date_value}

Time: {self.time_value}

--------------------------------

Please wait for your turn.

Thank You!

================================
"""

    # ========================================================
    # 9. PRINT TOKEN
    # ========================================================

    def print_token(self):

        if shutil.which("lp") is None:

            messagebox.showerror(
                "Printing Error",
                (
                    "Printer service is not available.\n"
                    "Please install CUPS printing utilities."
                ),
                parent=self
            )

            return

        temporary_path = None

        try:

            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                suffix=".txt",
                prefix="hospital_token_",
                delete=False
            ) as file:

                file.write(
                    self.get_token_print_content()
                )

                temporary_path = file.name

            result = subprocess.run(
                ["lp", temporary_path],
                capture_output=True,
                text=True,
                timeout=15,
                check=False
            )

            if result.returncode != 0:

                raise RuntimeError(
                    result.stderr.strip()
                    or "Unable to send token to printer."
                )

            logger.info(
                "Token sent to printer: %s",
                self.token_number
            )

            self.finish()

        except (
            OSError,
            RuntimeError,
            subprocess.TimeoutExpired
        ) as error:

            logger.exception(
                "Token printing failed"
            )

            messagebox.showerror(
                "Printing Error",
                (
                    "Unable to print token.\n"
                    "Please check the printer.\n\n"
                    f"{error}"
                ),
                parent=self
            )

        finally:

            if temporary_path and os.path.exists(
                temporary_path
            ):

                try:
                    os.remove(temporary_path)

                except OSError:
                    pass

    # ========================================================
    # 10. FINISH
    # ========================================================

    def finish(self):

        self.app.reset_session()


# ============================================================
# END OF FILE
# ============================================================
