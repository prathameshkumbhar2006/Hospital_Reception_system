# ============================================================
# HOSPITAL RECEPTION SYSTEM
# FILE: doctor/patient_records.py
# PURPOSE: Patient Records, Search and Visit History
# DATABASE: SQLite3
# GUI: CustomTkinter
# ============================================================

import sqlite3
from tkinter import messagebox, TclError

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

from database import fetch_all, fetch_one


class PatientRecordsScreen(ctk.CTkFrame):

    def __init__(self, parent, app):
        super().__init__(
            parent,
            fg_color=BACKGROUND_COLOR,
            corner_radius=0
        )

        self.app = app
        self.selected_patient_id = None

        self.create_widgets()
        self.load_patients()

    # ========================================================
    # CREATE INTERFACE
    # ========================================================

    def create_widgets(self):

        self.container = ctk.CTkFrame(
            self,
            fg_color=BACKGROUND_COLOR,
            corner_radius=0
        )
        self.container.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=15
        )

        # Header
        header = ctk.CTkFrame(
            self.container,
            fg_color="transparent"
        )
        header.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(
            header,
            text="Patient Records",
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
            command=self.show_all
        ).pack(side="right")

        # Search card
        search_card = ctk.CTkFrame(
            self.container,
            fg_color=CARD_COLOR,
            corner_radius=10,
            border_width=1,
            border_color=BORDER_COLOR
        )
        search_card.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(
            search_card,
            text="Search Patients",
            font=("Arial", 17, "bold"),
            text_color=TEXT_COLOR
        ).pack(
            anchor="w",
            padx=15,
            pady=(12, 8)
        )

        search_row = ctk.CTkFrame(
            search_card,
            fg_color="transparent"
        )
        search_row.pack(
            fill="x",
            padx=15,
            pady=(0, 15)
        )

        self.search_entry = ctk.CTkEntry(
            search_row,
            height=43,
            placeholder_text="Search by patient ID, name or mobile number",
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
            lambda event: self.search_patients()
        )

        ctk.CTkButton(
            search_row,
            text="Search",
            width=100,
            height=43,
            command=self.search_patients
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            search_row,
            text="Show All",
            width=100,
            height=43,
            fg_color="#E5E7EB",
            hover_color="#D1D5DB",
            text_color=TEXT_COLOR,
            command=self.show_all
        ).pack(side="left")

        # Summary
        summary_card = ctk.CTkFrame(
            self.container,
            fg_color=CARD_COLOR,
            corner_radius=10,
            border_width=1,
            border_color=BORDER_COLOR
        )
        summary_card.pack(fill="x", pady=(0, 15))

        self.total_label = ctk.CTkLabel(
            summary_card,
            text="Total Registered Patients: 0",
            font=("Arial", 17, "bold"),
            text_color=PRIMARY_COLOR
        )
        self.total_label.pack(
            anchor="w",
            padx=20,
            pady=15
        )

        # Patient table
        table_card = ctk.CTkFrame(
            self.container,
            fg_color=CARD_COLOR,
            corner_radius=10,
            border_width=1,
            border_color=BORDER_COLOR
        )
        table_card.pack(
            fill="both",
            expand=True,
            pady=(0, 15)
        )

        ctk.CTkLabel(
            table_card,
            text="Registered Patients",
            font=("Arial", 19, "bold"),
            text_color=TEXT_COLOR
        ).pack(
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

        # Selected patient details
        details_card = ctk.CTkFrame(
            self.container,
            fg_color=CARD_COLOR,
            corner_radius=10,
            border_width=1,
            border_color=BORDER_COLOR
        )
        details_card.pack(fill="x")

        ctk.CTkLabel(
            details_card,
            text="Selected Patient",
            font=("Arial", 17, "bold"),
            text_color=TEXT_COLOR
        ).pack(
            anchor="w",
            padx=15,
            pady=(12, 5)
        )

        self.selected_label = ctk.CTkLabel(
            details_card,
            text="No patient selected",
            font=("Arial", 14),
            text_color=MUTED_TEXT_COLOR,
            anchor="w"
        )
        self.selected_label.pack(
            fill="x",
            padx=15,
            pady=(0, 10)
        )

        actions = ctk.CTkFrame(
            details_card,
            fg_color="transparent"
        )
        actions.pack(
            fill="x",
            padx=15,
            pady=(0, 15)
        )

        self.history_button = ctk.CTkButton(
            actions,
            text="View Visit History",
            width=160,
            height=43,
            fg_color=PRIMARY_COLOR,
            hover_color=PRIMARY_HOVER_COLOR,
            command=self.open_history
        )
        self.history_button.pack(
            side="left",
            padx=(0, 10)
        )

        self.history_button.configure(state="disabled")

    # ========================================================
    # DATABASE QUERIES
    # ========================================================

    def get_patients(self, search=""):

        query = """
            SELECT
                p.id,
                p.name,
                p.mobile,
                p.gender,
                p.created_at,
                COUNT(v.id) AS total_visits,
                MAX(v.visit_date) AS last_visit

            FROM patients p

            LEFT JOIN visits v
                ON v.patient_id = p.id
        """

        params = []

        if search:

            query += """
                WHERE
                    CAST(p.id AS TEXT) LIKE ?
                    OR p.name LIKE ?
                    OR p.mobile LIKE ?
            """

            pattern = f"%{search}%"
            params = [pattern, pattern, pattern]

        query += """
            GROUP BY
                p.id,
                p.name,
                p.mobile,
                p.gender,
                p.created_at

            ORDER BY p.id DESC
        """

        return fetch_all(query, tuple(params))

    def get_total_patients(self):

        result = fetch_one(
            "SELECT COUNT(*) AS total FROM patients"
        )

        return result["total"] if result else 0

    def get_patient_history(self, patient_id):

        return fetch_all(
            """
            SELECT
                v.id AS visit_id,
                v.token_number,
                v.visit_date,
                v.visit_time,
                v.status,
                d.name AS doctor_name,
                b.bill_number,
                b.total_amount,
                b.payment_status

            FROM visits v

            LEFT JOIN doctors d
                ON d.id = v.doctor_id

            LEFT JOIN bills b
                ON b.visit_id = v.id

            WHERE v.patient_id = ?

            ORDER BY
                v.visit_date DESC,
                v.id DESC
            """,
            (patient_id,)
        )

    # ========================================================
    # LOAD PATIENTS
    # ========================================================

    def load_patients(self, search=""):

        try:

            patients = self.get_patients(search)

            total = self.get_total_patients()

            self.total_label.configure(
                text=f"Total Registered Patients: {total}"
            )

            self.display_patients(patients)

            self.selected_patient_id = None

            self.selected_label.configure(
                text="No patient selected"
            )

            self.history_button.configure(
                state="disabled"
            )

        except sqlite3.Error as error:

            messagebox.showerror(
                "Database Error",
                str(error),
                parent=self
            )

    # ========================================================
    # DISPLAY PATIENTS
    # ========================================================

    def display_patients(self, patients):

        for widget in self.table_frame.winfo_children():
            widget.destroy()

        headers = [
            "Patient ID",
            "Name",
            "Mobile",
            "Gender",
            "Visits",
            "Last Visit",
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
                text_color=TEXT_COLOR,
                anchor="w"
            ).grid(
                row=0,
                column=column,
                padx=8,
                pady=10,
                sticky="w"
            )

        if not patients:

            ctk.CTkLabel(
                self.table_frame,
                text="No patient records found.",
                font=("Arial", 15),
                text_color=MUTED_TEXT_COLOR
            ).grid(
                row=1,
                column=0,
                columnspan=7,
                pady=30
            )

            return

        for row_index, patient in enumerate(
            patients,
            start=1
        ):

            values = [
                patient["id"],
                patient["name"],
                patient["mobile"],
                patient["gender"],
                patient["total_visits"],
                patient["last_visit"] or "-"
            ]

            for column, value in enumerate(values):

                ctk.CTkLabel(
                    self.table_frame,
                    text=str(value),
                    font=("Arial", 13),
                    text_color=TEXT_COLOR,
                    anchor="w"
                ).grid(
                    row=row_index,
                    column=column,
                    padx=8,
                    pady=8,
                    sticky="w"
                )

            ctk.CTkButton(
                self.table_frame,
                text="Select",
                width=75,
                height=32,
                command=lambda p=patient: self.select_patient(p)
            ).grid(
                row=row_index,
                column=6,
                padx=8,
                pady=6
            )

    # ========================================================
    # SEARCH
    # ========================================================

    def search_patients(self):

        search = self.search_entry.get().strip()

        self.load_patients(search)

    def show_all(self):

        self.search_entry.delete(0, "end")

        self.load_patients()

    # ========================================================
    # SELECT PATIENT
    # ========================================================

    def select_patient(self, patient):

        self.selected_patient_id = patient["id"]

        self.selected_label.configure(
            text=(
                f"ID: {patient['id']}   |   "
                f"Name: {patient['name']}   |   "
                f"Mobile: {patient['mobile']}"
            )
        )

        self.history_button.configure(
            state="normal"
        )

    # ========================================================
    # VISIT HISTORY WINDOW
    # ========================================================

    def open_history(self):

        if not self.selected_patient_id:
            return

        try:

            patient = fetch_one(
                """
                SELECT id, name, mobile, gender, created_at
                FROM patients
                WHERE id = ?
                """,
                (self.selected_patient_id,)
            )

            if not patient:

                messagebox.showwarning(
                    "Patient",
                    "Patient record not found.",
                    parent=self
                )

                return

            visits = self.get_patient_history(
                self.selected_patient_id
            )

        except sqlite3.Error as error:

            messagebox.showerror(
                "Database Error",
                str(error),
                parent=self
            )

            return

        window = ctk.CTkToplevel(self)

        window.title("Patient Visit History")

        window.geometry("950x650")

        window.minsize(750, 500)

        window.configure(
            fg_color=BACKGROUND_COLOR
        )

        window.transient(self.winfo_toplevel())

        # Header
        header = ctk.CTkFrame(
            window,
            fg_color=CARD_COLOR,
            corner_radius=10
        )
        header.pack(
            fill="x",
            padx=20,
            pady=(20, 15)
        )

        ctk.CTkLabel(
            header,
            text="Patient Visit History",
            font=("Arial", 23, "bold"),
            text_color=PRIMARY_COLOR
        ).pack(
            anchor="w",
            padx=20,
            pady=(15, 8)
        )

        ctk.CTkLabel(
            header,
            text=(
                f"Patient ID: {patient['id']}     "
                f"Name: {patient['name']}     "
                f"Mobile: {patient['mobile']}"
            ),
            font=("Arial", 14),
            text_color=TEXT_COLOR,
            anchor="w"
        ).pack(
            fill="x",
            padx=20,
            pady=(0, 15)
        )

        # History table
        table = ctk.CTkScrollableFrame(
            window,
            fg_color=CARD_COLOR,
            corner_radius=10
        )
        table.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=(0, 15)
        )

        headers = [
            "Date",
            "Token",
            "Time",
            "Doctor",
            "Status",
            "Bill",
            "Amount"
        ]

        for column, heading in enumerate(headers):

            table.grid_columnconfigure(
                column,
                weight=1
            )

            ctk.CTkLabel(
                table,
                text=heading,
                font=("Arial", 13, "bold"),
                text_color=TEXT_COLOR,
                anchor="w"
            ).grid(
                row=0,
                column=column,
                padx=8,
                pady=12,
                sticky="w"
            )

        if not visits:

            ctk.CTkLabel(
                table,
                text="No visit history available.",
                font=("Arial", 15),
                text_color=MUTED_TEXT_COLOR
            ).grid(
                row=1,
                column=0,
                columnspan=7,
                pady=30
            )

        for row_index, visit in enumerate(
            visits,
            start=1
        ):

            amount = (
                f"₹{float(visit['total_amount']):,.2f}"
                if visit["total_amount"] is not None
                else "-"
            )

            values = [
                visit["visit_date"],
                visit["token_number"],
                visit["visit_time"],
                visit["doctor_name"] or "-",
                visit["status"],
                visit["bill_number"] or "-",
                amount
            ]

            for column, value in enumerate(values):

                color = TEXT_COLOR

                if column == 4:

                    if value == "Completed":
                        color = SUCCESS_COLOR

                    elif value == "Cancelled":
                        color = ERROR_COLOR

                    elif value == "Waiting":
                        color = PRIMARY_COLOR

                ctk.CTkLabel(
                    table,
                    text=str(value),
                    font=("Arial", 12),
                    text_color=color,
                    anchor="w"
                ).grid(
                    row=row_index,
                    column=column,
                    padx=8,
                    pady=8,
                    sticky="w"
                )

        # Footer
        footer = ctk.CTkFrame(
            window,
            fg_color="transparent"
        )
        footer.pack(
            fill="x",
            padx=20,
            pady=(0, 20)
        )

        ctk.CTkLabel(
            footer,
            text=f"Total Visits: {len(visits)}",
            font=("Arial", 14, "bold"),
            text_color=TEXT_COLOR
        ).pack(side="left")

        ctk.CTkButton(
            footer,
            text="Close",
            width=120,
            height=40,
            command=window.destroy
        ).pack(side="right")

        # Ubuntu/Tk requires the dialog to be visible before setting a grab.
        # Schedule the grab after Tk has mapped and drawn the dialog.
        def activate_dialog():
            if not window.winfo_exists():
                return
            if window.winfo_viewable():
                try:
                    window.lift()
                    window.focus_force()
                    window.grab_set()
                except TclError:
                    pass
            else:
                window.after(100, activate_dialog)

        window.after(100, activate_dialog)


# ============================================================
# END OF FILE
# ============================================================
