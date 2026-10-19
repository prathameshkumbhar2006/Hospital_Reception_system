# ============================================================
# HOSPITAL RECEPTION SYSTEM
# FILE: doctor/doctor_app.py
# PURPOSE: Main Doctor Desktop Application
# OS: Ubuntu Linux
# GUI: CustomTkinter
# DATABASE: SQLite3
# ============================================================

import customtkinter as ctk

from config import (
    APP_NAME,
    DOCTOR_WINDOW_TITLE,
    DOCTOR_WINDOW_WIDTH,
    DOCTOR_WINDOW_HEIGHT,
    BACKGROUND_COLOR,
    CARD_COLOR,
    PRIMARY_COLOR,
    PRIMARY_HOVER_COLOR,
    TEXT_COLOR,
    MUTED_TEXT_COLOR,
    BORDER_COLOR,
    FONT_FAMILY
)


# ============================================================
# DOCTOR APPLICATION
# ============================================================

class DoctorApp(ctk.CTk):

    def __init__(self):

        super().__init__()

        # ----------------------------------------------------
        # 1. WINDOW CONFIGURATION
        # ----------------------------------------------------

        self.title(DOCTOR_WINDOW_TITLE)

        self.geometry(
            f"{DOCTOR_WINDOW_WIDTH}x{DOCTOR_WINDOW_HEIGHT}"
        )

        self.minsize(1000, 650)

        self.configure(
            fg_color=BACKGROUND_COLOR
        )

        # ----------------------------------------------------
        # 2. DOCTOR SESSION
        # ----------------------------------------------------

        self.doctor_id = None
        self.doctor_name = ""
        self.doctor_email = ""

        self.is_logged_in = False

        self.current_page = None

        # ----------------------------------------------------
        # 3. MAIN CONTAINER
        # ----------------------------------------------------

        self.main_container = ctk.CTkFrame(
            self,
            fg_color=BACKGROUND_COLOR,
            corner_radius=0
        )

        self.main_container.pack(
            fill="both",
            expand=True
        )

        # Application starts with login
        self.show_login()

    # ========================================================
    # 4. CLEAR WINDOW
    # ========================================================

    def clear_window(self):
        """
        Remove all widgets from the main window.
        """

        for widget in self.main_container.winfo_children():
            widget.destroy()

    # ========================================================
    # 5. SHOW LOGIN
    # ========================================================

    def show_login(self):
        """
        Display the doctor login screen.
        """

        self.clear_window()

        self.current_page = "login"

        from doctor.login import LoginScreen

        login_screen = LoginScreen(
            self.main_container,
            self
        )

        login_screen.pack(
            fill="both",
            expand=True
        )

    # ========================================================
    # 6. LOGIN SUCCESS
    # ========================================================

    def login_success(self, doctor):
        """
        Save doctor information after successful login.
        """

        self.doctor_id = doctor["id"]

        self.doctor_name = doctor["name"]

        self.doctor_email = doctor["email"]

        self.is_logged_in = True

        print(
            f"Doctor logged in: {self.doctor_name}"
        )

        self.show_dashboard()

    # ========================================================
    # 7. LOGOUT
    # ========================================================

    def logout(self):
        """
        Clear the doctor session and return to login.
        """

        self.doctor_id = None
        self.doctor_name = ""
        self.doctor_email = ""

        self.is_logged_in = False

        self.current_page = None

        self.show_login()

    # ========================================================
    # 8. CREATE MAIN LAYOUT
    # ========================================================

    def create_main_layout(self):
        """
        Create the sidebar and main content area.
        """

        self.clear_window()

        # ----------------------------------------------------
        # SIDEBAR
        # ----------------------------------------------------

        self.sidebar = ctk.CTkFrame(
            self.main_container,
            width=230,
            fg_color=CARD_COLOR,
            corner_radius=0,
            border_width=1,
            border_color=BORDER_COLOR
        )

        self.sidebar.pack(
            side="left",
            fill="y"
        )

        self.sidebar.pack_propagate(False)

        # ----------------------------------------------------
        # HOSPITAL TITLE
        # ----------------------------------------------------

        self.logo_label = ctk.CTkLabel(
            self.sidebar,
            text="✚  HOSPITAL",
            font=ctk.CTkFont(
                family=FONT_FAMILY,
                size=24,
                weight="bold"
            ),
            text_color=PRIMARY_COLOR
        )

        self.logo_label.pack(
            pady=(30, 5)
        )

        self.system_label = ctk.CTkLabel(
            self.sidebar,
            text="Reception System",
            font=ctk.CTkFont(
                family=FONT_FAMILY,
                size=14
            ),
            text_color=MUTED_TEXT_COLOR
        )

        self.system_label.pack(
            pady=(0, 25)
        )

        # ----------------------------------------------------
        # SIDEBAR NAVIGATION
        # ----------------------------------------------------

        self.nav_frame = ctk.CTkFrame(
            self.sidebar,
            fg_color="transparent"
        )

        self.nav_frame.pack(
            fill="x",
            padx=12
        )

        self.nav_buttons = {}

        navigation = [
            ("Dashboard", self.show_dashboard),
            ("Token Management", self.show_tokens),
            ("Patient Records", self.show_patients),
            ("Billing", self.show_billing),
            ("Receipts", self.show_receipts),
            ("Analytics", self.show_analytics),
            ("Reports", self.show_reports)
        ]

        for title, command in navigation:

            button = ctk.CTkButton(
                self.nav_frame,
                text=title,
                command=command,
                height=46,
                anchor="w",
                fg_color="transparent",
                hover_color="#EFF6FF",
                text_color=TEXT_COLOR,
                corner_radius=8,
                font=ctk.CTkFont(
                    family=FONT_FAMILY,
                    size=15
                )
            )

            button.pack(
                fill="x",
                pady=4
            )

            self.nav_buttons[title] = button

        # ----------------------------------------------------
        # SIDEBAR BOTTOM
        # ----------------------------------------------------

        self.bottom_frame = ctk.CTkFrame(
            self.sidebar,
            fg_color="transparent"
        )

        self.bottom_frame.pack(
            side="bottom",
            fill="x",
            padx=12,
            pady=20
        )

        self.doctor_label = ctk.CTkLabel(
            self.bottom_frame,
            text=self.doctor_name,
            font=ctk.CTkFont(
                family=FONT_FAMILY,
                size=14,
                weight="bold"
            ),
            text_color=TEXT_COLOR,
            wraplength=200
        )

        self.doctor_label.pack(
            pady=(0, 10)
        )

        self.logout_button = ctk.CTkButton(
            self.bottom_frame,
            text="Logout",
            command=self.logout,
            height=45,
            fg_color="#FEE2E2",
            hover_color="#FECACA",
            text_color="#DC2626",
            corner_radius=8,
            font=ctk.CTkFont(
                family=FONT_FAMILY,
                size=15,
                weight="bold"
            )
        )

        self.logout_button.pack(
            fill="x"
        )

        # ----------------------------------------------------
        # MAIN CONTENT AREA
        # ----------------------------------------------------

        self.content_area = ctk.CTkFrame(
            self.main_container,
            fg_color=BACKGROUND_COLOR,
            corner_radius=0
        )

        self.content_area.pack(
            side="right",
            fill="both",
            expand=True
        )

    # ========================================================
    # 9. CLEAR CONTENT AREA
    # ========================================================

    def clear_content(self):
        """
        Remove the previously opened page.
        """

        for widget in self.content_area.winfo_children():
            widget.destroy()

    # ========================================================
    # 10. HIGHLIGHT ACTIVE SIDEBAR BUTTON
    # ========================================================

    def highlight_navigation(self, page_name):

        for title, button in self.nav_buttons.items():

            if title == page_name:

                button.configure(
                    fg_color=PRIMARY_COLOR,
                    hover_color=PRIMARY_HOVER_COLOR,
                    text_color="white"
                )

            else:

                button.configure(
                    fg_color="transparent",
                    hover_color="#EFF6FF",
                    text_color=TEXT_COLOR
                )

    # ========================================================
    # 11. SHOW PAGE
    # ========================================================

    def show_page(self, page_name, screen_class, **kwargs):
        """
        Display a doctor module page.
        """

        if not self.is_logged_in:
            self.show_login()
            return

        # Create sidebar if not already displayed
        if not hasattr(self, "content_area"):
            self.create_main_layout()

        if not self.content_area.winfo_exists():
            self.create_main_layout()

        self.clear_content()

        self.current_page = page_name

        self.highlight_navigation(page_name)

        screen = screen_class(
            self.content_area,
            self,
            **kwargs
        )

        screen.pack(
            fill="both",
            expand=True
        )

    # ========================================================
    # 12. DASHBOARD
    # ========================================================

    def show_dashboard(self):

        if not self.is_logged_in:
            self.show_login()
            return

        from doctor.dashboard import DashboardScreen

        self.show_page(
            "Dashboard",
            DashboardScreen
        )

    # ========================================================
    # 13. TOKEN MANAGEMENT
    # ========================================================

    def show_tokens(self):

        if not self.is_logged_in:
            self.show_login()
            return

        from doctor.token_management import TokenManagementScreen

        self.show_page(
            "Token Management",
            TokenManagementScreen
        )

    # ========================================================
    # 14. PATIENT RECORDS
    # ========================================================

    def show_patients(self):

        if not self.is_logged_in:
            self.show_login()
            return

        from doctor.patient_records import PatientRecordsScreen

        self.show_page(
            "Patient Records",
            PatientRecordsScreen
        )

    # ========================================================
    # 15. BILLING
    # ========================================================

    def show_billing(self, visit_id=None):

        if not self.is_logged_in:
            self.show_login()
            return

        from doctor.billing import BillingScreen

        self.show_page(
            "Billing",
            BillingScreen,
            visit_id=visit_id
        )

    # ========================================================
    # 16. RECEIPTS
    # ========================================================

    def show_receipts(self):

        if not self.is_logged_in:
            self.show_login()
            return

        from doctor.receipts import ReceiptsScreen

        self.show_page(
            "Receipts",
            ReceiptsScreen
        )

    # ========================================================
    # 17. ANALYTICS
    # ========================================================

    def show_analytics(self):

        if not self.is_logged_in:
            self.show_login()
            return

        from doctor.analytics import AnalyticsScreen

        self.show_page(
            "Analytics",
            AnalyticsScreen
        )

    # ========================================================
    # 18. REPORTS
    # ========================================================

    def show_reports(self):

        if not self.is_logged_in:
            self.show_login()
            return

        from doctor.reports import ReportsScreen

        self.show_page(
            "Reports",
            ReportsScreen
        )


# ============================================================
# RUN DOCTOR APPLICATION DIRECTLY
# ============================================================

if __name__ == "__main__":

    from config import create_directories
    from database import initialize_database

    create_directories()

    if initialize_database():

        app = DoctorApp()

        app.mainloop()

    else:

        print("Unable to initialize the database.")
