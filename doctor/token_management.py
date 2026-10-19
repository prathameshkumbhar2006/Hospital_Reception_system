# ============================================================
# HOSPITAL RECEPTION SYSTEM
# FILE: doctor/token_management.py
# PURPOSE: Patient Token Management
# ============================================================

import sqlite3
from datetime import date, datetime
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
    SUCCESS_COLOR,
    ERROR_COLOR
)

from database import fetch_all, execute_query


class TokenManagementScreen(ctk.CTkFrame):

    def __init__(self, parent, app):

        super().__init__(
            parent,
            fg_color=BACKGROUND_COLOR,
            corner_radius=0
        )

        self.app = app

        self.selected_visit_id = None
        self.selected_token = None

        self.filter_mode = "all"
        self.current_search = ""

        self.create_widgets()
        self.load_tokens()

    # ========================================================
    # CREATE INTERFACE
    # ========================================================

    def create_widgets(self):

        self.container = ctk.CTkFrame(
            self,
            fg_color=BACKGROUND_COLOR
        )

        self.container.pack(
            fill="both",
            expand=True,
            padx=20,
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
            pady=(0, 15)
        )

        ctk.CTkLabel(
            header,
            text="Token Management",
            font=("Arial", 27, "bold"),
            text_color=TEXT_COLOR
        ).pack(side="left")

        ctk.CTkButton(
            header,
            text="Refresh",
            width=110,
            height=40,
            fg_color=PRIMARY_COLOR,
            hover_color=PRIMARY_HOVER_COLOR,
            command=self.load_tokens
        ).pack(side="right")

        # ----------------------------------------------------
        # SEARCH
        # ----------------------------------------------------

        search_frame = ctk.CTkFrame(
            self.container,
            fg_color=CARD_COLOR,
            corner_radius=10,
            border_width=1,
            border_color=BORDER_COLOR
        )

        search_frame.pack(
            fill="x",
            pady=(0, 12)
        )

        ctk.CTkLabel(
            search_frame,
            text="Search Token / Patient",
            font=("Arial", 16, "bold"),
            text_color=TEXT_COLOR
        ).pack(
            anchor="w",
            padx=15,
            pady=(12, 5)
        )

        search_row = ctk.CTkFrame(
            search_frame,
            fg_color="transparent"
        )

        search_row.pack(
            fill="x",
            padx=15,
            pady=(0, 12)
        )

        self.search_entry = ctk.CTkEntry(
            search_row,
            height=42,
            placeholder_text=(
                "Search token, patient name or mobile"
            ),
            font=("Arial", 14)
        )

        self.search_entry.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(0, 10)
        )

        self.search_entry.bind(
            "<Return>",
            lambda event: self.search_token()
        )

        ctk.CTkButton(
            search_row,
            text="Search",
            width=100,
            height=42,
            command=self.search_token
        ).pack(
            side="left",
            padx=(0, 8)
        )

        ctk.CTkButton(
            search_row,
            text="Clear",
            width=90,
            height=42,
            fg_color="#E5E7EB",
            hover_color="#D1D5DB",
            text_color=TEXT_COLOR,
            command=self.clear_search
        ).pack(side="left")

        # ----------------------------------------------------
        # FILTERS
        # ----------------------------------------------------

        filter_frame = ctk.CTkFrame(
            self.container,
            fg_color=CARD_COLOR,
            corner_radius=10,
            border_width=1,
            border_color=BORDER_COLOR
        )

        filter_frame.pack(
            fill="x",
            pady=(0, 12)
        )

        filter_row = ctk.CTkFrame(
            filter_frame,
            fg_color="transparent"
        )

        filter_row.pack(
            fill="x",
            padx=15,
            pady=12
        )

        self.all_button = ctk.CTkButton(
            filter_row,
            text="All Tokens",
            width=115,
            height=38,
            command=self.show_all
        )

        self.all_button.pack(
            side="left",
            padx=(0, 8)
        )

        self.today_button = ctk.CTkButton(
            filter_row,
            text="Today's Tokens",
            width=125,
            height=38,
            command=self.show_today
        )

        self.today_button.pack(
            side="left",
            padx=(0, 15)
        )

        ctk.CTkLabel(
            filter_row,
            text="Date:",
            font=("Arial", 14),
            text_color=TEXT_COLOR
        ).pack(
            side="left",
            padx=(0, 8)
        )

        self.date_entry = ctk.CTkEntry(
            filter_row,
            width=145,
            height=38,
            placeholder_text="YYYY-MM-DD"
        )

        self.date_entry.pack(
            side="left",
            padx=(0, 8)
        )

        self.date_entry.bind(
            "<Return>",
            lambda event: self.apply_date_filter()
        )

        ctk.CTkButton(
            filter_row,
            text="Filter Date",
            width=105,
            height=38,
            command=self.apply_date_filter
        ).pack(side="left")

        self.filter_label = ctk.CTkLabel(
            filter_frame,
            text="Showing all consultation tokens",
            font=("Arial", 12),
            text_color=MUTED_TEXT_COLOR
        )

        self.filter_label.pack(
            anchor="w",
            padx=15,
            pady=(0, 10)
        )

        # ----------------------------------------------------
        # SUMMARY CARDS
        # ----------------------------------------------------

        summary = ctk.CTkFrame(
            self.container,
            fg_color="transparent"
        )

        summary.pack(
            fill="x",
            pady=(0, 12)
        )

        self.total_label = self.create_summary_card(
            summary,
            "Total Tokens",
            0
        )

        self.waiting_label = self.create_summary_card(
            summary,
            "Waiting",
            1
        )

        self.progress_label = self.create_summary_card(
            summary,
            "In Progress",
            2
        )

        self.completed_label = self.create_summary_card(
            summary,
            "Completed",
            3
        )

        # ----------------------------------------------------
        # TABLE
        # ----------------------------------------------------

        table_card = ctk.CTkFrame(
            self.container,
            fg_color=CARD_COLOR,
            corner_radius=10,
            border_width=1,
            border_color=BORDER_COLOR
        )

        table_card.pack(
            fill="both",
            expand=True
        )

        self.table_title = ctk.CTkLabel(
            table_card,
            text="All Patient Tokens",
            font=("Arial", 19, "bold"),
            text_color=TEXT_COLOR
        )

        self.table_title.pack(
            anchor="w",
            padx=15,
            pady=(15, 10)
        )

        self.table_frame = ctk.CTkScrollableFrame(
            table_card,
            fg_color="transparent"
        )

        self.table_frame.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=(0, 10)
        )

        # ----------------------------------------------------
        # ACTION BUTTONS
        # ----------------------------------------------------

        action_frame = ctk.CTkFrame(
            self.container,
            fg_color="transparent"
        )

        action_frame.pack(
            fill="x",
            pady=(15, 0)
        )

        self.selected_label = ctk.CTkLabel(
            action_frame,
            text="No token selected",
            font=("Arial", 13),
            text_color=MUTED_TEXT_COLOR
        )

        self.selected_label.pack(side="left")

        self.cancel_button = ctk.CTkButton(
            action_frame,
            text="Cancel Token",
            width=125,
            height=42,
            fg_color="#FEE2E2",
            hover_color="#FECACA",
            text_color=ERROR_COLOR,
            command=self.cancel_token
        )

        self.cancel_button.pack(
            side="right",
            padx=(8, 0)
        )

        self.details_button = ctk.CTkButton(
            action_frame,
            text="Patient Details",
            width=130,
            height=42,
            command=self.open_patient_details
        )

        self.details_button.pack(
            side="right",
            padx=(8, 0)
        )

        self.start_button = ctk.CTkButton(
            action_frame,
            text="Start Consultation",
            width=155,
            height=42,
            fg_color=SUCCESS_COLOR,
            hover_color="#15803D",
            command=self.start_consultation
        )

        self.start_button.pack(
            side="right",
            padx=(8, 0)
        )

        self.set_action_state(False)
        self.update_filter_buttons()

    # ========================================================
    # SUMMARY CARD
    # ========================================================

    def create_summary_card(
        self,
        parent,
        title,
        column
    ):

        parent.grid_columnconfigure(
            column,
            weight=1
        )

        card = ctk.CTkFrame(
            parent,
            fg_color=CARD_COLOR,
            corner_radius=8,
            border_width=1,
            border_color=BORDER_COLOR
        )

        card.grid(
            row=0,
            column=column,
            padx=5,
            sticky="ew"
        )

        ctk.CTkLabel(
            card,
            text=title,
            font=("Arial", 13),
            text_color=MUTED_TEXT_COLOR
        ).pack(
            pady=(12, 3)
        )

        value_label = ctk.CTkLabel(
            card,
            text="0",
            font=("Arial", 24, "bold"),
            text_color=PRIMARY_COLOR
        )

        value_label.pack(
            pady=(0, 12)
        )

        return value_label

    # ========================================================
    # DATE FILTER
    # ========================================================

    def get_filter_date(self):

        if self.filter_mode == "today":
            return date.today().isoformat()

        if self.filter_mode == "date":
            return self.date_entry.get().strip()

        return None

    def validate_date(self, value):

        try:
            datetime.strptime(
                value,
                "%Y-%m-%d"
            )

            return True

        except ValueError:
            return False

    # ========================================================
    # DATABASE - GET TOKENS
    # ========================================================

    def get_tokens(self, search=""):

        query = """
            SELECT
                v.id,
                v.patient_id,
                v.token_number,
                v.token_sequence,
                v.visit_date,
                v.visit_time,
                v.status,
                p.name AS patient_name,
                p.mobile,
                p.gender
            FROM visits v
            JOIN patients p
                ON p.id = v.patient_id
            WHERE 1 = 1
        """

        params = []

        selected_date = self.get_filter_date()

        if selected_date:

            query += """
                AND v.visit_date = ?
            """

            params.append(selected_date)

        if search:

            query += """
                AND (
                    UPPER(v.token_number) LIKE ?
                    OR UPPER(p.name) LIKE ?
                    OR p.mobile LIKE ?
                )
            """

            pattern = f"%{search}%"

            params.extend([
                pattern.upper(),
                pattern.upper(),
                pattern
            ])

        query += """
            ORDER BY
                v.visit_date DESC,
                v.token_sequence ASC,
                v.id ASC
        """

        return fetch_all(
            query,
            tuple(params)
        )

    # ========================================================
    # SUMMARY COUNTS
    # ========================================================

    def get_token_counts(self, tokens):

        counts = {
            "total": 0,
            "waiting": 0,
            "in_progress": 0,
            "completed": 0
        }

        for token in tokens:

            counts["total"] += 1

            status = token["status"]

            if status == "Waiting":
                counts["waiting"] += 1

            elif status == "In Progress":
                counts["in_progress"] += 1

            elif status == "Completed":
                counts["completed"] += 1

        return counts

    # ========================================================
    # LOAD TOKENS
    # ========================================================

    def load_tokens(self, search=None):

        try:

            if search is not None:
                self.current_search = search

            tokens = self.get_tokens(
                self.current_search
            )

            counts = self.get_token_counts(
                tokens
            )

            self.total_label.configure(
                text=str(counts["total"])
            )

            self.waiting_label.configure(
                text=str(counts["waiting"])
            )

            self.progress_label.configure(
                text=str(counts["in_progress"])
            )

            self.completed_label.configure(
                text=str(counts["completed"])
            )

            self.update_table_title()

            self.update_filter_buttons()

            self.display_tokens(tokens)

            self.clear_selection()

        except sqlite3.Error as error:

            messagebox.showerror(
                "Database Error",
                str(error),
                parent=self
            )

    # ========================================================
    # TABLE TITLE
    # ========================================================

    def update_table_title(self):

        if self.filter_mode == "today":

            self.table_title.configure(
                text="Today's Patient Tokens"
            )

            self.filter_label.configure(
                text=(
                    "Showing tokens for "
                    f"{date.today().isoformat()}"
                )
            )

        elif self.filter_mode == "date":

            selected_date = self.get_filter_date()

            self.table_title.configure(
                text=f"Patient Tokens - {selected_date}"
            )

            self.filter_label.configure(
                text=(
                    "Showing consultation tokens "
                    f"for {selected_date}"
                )
            )

        else:

            self.table_title.configure(
                text="All Patient Tokens"
            )

            self.filter_label.configure(
                text=(
                    "Showing all consultation "
                    "tokens from all dates"
                )
            )

    # ========================================================
    # UPDATE FILTER BUTTONS
    # ========================================================

    def update_filter_buttons(self):

        if self.filter_mode == "all":

            self.all_button.configure(
                fg_color=PRIMARY_COLOR,
                text_color="white"
            )

            self.today_button.configure(
                fg_color="#E5E7EB",
                hover_color="#D1D5DB",
                text_color=TEXT_COLOR
            )

        elif self.filter_mode == "today":

            self.all_button.configure(
                fg_color="#E5E7EB",
                hover_color="#D1D5DB",
                text_color=TEXT_COLOR
            )

            self.today_button.configure(
                fg_color=PRIMARY_COLOR,
                hover_color=PRIMARY_HOVER_COLOR,
                text_color="white"
            )

        else:

            self.all_button.configure(
                fg_color="#E5E7EB",
                hover_color="#D1D5DB",
                text_color=TEXT_COLOR
            )

            self.today_button.configure(
                fg_color="#E5E7EB",
                hover_color="#D1D5DB",
                text_color=TEXT_COLOR
            )

    # ========================================================
    # DISPLAY TOKENS
    # ========================================================

    def display_tokens(self, tokens):

        for widget in self.table_frame.winfo_children():
            widget.destroy()

        headers = [
            "Token",
            "Patient Name",
            "Mobile",
            "Date",
            "Time",
            "Status",
            "Action"
        ]

        for column, heading in enumerate(headers):

            self.table_frame.grid_columnconfigure(
                column,
                weight=1
            )

            ctk.CTkLabel(
                self.table_frame,
                text=heading,
                font=("Arial", 13, "bold"),
                text_color=TEXT_COLOR
            ).grid(
                row=0,
                column=column,
                padx=10,
                pady=10,
                sticky="w"
            )

        if not tokens:

            ctk.CTkLabel(
                self.table_frame,
                text="No consultation tokens found.",
                font=("Arial", 15),
                text_color=MUTED_TEXT_COLOR
            ).grid(
                row=1,
                column=0,
                columnspan=7,
                pady=30
            )

            return

        for row_index, token in enumerate(
            tokens,
            start=1
        ):

            status = token["status"]

            if status == "Completed":
                status_color = SUCCESS_COLOR

            elif status == "Waiting":
                status_color = PRIMARY_COLOR

            elif status == "Cancelled":
                status_color = ERROR_COLOR

            else:
                status_color = "#D97706"

            values = [
                token["token_number"],
                token["patient_name"],
                token["mobile"],
                token["visit_date"],
                token["visit_time"],
                status
            ]

            for column, value in enumerate(values):

                ctk.CTkLabel(
                    self.table_frame,
                    text=str(value or "-"),
                    font=("Arial", 13),
                    text_color=(
                        status_color
                        if column == 5
                        else TEXT_COLOR
                    ),
                    anchor="w"
                ).grid(
                    row=row_index,
                    column=column,
                    padx=10,
                    pady=9,
                    sticky="w"
                )

            ctk.CTkButton(
                self.table_frame,
                text="Select",
                width=75,
                height=32,
                command=(
                    lambda item=token:
                    self.select_token(item)
                )
            ).grid(
                row=row_index,
                column=6,
                padx=10,
                pady=7
            )

    # ========================================================
    # SELECT TOKEN
    # ========================================================

    def select_token(self, token):

        self.selected_visit_id = token["id"]
        self.selected_token = token

        self.selected_label.configure(
            text=(
                f"Selected: {token['token_number']} - "
                f"{token['patient_name']} "
                f"({token['visit_date']})"
            )
        )

        self.set_action_state(True)

        status = token["status"]

        is_today = (
            token["visit_date"]
            == date.today().isoformat()
        )

        # Historical consultations cannot be modified.

        if not is_today:

            self.start_button.configure(
                state="disabled"
            )

            self.cancel_button.configure(
                state="disabled"
            )

            return

        if status == "Waiting":

            self.start_button.configure(
                state="normal"
            )

            self.cancel_button.configure(
                state="normal"
            )

        elif status == "In Progress":

            self.start_button.configure(
                state="disabled"
            )

            self.cancel_button.configure(
                state="normal"
            )

        else:

            self.start_button.configure(
                state="disabled"
            )

            self.cancel_button.configure(
                state="disabled"
            )

    # ========================================================
    # ACTION STATES
    # ========================================================

    def set_action_state(self, enabled):

        state = (
            "normal"
            if enabled
            else "disabled"
        )

        self.start_button.configure(
            state=state
        )

        self.details_button.configure(
            state=state
        )

        self.cancel_button.configure(
            state=state
        )

    def clear_selection(self):

        self.selected_visit_id = None
        self.selected_token = None

        self.selected_label.configure(
            text="No token selected"
        )

        self.set_action_state(False)

    # ========================================================
    # SEARCH
    # ========================================================

    def search_token(self):

        search = self.search_entry.get().strip()

        self.load_tokens(search)

    def clear_search(self):

        self.search_entry.delete(
            0,
            "end"
        )

        self.current_search = ""

        self.load_tokens()

    # ========================================================
    # SHOW ALL
    # ========================================================

    def show_all(self):

        self.filter_mode = "all"

        self.date_entry.delete(
            0,
            "end"
        )

        self.search_entry.delete(
            0,
            "end"
        )

        self.current_search = ""

        self.load_tokens()

    # ========================================================
    # SHOW TODAY
    # ========================================================

    def show_today(self):

        self.filter_mode = "today"

        self.date_entry.delete(
            0,
            "end"
        )

        self.date_entry.insert(
            0,
            date.today().isoformat()
        )

        self.search_entry.delete(
            0,
            "end"
        )

        self.current_search = ""

        self.load_tokens()

    # ========================================================
    # APPLY DATE FILTER
    # ========================================================

    def apply_date_filter(self):

        selected_date = (
            self.date_entry.get().strip()
        )

        if not selected_date:

            messagebox.showwarning(
                "Date Required",
                "Please enter a date in YYYY-MM-DD format.",
                parent=self
            )

            return

        if not self.validate_date(selected_date):

            messagebox.showerror(
                "Invalid Date",
                "Please enter a valid date.\n\n"
                "Example: 2026-10-13",
                parent=self
            )

            return

        self.filter_mode = "date"

        self.load_tokens()

    # ========================================================
    # START CONSULTATION
    # ========================================================

    def start_consultation(self):

        if not self.selected_visit_id:
            return

        if not self.selected_token:
            return

        if (
            self.selected_token["visit_date"]
            != date.today().isoformat()
        ):

            messagebox.showwarning(
                "Historical Token",
                "Consultation can only be started "
                "for today's tokens.",
                parent=self
            )

            return

        visit_id = self.selected_visit_id

        try:

            updated = execute_query(
                """
                UPDATE visits
                SET
                    status = 'In Progress',
                    doctor_id = ?
                WHERE id = ?
                    AND visit_date = ?
                    AND status = 'Waiting'
                """,
                (
                    self.app.doctor_id,
                    visit_id,
                    date.today().isoformat()
                )
            )

            if updated == 0:

                messagebox.showwarning(
                    "Token Status",
                    "This token is no longer waiting.",
                    parent=self
                )

                self.load_tokens()

                return

            self.load_tokens()

            messagebox.showinfo(
                "Consultation",
                "Consultation started successfully.",
                parent=self
            )

            self.app.show_billing(
                visit_id=visit_id
            )

        except sqlite3.Error as error:

            messagebox.showerror(
                "Database Error",
                str(error),
                parent=self
            )

    # ========================================================
    # PATIENT DETAILS
    # ========================================================

    def open_patient_details(self):

        if not self.selected_visit_id:
            return

        visit_id = self.selected_visit_id

        try:

            from doctor.patient_details import (
                PatientDetailsScreen
            )

            self.app.show_page(
                "Token Management",
                PatientDetailsScreen,
                visit_id=visit_id
            )

        except ImportError:

            messagebox.showerror(
                "Error",
                "Patient details module is not available.",
                parent=self
            )

    # ========================================================
    # CANCEL TOKEN
    # ========================================================

    def cancel_token(self):

        if not self.selected_visit_id:
            return

        if not self.selected_token:
            return

        if (
            self.selected_token["visit_date"]
            != date.today().isoformat()
        ):

            messagebox.showwarning(
                "Historical Token",
                "Previous-day tokens cannot be cancelled.",
                parent=self
            )

            return

        confirm = messagebox.askyesno(
            "Cancel Token",
            "Are you sure you want to cancel this token?",
            parent=self
        )

        if not confirm:
            return

        try:

            updated = execute_query(
                """
                UPDATE visits
                SET status = 'Cancelled'
                WHERE id = ?
                    AND visit_date = ?
                    AND status IN (
                        'Waiting',
                        'In Progress'
                    )
                    AND NOT EXISTS (
                        SELECT 1
                        FROM bills
                        WHERE bills.visit_id = visits.id
                    )
                """,
                (
                    self.selected_visit_id,
                    date.today().isoformat()
                )
            )

            if updated:

                messagebox.showinfo(
                    "Success",
                    "Token cancelled successfully.",
                    parent=self
                )

            else:

                messagebox.showwarning(
                    "Cannot Cancel",
                    "This token cannot be cancelled.\n\n"
                    "It may already be completed, cancelled, "
                    "or associated with a bill.",
                    parent=self
                )

            self.load_tokens()

        except sqlite3.Error as error:

            messagebox.showerror(
                "Database Error",
                str(error),
                parent=self
            )


# ============================================================
# END OF FILE
# ============================================================
