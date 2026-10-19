# ============================================================
# HOSPITAL RECEPTION SYSTEM
# FILE: patient/welcome.py
# PURPOSE: Welcome Screen and Language Selection
# GUI: CustomTkinter + Pillow
# OS: Ubuntu Linux
# ============================================================

from datetime import datetime
from pathlib import Path
import tkinter as tk

import customtkinter as ctk
from PIL import Image, ImageDraw, ImageFont

from config import (
    HOSPITAL_NAME,
    BACKGROUND_COLOR,
    CARD_COLOR,
    PRIMARY_COLOR,
    PRIMARY_HOVER_COLOR,
    TEXT_COLOR,
    MUTED_TEXT_COLOR,
    FONT_FAMILY
)


# ============================================================
# MARATHI FONT CONFIGURATION
# ============================================================

FONT_DIRECTORY = Path(
    "/usr/share/fonts/truetype/noto"
)

MARATHI_FONT_REGULAR = (
    FONT_DIRECTORY / "NotoSansDevanagari-Regular.ttf"
)

MARATHI_FONT_BOLD = (
    FONT_DIRECTORY / "NotoSansDevanagari-Bold.ttf"
)


# ============================================================
# PILLOW MARATHI TEXT RENDERER
# ============================================================

def render_marathi_text(
    text,
    size=24,
    color=TEXT_COLOR,
    bold=False,
    padding=8
):
    """
    Render Marathi text using Pillow and RAQM.

    Returns a transparent PIL image suitable for use
    inside a CustomTkinter CTkImage.

    This avoids the Devanagari rendering problem
    encountered with Tkinter on Ubuntu.
    """

    font_path = (
        MARATHI_FONT_BOLD
        if bold and MARATHI_FONT_BOLD.exists()
        else MARATHI_FONT_REGULAR
    )

    if not font_path.exists():
        raise FileNotFoundError(
            "Marathi font not found:\n"
            f"{font_path}\n\n"
            "Install fonts-noto-core."
        )

    font = ImageFont.truetype(
        str(font_path),
        size
    )

    # Measure the actual rendered text.
    temporary_image = Image.new(
        "RGBA",
        (1, 1),
        (0, 0, 0, 0)
    )

    temporary_draw = ImageDraw.Draw(
        temporary_image
    )

    bbox = temporary_draw.textbbox(
        (0, 0),
        text,
        font=font,
        language="mr"
    )

    left, top, right, bottom = bbox

    width = max(
        1,
        right - left + padding * 2
    )

    height = max(
        1,
        bottom - top + padding * 2
    )

    image = Image.new(
        "RGBA",
        (width, height),
        (0, 0, 0, 0)
    )

    draw = ImageDraw.Draw(image)

    draw.text(
        (
            padding - left,
            padding - top
        ),
        text,
        font=font,
        fill=color,
        language="mr"
    )

    return image


# ============================================================
# WELCOME SCREEN
# ============================================================

class WelcomeScreen(ctk.CTkFrame):

    def __init__(self, parent, app):

        super().__init__(
            parent,
            fg_color=BACKGROUND_COLOR,
            corner_radius=0
        )

        self.app = app

        self.clock_job = None

        # Keep references to rendered images.
        self.marathi_images = []

        self.create_widgets()

        self.bind(
            "<Destroy>",
            self.on_destroy,
            add="+"
        )

    # ========================================================
    # 1. CREATE MARATHI IMAGE
    # ========================================================

    def create_marathi_image(
        self,
        text,
        size=24,
        color=TEXT_COLOR,
        bold=False
    ):

        image = render_marathi_text(
            text=text,
            size=size,
            color=color,
            bold=bold
        )

        ctk_image = ctk.CTkImage(
            light_image=image,
            dark_image=image,
            size=image.size
        )

        self.marathi_images.append(
            ctk_image
        )

        return ctk_image

    # ========================================================
    # 2. CREATE MARATHI LABEL
    # ========================================================

    def create_marathi_label(
        self,
        parent,
        text,
        size=24,
        color=TEXT_COLOR,
        bold=False
    ):

        image = self.create_marathi_image(
            text=text,
            size=size,
            color=color,
            bold=bold
        )

        return ctk.CTkLabel(
            parent,
            text="",
            image=image,
            fg_color="transparent",
            width=image.cget("size")[0],
            height=image.cget("size")[1]
        )

    # ========================================================
    # 3. CREATE SCREEN
    # ========================================================

    def create_widgets(self):

        # ----------------------------------------------------
        # MAIN CONTAINER
        # ----------------------------------------------------

        self.container = ctk.CTkFrame(
            self,
            fg_color="transparent",
            corner_radius=0
        )

        self.container.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=20
        )

        # ----------------------------------------------------
        # HEADER
        # ----------------------------------------------------

        self.header = ctk.CTkFrame(
            self.container,
            fg_color="transparent",
            height=65
        )

        self.header.pack(
            fill="x",
            pady=(5, 0)
        )

        self.hospital_label = ctk.CTkLabel(
            self.header,
            text="✚  " + HOSPITAL_NAME,
            font=ctk.CTkFont(
                family=FONT_FAMILY,
                size=25,
                weight="bold"
            ),
            text_color=PRIMARY_COLOR
        )

        self.hospital_label.pack(
            side="left",
            padx=10
        )

        self.datetime_label = ctk.CTkLabel(
            self.header,
            text="",
            font=ctk.CTkFont(
                family=FONT_FAMILY,
                size=15
            ),
            text_color=MUTED_TEXT_COLOR
        )

        self.datetime_label.pack(
            side="right",
            padx=10
        )

        # ----------------------------------------------------
        # CENTER FRAME
        # ----------------------------------------------------

        self.center_frame = ctk.CTkFrame(
            self.container,
            fg_color="transparent",
            corner_radius=0
        )

        self.center_frame.pack(
            fill="both",
            expand=True
        )

        # ----------------------------------------------------
        # WHITE CARD
        # ----------------------------------------------------

        self.content_frame = ctk.CTkFrame(
            self.center_frame,
            fg_color=CARD_COLOR,
            corner_radius=15,
            border_width=1,
            border_color="#E5E7EB"
        )

        self.content_frame.place(
            relx=0.5,
            rely=0.48,
            anchor="center",
            relwidth=0.82,
            relheight=0.78
        )

        # ----------------------------------------------------
        # HOSPITAL ICON
        # ----------------------------------------------------

        self.icon_label = ctk.CTkLabel(
            self.content_frame,
            text="✚",
            font=ctk.CTkFont(
                family=FONT_FAMILY,
                size=70,
                weight="bold"
            ),
            text_color=PRIMARY_COLOR
        )

        self.icon_label.pack(
            pady=(22, 5)
        )

        # ----------------------------------------------------
        # ENGLISH WELCOME HEADING
        # ----------------------------------------------------

        self.welcome_label = ctk.CTkLabel(
            self.content_frame,
            text="WELCOME TO OUR HOSPITAL",
            font=ctk.CTkFont(
                family=FONT_FAMILY,
                size=32,
                weight="bold"
            ),
            text_color=TEXT_COLOR
        )

        self.welcome_label.pack(
            pady=(5, 5)
        )

        # ----------------------------------------------------
        # MARATHI WELCOME HEADING
        # ----------------------------------------------------

        self.marathi_label = self.create_marathi_label(
            self.content_frame,
            text="आमच्या रुग्णालयात आपले स्वागत आहे",
            size=26,
            bold=True,
            color=TEXT_COLOR
        )

        self.marathi_label.pack(
            pady=(0, 22)
        )

        # ----------------------------------------------------
        # ENGLISH LANGUAGE HEADING
        # ----------------------------------------------------

        self.language_label = ctk.CTkLabel(
            self.content_frame,
            text="SELECT YOUR LANGUAGE",
            font=ctk.CTkFont(
                family=FONT_FAMILY,
                size=22,
                weight="bold"
            ),
            text_color=PRIMARY_COLOR
        )

        self.language_label.pack(
            pady=(5, 5)
        )

        # ----------------------------------------------------
        # MARATHI LANGUAGE HEADING
        # ----------------------------------------------------

        self.language_marathi_label = (
            self.create_marathi_label(
                self.content_frame,
                text="आपली भाषा निवडा",
                size=21,
                color=MUTED_TEXT_COLOR
            )
        )

        self.language_marathi_label.pack(
            pady=(0, 23)
        )

        # ----------------------------------------------------
        # LANGUAGE BUTTON FRAME
        # ----------------------------------------------------

        self.button_frame = ctk.CTkFrame(
            self.content_frame,
            fg_color="transparent"
        )

        self.button_frame.pack(
            pady=(0, 18)
        )

        # ----------------------------------------------------
        # ENGLISH BUTTON
        # ----------------------------------------------------

        self.english_button = ctk.CTkButton(
            self.button_frame,
            text="ENGLISH",
            width=240,
            height=80,
            font=ctk.CTkFont(
                family=FONT_FAMILY,
                size=24,
                weight="bold"
            ),
            fg_color=PRIMARY_COLOR,
            hover_color=PRIMARY_HOVER_COLOR,
            text_color="white",
            corner_radius=10,
            command=self.select_english
        )

        self.english_button.grid(
            row=0,
            column=0,
            padx=15,
            pady=10
        )

        # ----------------------------------------------------
        # MARATHI BUTTON IMAGE
        # ----------------------------------------------------

        self.marathi_button_image = (
            self.create_marathi_image(
                text="मराठी",
                size=26,
                color="#FFFFFF",
                bold=True
            )
        )

        # ----------------------------------------------------
        # MARATHI BUTTON
        # ----------------------------------------------------

        self.marathi_button = ctk.CTkButton(
            self.button_frame,
            text=" ",
            image=self.marathi_button_image,
            compound="left",
            width=240,
            height=80,
            fg_color=PRIMARY_COLOR,
            hover_color=PRIMARY_HOVER_COLOR,
            text_color="white",
            corner_radius=10,
            command=self.select_marathi
        )

        self.marathi_button.grid(
            row=0,
            column=1,
            padx=15,
            pady=10
        )

        # ----------------------------------------------------
        # HELP TEXT
        # ----------------------------------------------------

        self.help_label = ctk.CTkLabel(
            self.content_frame,
            text="Touch your preferred language to continue",
            font=ctk.CTkFont(
                family=FONT_FAMILY,
                size=16
            ),
            text_color=MUTED_TEXT_COLOR
        )

        self.help_label.pack(
            pady=(10, 5)
        )

        # ----------------------------------------------------
        # FOOTER
        # ----------------------------------------------------

        self.footer_label = ctk.CTkLabel(
            self.container,
            text="Patient Self-Registration & Token System",
            font=ctk.CTkFont(
                family=FONT_FAMILY,
                size=14
            ),
            text_color=MUTED_TEXT_COLOR
        )

        self.footer_label.pack(
            side="bottom",
            pady=5
        )

        # ----------------------------------------------------
        # START CLOCK
        # ----------------------------------------------------

        self.update_clock()

    # ========================================================
    # 4. SELECT ENGLISH
    # ========================================================

    def select_english(self):

        self.app.set_language(
            "English"
        )

    # ========================================================
    # 5. SELECT MARATHI
    # ========================================================

    def select_marathi(self):

        self.app.set_language(
            "मराठी"
        )

    # ========================================================
    # 6. UPDATE DATE AND TIME
    # ========================================================

    def update_clock(self):

        if not self.winfo_exists():
            return

        now = datetime.now()

        current_datetime = now.strftime(
            "%d %B %Y  |  %I:%M:%S %p"
        )

        self.datetime_label.configure(
            text=current_datetime
        )

        self.clock_job = self.after(
            1000,
            self.update_clock
        )

    # ========================================================
    # 7. CLEANUP
    # ========================================================

    def on_destroy(self, event):

        if event.widget != self:
            return

        if self.clock_job is not None:

            try:
                self.after_cancel(
                    self.clock_job
                )

            except (ValueError, tk.TclError):
                pass

            self.clock_job = None


# ============================================================
# END OF FILE
# ============================================================
