# ============================================================
# HOSPITAL RECEPTION SYSTEM
# FILE: doctor/patient_details.py
# PURPOSE: Patient Information and Visit Details
# DATABASE: SQLite3
# GUI: CustomTkinter
# ============================================================

import sqlite3
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

from database import fetch_one, fetch_all, execute_query


class PatientDetailsScreen(ctk.CTkFrame):

    def __init__(self, parent, app, visit_id=None):
        super().__init__(
            parent,
            fg_color=BACKGROUND_COLOR,
            corner_radius=0
        )

        self.app = app
        self.visit_id = visit_id
        self.patient = None

        self.create_widgets()

        if self.visit_id:
            self.load_patient_details()
        else:
            self.show_message(
                "No patient visit selected.",
                error=True
            )

    # ========================================================
    # CREATE INTERFACE
    # ========================================================

    def create_widgets(self):

        self.container = ctk.CTkScrollableFrame(
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
        header.pack(fill="x", pady=(0, 20))

        ctk.CTkButton(
            header,
            text="← Back",
            width=100,
            height=40,
            fg_color="#E5E7EB",
            hover_color="#D1D5DB",
            text_color=TEXT_COLOR,
            command=self.app.show_tokens
        ).pack(side="left", padx=(0, 15))

        ctk.CTkLabel(
            header,
            text="Patient Details",
            font=("Arial", 26, "bold"),
            text_color=TEXT_COLOR
        ).pack(side="left")

        ctk.CTkButton(
            header,
            text="Refresh",
            width=100,
            height=40,
            fg_color=PRIMARY_COLOR,
            hover_color=PRIMARY_HOVER_COLOR,
            command=self.load_patient_details
        ).pack(side="right")

        # Status message
        self.message_label = ctk.CTkLabel(
            self.container,
            text="",
            font=("Arial", 14),
            text_color=MUTED_TEXT_COLOR,
            wraplength=650
        )
        self.message_label.pack(fill="x", pady=(0, 10))

        # Patient information
        self.patient_card = self.create_card(
            "Patient Information"
        )

        self.patient_fields = {}

        fields = [
            ("Patient ID", "patient_id"),
            ("Full Name", "patient_name"),
            ("Mobile Number", "mobile"),
            ("Gender", "gender"),
            ("Registration Date", "created_at")
        ]

        for title, key in fields:
            self.patient_fields[key] = self.create_detail_row(
                self.patient_card,
                title
            )

        # Visit information
        self.visit_card = self.create_card(
            "Current Visit Information"
        )

        self.visit_fields = {}

        visit_fields = [
            ("Visit ID", "visit_id"),
            ("Token Number", "token_number"),
            ("Visit Date", "visit_date"),
            ("Visit Time", "visit_time"),
            ("Status", "status"),
            ("Doctor", "doctor_name"),
            ("Completed At", "completed_at")
        ]

        for title, key in visit_fields:
            self.visit_fields[key] = self.create_detail_row(
                self.visit_card,
                title
            )

        # Billing information
        self.billing_card = self.create_card(
            "Billing Information"
        )

        self.billing_fields = {}

        billing_fields = [
            ("Bill Number", "bill_number"),
            ("Consultation Fee", "consultation_fee"),
            ("Medicine Fee", "medicine_fee"),
            ("Other Charges", "other_charges"),
            ("Total Amount", "total_amount"),
            ("Amount Paid", "amount_paid"),
            ("Payment Status", "payment_status")
        ]

        for title, key in billing_fields:
            self.billing_fields[key] = self.create_detail_row(
                self.billing_card,
                title
            )

        # Actions
        action_frame = ctk.CTkFrame(
            self.container,
            fg_color="transparent"
        )
        action_frame.pack(fill="x", pady=(0, 20))

        self.start_button = ctk.CTkButton(
            action_frame,
            text="Start Consultation",
            width=170,
            height=45,
            fg_color=SUCCESS_COLOR,
            hover_color="#15803D",
            font=("Arial", 14, "bold"),
            command=self.start_consultation
        )
        self.start_button.pack(side="left", padx=(0, 10))

        self.billing_button = ctk.CTkButton(
            action_frame,
            text="Open Billing",
            width=150,
            height=45,
            fg_color=PRIMARY_COLOR,
            hover_color=PRIMARY_HOVER_COLOR,
            font=("Arial", 14, "bold"),
            command=self.open_billing
        )
        self.billing_button.pack(side="left", padx=(0, 10))

        self.records_button = ctk.CTkButton(
            action_frame,
            text="All Patient Records",
            width=170,
            height=45,
            fg_color="#E5E7EB",
            hover_color="#D1D5DB",
            text_color=TEXT_COLOR,
            command=self.app.show_patients
        )
        self.records_button.pack(side="left")

        # Visit history
        history_card = self.create_card(
            "Previous Visits"
        )

        self.history_frame = ctk.CTkFrame(
            history_card,
            fg_color="transparent"
        )
        self.history_frame.pack(
            fill="x",
            padx=15,
            pady=(5, 15)
        )

        self.start_button.configure(state="disabled")
        self.billing_button.configure(state="disabled")

    # ========================================================
    # CREATE CARD
    # ========================================================

    def create_card(self, title):

        card = ctk.CTkFrame(
            self.container,
            fg_color=CARD_COLOR,
            corner_radius=10,
            border_width=1,
            border_color=BORDER_COLOR
        )
        card.pack(
            fill="x",
            pady=(0, 15)
        )

        ctk.CTkLabel(
            card,
            text=title,
            font=("Arial", 19, "bold"),
            text_color=TEXT_COLOR
        ).pack(
            anchor="w",
            padx=20,
            pady=(15, 10)
        )

        return card

    # ========================================================
    # CREATE DETAIL ROW
    # ========================================================

    def create_detail_row(self, parent, title):

        row = ctk.CTkFrame(
            parent,
            fg_color="transparent"
        )
        row.pack(
            fill="x",
            padx=20,
            pady=5
        )

        ctk.CTkLabel(
            row,
            text=title,
            width=185,
            font=("Arial", 14),
            text_color=MUTED_TEXT_COLOR,
            anchor="w"
        ).pack(side="left")

        value_label = ctk.CTkLabel(
            row,
            text="-",
            font=("Arial", 14, "bold"),
            text_color=TEXT_COLOR,
            anchor="w"
        )
        value_label.pack(
            side="left",
            fill="x",
            expand=True
        )

        return value_label

    # ========================================================
    # MESSAGES
    # ========================================================

    def show_message(self, text, error=False):

        self.message_label.configure(
            text=text,
            text_color=ERROR_COLOR if error else SUCCESS_COLOR
        )

    # ========================================================
    # DATABASE: GET PATIENT VISIT
    # ========================================================

    def get_patient_visit(self):

        return fetch_one(
            """
            SELECT
                v.id AS visit_id,
                v.patient_id,
                v.token_number,
                v.visit_date,
                v.visit_time,
                v.status,
                v.completed_at,

                p.name AS patient_name,
                p.mobile,
                p.gender,
                p.created_at,

                d.name AS doctor_name,

                b.id AS bill_id,
                b.bill_number,
                b.consultation_fee,
                b.medicine_fee,
                b.other_charges,
                b.total_amount,
                b.payment_status,

                COALESCE(
                    (
                        SELECT SUM(pay.amount)
                        FROM payments pay
                        WHERE pay.bill_id = b.id
                    ),
                    0
                ) AS amount_paid

            FROM visits v

            JOIN patients p
                ON p.id = v.patient_id

            LEFT JOIN doctors d
                ON d.id = v.doctor_id

            LEFT JOIN bills b
                ON b.visit_id = v.id

            WHERE v.id = ?

            LIMIT 1
            """,
            (self.visit_id,)
        )

    # ========================================================
    # LOAD PATIENT DETAILS
    # ========================================================

    def load_patient_details(self):

        if not self.visit_id:
            return

        try:
            self.patient = self.get_patient_visit()

            if not self.patient:
                self.show_message(
                    "Patient visit not found.",
                    error=True
                )
                self.start_button.configure(state="disabled")
                self.billing_button.configure(state="disabled")
                return

            patient = self.patient

            # Patient information
            patient_values = {
                "patient_id": patient["patient_id"],
                "patient_name": patient["patient_name"],
                "mobile": patient["mobile"],
                "gender": patient["gender"],
                "created_at": patient["created_at"]
            }

            for key, value in patient_values.items():
                self.patient_fields[key].configure(
                    text=str(value) if value is not None else "-"
                )

            # Visit information
            visit_values = {
                "visit_id": patient["visit_id"],
                "token_number": patient["token_number"],
                "visit_date": patient["visit_date"],
                "visit_time": patient["visit_time"],
                "status": patient["status"],
                "doctor_name": patient["doctor_name"] or "Not Assigned",
                "completed_at": patient["completed_at"] or "-"
            }

            for key, value in visit_values.items():
                self.visit_fields[key].configure(
                    text=str(value)
                )

            status_color = {
                "Waiting": PRIMARY_COLOR,
                "In Progress": "#D97706",
                "Completed": SUCCESS_COLOR,
                "Cancelled": ERROR_COLOR
            }.get(patient["status"], TEXT_COLOR)

            self.visit_fields["status"].configure(
                text_color=status_color
            )

            # Billing information
            if patient["bill_id"]:

                billing_values = {
                    "bill_number": patient["bill_number"],
                    "consultation_fee": self.format_amount(
                        patient["consultation_fee"]
                    ),
                    "medicine_fee": self.format_amount(
                        patient["medicine_fee"]
                    ),
                    "other_charges": self.format_amount(
                        patient["other_charges"]
                    ),
                    "total_amount": self.format_amount(
                        patient["total_amount"]
                    ),
                    "amount_paid": self.format_amount(
                        patient["amount_paid"]
                    ),
                    "payment_status": patient["payment_status"]
                }

            else:

                billing_values = {
                    "bill_number": "Not Generated",
                    "consultation_fee": "-",
                    "medicine_fee": "-",
                    "other_charges": "-",
                    "total_amount": "-",
                    "amount_paid": "-",
                    "payment_status": "-"
                }

            for key, value in billing_values.items():
                self.billing_fields[key].configure(
                    text=str(value)
                )

            # Action buttons
            status = patient["status"]

            self.start_button.configure(
                state="normal" if status == "Waiting" else "disabled"
            )

            self.billing_button.configure(
                state=(
                    "normal"
                    if status in ("In Progress", "Completed")
                    else "disabled"
                )
            )

            if status == "Cancelled":
                self.billing_button.configure(state="disabled")

            # Previous visits
            self.load_visit_history(patient["patient_id"])

            self.message_label.configure(text="")

        except sqlite3.Error as error:

            print("Patient details database error:", error)

            self.show_message(
                "Unable to load patient information.",
                error=True
            )

    # ========================================================
    # FORMAT AMOUNT
    # ========================================================

    @staticmethod
    def format_amount(amount):

        return f"₹{float(amount or 0):,.2f}"

    # ========================================================
    # START CONSULTATION
    # ========================================================

    def start_consultation(self):

        if not self.patient:
            return

        if self.patient["status"] != "Waiting":
            messagebox.showwarning(
                "Consultation",
                "Only waiting patients can start consultation.",
                parent=self
            )
            return

        try:
            updated = execute_query(
                """
                UPDATE visits
                SET
                    status = 'In Progress',
                    doctor_id = ?
                WHERE id = ?
                  AND status = 'Waiting'
                """,
                (
                    self.app.doctor_id,
                    self.visit_id
                )
            )

            if updated:

                messagebox.showinfo(
                    "Success",
                    "Consultation started successfully.",
                    parent=self
                )

                self.app.show_billing(
                    visit_id=self.visit_id
                )

            else:

                self.load_patient_details()

                messagebox.showwarning(
                    "Consultation",
                    "Token status has changed. Please refresh.",
                    parent=self
                )

        except sqlite3.Error as error:

            messagebox.showerror(
                "Database Error",
                str(error),
                parent=self
            )

    # ========================================================
    # OPEN BILLING
    # ========================================================

    def open_billing(self):

        if not self.patient:
            return

        if self.patient["status"] not in (
            "In Progress",
            "Completed"
        ):
            return

        self.app.show_billing(
            visit_id=self.visit_id
        )

    # ========================================================
    # PREVIOUS VISITS
    # ========================================================

    def load_visit_history(self, patient_id):

        for widget in self.history_frame.winfo_children():
            widget.destroy()

        try:
            records = fetch_all(
                """
                SELECT
                    v.id,
                    v.token_number,
                    v.visit_date,
                    v.status,
                    b.total_amount

                FROM visits v

                LEFT JOIN bills b
                    ON b.visit_id = v.id

                WHERE v.patient_id = ?
                  AND v.id != ?

                ORDER BY
                    v.visit_date DESC,
                    v.id DESC

                LIMIT 10
                """,
                (
                    patient_id,
                    self.visit_id
                )
            )

            headers = [
                "Date",
                "Token",
                "Status",
                "Bill Amount"
            ]

            for column, heading in enumerate(headers):

                self.history_frame.grid_columnconfigure(
                    column,
                    weight=1
                )

                ctk.CTkLabel(
                    self.history_frame,
                    text=heading,
                    font=("Arial", 13, "bold"),
                    text_color=TEXT_COLOR,
                    anchor="w"
                ).grid(
                    row=0,
                    column=column,
                    padx=10,
                    pady=10,
                    sticky="w"
                )

            if not records:

                ctk.CTkLabel(
                    self.history_frame,
                    text="No previous visits found.",
                    font=("Arial", 14),
                    text_color=MUTED_TEXT_COLOR
                ).grid(
                    row=1,
                    column=0,
                    columnspan=4,
                    pady=20
                )

                return

            for row_index, record in enumerate(
                records,
                start=1
            ):

                values = [
                    record["visit_date"],
                    record["token_number"],
                    record["status"],
                    (
                        self.format_amount(record["total_amount"])
                        if record["total_amount"] is not None
                        else "-"
                    )
                ]

                for column, value in enumerate(values):

                    ctk.CTkLabel(
                        self.history_frame,
                        text=str(value),
                        font=("Arial", 13),
                        text_color=TEXT_COLOR,
                        anchor="w"
                    ).grid(
                        row=row_index,
                        column=column,
                        padx=10,
                        pady=8,
                        sticky="w"
                    )

        except sqlite3.Error as error:

            print("Patient history error:", error)

            ctk.CTkLabel(
                self.history_frame,
                text="Unable to load previous visits.",
                text_color=ERROR_COLOR
            ).pack(pady=10)


# ============================================================
# END OF FILE
# ============================================================
