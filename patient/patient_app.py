# ============================================================
# HOSPITAL RECEPTION SYSTEM
# FILE: patient/patient_app.py
# PURPOSE: Main Patient Kiosk Application
# GUI: CustomTkinter
# DATABASE: SQLite3
# OS: Ubuntu Linux
# ============================================================

import logging
import tkinter as tk
from tkinter import messagebox

import customtkinter as ctk

from config import (
    PATIENT_WINDOW_TITLE,
    PATIENT_FULLSCREEN,
    PATIENT_RESET_SECONDS,
    BACKGROUND_COLOR,
    PRIMARY_COLOR,
    TEXT_COLOR,
    FONT_FAMILY,
    MARATHI_FONT_FAMILY
)

from patient.language import get_text


logger = logging.getLogger(__name__)


class PatientApp(ctk.CTk):

    # ========================================================
    # 1. INITIALIZE APPLICATION
    # ========================================================

    def __init__(self):

        super().__init__()

        self.title(PATIENT_WINDOW_TITLE)

        self.geometry("1100x750")
        self.minsize(850, 600)

        self.configure(
            fg_color=BACKGROUND_COLOR
        )

        # ----------------------------------------------------
        # FULLSCREEN SETTINGS
        # ----------------------------------------------------

        if PATIENT_FULLSCREEN:
            self.attributes("-fullscreen", True)

        self.bind(
            "<Escape>",
            self.exit_fullscreen
        )

        self.bind(
            "<F11>",
            self.toggle_fullscreen
        )

        # ----------------------------------------------------
        # PATIENT SESSION
        # ----------------------------------------------------

        self.language = "English"

        self.mobile_number = ""
        self.patient_id = None
        self.patient_name = ""
        self.gender = ""
        self.token_number = ""

        self.current_screen = None
        self.current_widget = None

        self.reset_timer = None

        # ----------------------------------------------------
        # MAIN CONTAINER
        # ----------------------------------------------------

        self.main_frame = ctk.CTkFrame(
            self,
            fg_color=BACKGROUND_COLOR,
            corner_radius=0
        )

        self.main_frame.pack(
            fill="both",
            expand=True
        )

        # ----------------------------------------------------
        # START WELCOME SCREEN
        # ----------------------------------------------------

        self.show_welcome()

    # ========================================================
    # 2. FULLSCREEN CONTROLS
    # ========================================================

    def exit_fullscreen(self, event=None):

        self.attributes(
            "-fullscreen",
            False
        )

    def toggle_fullscreen(self, event=None):

        fullscreen = bool(
            self.attributes("-fullscreen")
        )

        self.attributes(
            "-fullscreen",
            not fullscreen
        )

    # ========================================================
    # 3. CANCEL AUTOMATIC RESET
    # ========================================================

    def cancel_reset_timer(self):

        if self.reset_timer is None:
            return

        try:

            self.after_cancel(
                self.reset_timer
            )

        except (ValueError, tk.TclError):

            pass

        self.reset_timer = None

    # ========================================================
    # 4. CLEAR CURRENT SCREEN
    # ========================================================

    def clear_screen(self):

        for widget in self.main_frame.winfo_children():

            widget.destroy()

        self.current_widget = None
        self.current_screen = None

    # ========================================================
    # 5. SAFE SCREEN NAVIGATION
    # ========================================================

    def open_screen(self, screen_name, screen_class):
        """
        Build the next screen before destroying the current
        one.

        If a screen fails to load, the previous screen stays
        visible instead of leaving a blank application.
        """

        if not isinstance(
            screen_name,
            str
        ):
            raise ValueError(
                "Invalid screen name."
            )

        previous_screen = self.current_widget

        new_screen = None

        try:

            # Construct the new screen first.
            new_screen = screen_class(
                self.main_frame,
                self
            )

            # Ensure the new screen is a Tkinter widget.
            if not isinstance(
                new_screen,
                tk.Misc
            ):
                raise TypeError(
                    "Screen must be a Tkinter widget."
                )

            # Display new screen.
            new_screen.pack(
                fill="both",
                expand=True
            )

            # Only remove old widgets after successful creation.
            for widget in list(
                self.main_frame.winfo_children()
            ):

                if widget is not new_screen:

                    widget.destroy()

            self.current_widget = new_screen
            self.current_screen = screen_name

            return True

        except Exception as error:

            logger.exception(
                "Failed to open patient screen '%s'",
                screen_name
            )

            print(
                f"Patient screen error "
                f"({screen_name}): {error}"
            )

            # Remove the failed new screen if it exists.
            if (
                new_screen is not None
                and new_screen.winfo_exists()
            ):

                new_screen.destroy()

            # Preserve the previous screen.
            if (
                previous_screen is not None
                and previous_screen.winfo_exists()
            ):

                if not previous_screen.winfo_manager():

                    previous_screen.pack(
                        fill="both",
                        expand=True
                    )

            self.show_navigation_error(
                screen_name,
                error
            )

            return False

    # ========================================================
    # 6. NAVIGATION ERROR
    # ========================================================

    def show_navigation_error(self, screen_name, error):

        message = (
            "Unable to open the requested screen.\n\n"
            f"Screen: {screen_name}\n"
            f"Error: {error}\n\n"
            "Please check the terminal for details."
        )

        try:

            messagebox.showerror(
                "Hospital Reception System",
                message,
                parent=self
            )

        except tk.TclError:

            print(message)

    # ========================================================
    # 7. WELCOME SCREEN
    # ========================================================

    def show_welcome(self):

        from patient.welcome import WelcomeScreen

        if self.open_screen(
            "welcome",
            WelcomeScreen
        ):

            self.cancel_reset_timer()

    # ========================================================
    # 8. MOBILE NUMBER SCREEN
    # ========================================================

    def show_mobile(self):

        try:

            from patient.mobile import MobileScreen

        except Exception as error:

            logger.exception(
                "Unable to import MobileScreen"
            )

            self.show_navigation_error(
                "mobile",
                error
            )

            return

        if self.open_screen(
            "mobile",
            MobileScreen
        ):

            self.cancel_reset_timer()

    # ========================================================
    # 9. NEW PATIENT REGISTRATION
    # ========================================================

    def show_register(self):

        try:

            from patient.register import RegisterScreen

        except Exception as error:

            logger.exception(
                "Unable to import RegisterScreen"
            )

            self.show_navigation_error(
                "register",
                error
            )

            return

        if self.open_screen(
            "register",
            RegisterScreen
        ):

            self.cancel_reset_timer()

    # ========================================================
    # 10. GENERATED TOKEN SCREEN
    # ========================================================

    def show_token(self):

        try:

            from patient.token import TokenScreen

        except Exception as error:

            logger.exception(
                "Unable to import TokenScreen"
            )

            self.show_navigation_error(
                "token",
                error
            )

            return

        if self.open_screen(
            "token",
            TokenScreen
        ):

            self.cancel_reset_timer()

            # Automatically return to the Welcome Screen.
            self.reset_timer = self.after(
                int(PATIENT_RESET_SECONDS) * 1000,
                self.reset_session
            )

    # ========================================================
    # 11. SET PATIENT LANGUAGE
    # ========================================================

    def set_language(self, language):

        if language not in (
            "English",
            "मराठी"
        ):

            return

        previous_language = self.language

        self.language = language

        self.show_mobile()

        # Restore the previous language if navigation failed.
        if self.current_screen != "mobile":

            self.language = previous_language

    # ========================================================
    # 12. TRANSLATE TEXT
    # ========================================================

    def translate(self, key):

        return get_text(
            key,
            self.language
        )

    # ========================================================
    # 13. GET APPLICATION FONT
    # ========================================================

    def get_font(
        self,
        size=20,
        weight="normal"
    ):

        if self.language == "मराठी":

            font_family = MARATHI_FONT_FAMILY

        else:

            font_family = FONT_FAMILY

        return ctk.CTkFont(
            family=font_family,
            size=int(size),
            weight=weight
        )

    # ========================================================
    # 14. GET MARATHI FONT
    # ========================================================

    def get_marathi_font(
        self,
        size=20,
        weight="normal"
    ):

        return ctk.CTkFont(
            family=MARATHI_FONT_FAMILY,
            size=int(size),
            weight=weight
        )

    # ========================================================
    # 15. CREATE PAGE TITLE
    # ========================================================

    def create_title(
        self,
        parent,
        text
    ):

        title = ctk.CTkLabel(
            parent,
            text=text,
            font=self.get_font(
                size=32,
                weight="bold"
            ),
            text_color=TEXT_COLOR
        )

        title.pack(
            pady=(25, 15)
        )

        return title

    # ========================================================
    # 16. CREATE STANDARD BUTTON
    # ========================================================

    def create_button(
        self,
        parent,
        text,
        command,
        width=250,
        height=65,
        color=PRIMARY_COLOR
    ):

        button = ctk.CTkButton(
            parent,
            text=text,
            command=command,
            width=width,
            height=height,
            fg_color=color,
            hover_color="#1D4ED8",
            corner_radius=10,
            font=self.get_font(
                size=22,
                weight="bold"
            ),
            text_color="white"
        )

        return button

    # ========================================================
    # 17. RESET PATIENT SESSION
    # ========================================================

    def reset_session(self):

        self.cancel_reset_timer()

        # Return to Welcome Screen first.
        self.show_welcome()

        if self.current_screen != "welcome":
            return

        # Clear personal information after navigation succeeds.
        self.language = "English"

        self.mobile_number = ""
        self.patient_id = None
        self.patient_name = ""
        self.gender = ""
        self.token_number = ""

    # ========================================================
    # 18. CLOSE APPLICATION
    # ========================================================

    def destroy(self):

        self.cancel_reset_timer()

        super().destroy()


# ============================================================
# RUN PATIENT APPLICATION DIRECTLY
# ============================================================

if __name__ == "__main__":

    from config import create_directories
    from database import initialize_database

    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    create_directories()

    if initialize_database():

        app = PatientApp()
        app.mainloop()

    else:

        print(
            "Unable to initialize the hospital database."
        )
