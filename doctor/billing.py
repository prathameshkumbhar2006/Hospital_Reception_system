# ============================================================
# HOSPITAL RECEPTION SYSTEM
# FILE: doctor/billing.py
# PURPOSE: Consultation Billing, Payments and Receipts
# DATABASE: SQLite3
# GUI: CustomTkinter
# OS: Ubuntu Linux
# ============================================================

import os
import sqlite3
import subprocess
from datetime import date, datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from tkinter import messagebox

import customtkinter as ctk

from reportlab.lib import colors
from reportlab.lib.pagesizes import A5
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

from config import (
    BACKGROUND_COLOR,
    CARD_COLOR,
    PRIMARY_COLOR,
    PRIMARY_HOVER_COLOR,
    TEXT_COLOR,
    MUTED_TEXT_COLOR,
    BORDER_COLOR,
    SUCCESS_COLOR,
    ERROR_COLOR,
    HOSPITAL_NAME,
    HOSPITAL_ADDRESS,
    HOSPITAL_PHONE,
    RECEIPTS_DIR
)

from database import get_connection, fetch_one


# ============================================================
# BILLING SCREEN
# ============================================================

class BillingScreen(ctk.CTkFrame):

    def __init__(self, parent, app, visit_id=None):

        super().__init__(
            parent,
            fg_color=BACKGROUND_COLOR,
            corner_radius=0
        )

        self.app = app
        self.visit_id = visit_id
        self.patient = None
        self.bill = None

        self.create_widgets()

        if self.visit_id:
            self.load_patient()

    # ========================================================
    # 1. CREATE GUI
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

        header.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(
            header,
            text="Patient Billing",
            font=("Arial", 27, "bold"),
            text_color=TEXT_COLOR
        ).pack(side="left")

        ctk.CTkButton(
            header,
            text="Refresh",
            width=100,
            height=40,
            command=self.load_patient
        ).pack(side="right")

        # Token search
        search_card = self.create_card("Search Patient Token")

        search_row = ctk.CTkFrame(
            search_card,
            fg_color="transparent"
        )

        search_row.pack(
            fill="x",
            padx=20,
            pady=(0, 15)
        )

        self.token_entry = ctk.CTkEntry(
            search_row,
            height=45,
            placeholder_text="A-001 or A-001 2026-10-13",
            font=("Arial", 16)
        )

        self.token_entry.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(0, 10)
        )

        self.token_entry.bind(
            "<Return>",
            lambda event: self.search_token()
        )

        ctk.CTkButton(
            search_row,
            text="Search",
            width=110,
            height=45,
            command=self.search_token
        ).pack(side="right")

        # Patient information
        patient_card = self.create_card("Patient Information")

        self.patient_labels = {}

        fields = [
            ("Patient ID", "patient_id"),
            ("Patient Name", "name"),
            ("Mobile Number", "mobile"),
            ("Gender", "gender"),
            ("Token Number", "token_number"),
            ("Visit Date", "visit_date"),
            ("Visit Status", "status")
        ]

        for title, key in fields:

            self.patient_labels[key] = self.create_info_row(
                patient_card,
                title
            )

        # Billing fields
        billing_card = self.create_card("Billing Details")

        self.consultation_entry = self.create_amount_field(
            billing_card,
            "Consultation Fee"
        )

        self.medicine_entry = self.create_amount_field(
            billing_card,
            "Medicine Fee"
        )

        self.other_entry = self.create_amount_field(
            billing_card,
            "Other Charges"
        )

        # Total
        total_frame = ctk.CTkFrame(
            billing_card,
            fg_color="#EFF6FF",
            corner_radius=8
        )

        total_frame.pack(
            fill="x",
            padx=20,
            pady=15
        )

        ctk.CTkLabel(
            total_frame,
            text="Total Amount",
            font=("Arial", 19, "bold"),
            text_color=TEXT_COLOR
        ).pack(
            side="left",
            padx=20,
            pady=15
        )

        self.total_label = ctk.CTkLabel(
            total_frame,
            text="₹0.00",
            font=("Arial", 25, "bold"),
            text_color=PRIMARY_COLOR
        )

        self.total_label.pack(
            side="right",
            padx=20
        )

        # Payment options
        payment_card = self.create_card("Payment Details")

        ctk.CTkLabel(
            payment_card,
            text="Payment Method",
            font=("Arial", 15, "bold"),
            text_color=TEXT_COLOR
        ).pack(
            anchor="w",
            padx=20,
            pady=(5, 5)
        )

        self.payment_method = ctk.CTkOptionMenu(
            payment_card,
            values=["Cash", "UPI", "Card"],
            width=250,
            height=40
        )

        self.payment_method.pack(
            anchor="w",
            padx=20,
            pady=(0, 15)
        )

        self.payment_method.set("Cash")

        ctk.CTkLabel(
            payment_card,
            text="Payment Status",
            font=("Arial", 15, "bold"),
            text_color=TEXT_COLOR
        ).pack(
            anchor="w",
            padx=20,
            pady=(0, 5)
        )

        self.payment_status = ctk.CTkOptionMenu(
            payment_card,
            values=["Unpaid", "Paid", "Partial"],
            width=250,
            height=40,
            command=self.payment_status_changed
        )

        self.payment_status.pack(
            anchor="w",
            padx=20,
            pady=(0, 15)
        )

        self.payment_status.set("Unpaid")

        self.amount_paid_entry = self.create_amount_field(
            payment_card,
            "Amount Received"
        )

        self.amount_paid_entry.insert(0, "0")

        self.amount_paid_entry.configure(state="disabled")

        ctk.CTkLabel(
            payment_card,
            text="Payment Reference (Optional)",
            font=("Arial", 15, "bold"),
            text_color=TEXT_COLOR
        ).pack(
            anchor="w",
            padx=20,
            pady=(0, 5)
        )

        self.reference_entry = ctk.CTkEntry(
            payment_card,
            height=42,
            placeholder_text="UPI / Card transaction reference"
        )

        self.reference_entry.pack(
            fill="x",
            padx=20,
            pady=(0, 20)
        )

        # Buttons
        actions = ctk.CTkFrame(
            self.container,
            fg_color="transparent"
        )

        actions.pack(fill="x", pady=15)

        self.calculate_button = ctk.CTkButton(
            actions,
            text="Calculate Total",
            width=150,
            height=45,
            command=self.calculate_total
        )

        self.calculate_button.pack(
            side="left",
            padx=(0, 10)
        )

        self.save_button = ctk.CTkButton(
            actions,
            text="Save Bill",
            width=150,
            height=45,
            fg_color=SUCCESS_COLOR,
            hover_color="#15803D",
            command=self.save_bill
        )

        self.save_button.pack(
            side="left",
            padx=(0, 10)
        )

        self.receipt_button = ctk.CTkButton(
            actions,
            text="Generate Receipt",
            width=170,
            height=45,
            command=self.generate_receipt
        )

        self.receipt_button.pack(
            side="left",
            padx=(0, 10)
        )

        self.tokens_button = ctk.CTkButton(
            actions,
            text="Back to Tokens",
            width=140,
            height=45,
            fg_color="#E5E7EB",
            hover_color="#D1D5DB",
            text_color=TEXT_COLOR,
            command=self.app.show_tokens
        )

        self.tokens_button.pack(side="right")

        self.message_label = ctk.CTkLabel(
            self.container,
            text="",
            font=("Arial", 14),
            text_color=ERROR_COLOR
        )

        self.message_label.pack(pady=10)

        self.set_form_state(False)

    # ========================================================
    # 2. GUI HELPERS
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
            pady=(15, 12)
        )

        return card

    def create_info_row(self, parent, title):

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
            width=180,
            anchor="w",
            text_color=MUTED_TEXT_COLOR
        ).pack(side="left")

        value = ctk.CTkLabel(
            row,
            text="-",
            anchor="w",
            font=("Arial", 14, "bold"),
            text_color=TEXT_COLOR
        )

        value.pack(
            side="left",
            fill="x",
            expand=True
        )

        return value

    def create_amount_field(self, parent, title):

        ctk.CTkLabel(
            parent,
            text=title,
            font=("Arial", 15, "bold"),
            text_color=TEXT_COLOR
        ).pack(
            anchor="w",
            padx=20,
            pady=(5, 5)
        )

        entry = ctk.CTkEntry(
            parent,
            height=43,
            placeholder_text="0.00",
            font=("Arial", 16)
        )

        entry.pack(
            fill="x",
            padx=20,
            pady=(0, 15)
        )

        if title != "Amount Received":
            entry.insert(0, "0")

        return entry

    def show_message(self, message, success=False):

        self.message_label.configure(
            text=message,
            text_color=SUCCESS_COLOR if success else ERROR_COLOR
        )

    def set_form_state(self, enabled):

        state = "normal" if enabled else "disabled"

        for entry in [
            self.consultation_entry,
            self.medicine_entry,
            self.other_entry,
            self.reference_entry
        ]:
            entry.configure(state=state)

        self.payment_method.configure(state=state)
        self.payment_status.configure(state=state)
        self.calculate_button.configure(state=state)
        self.save_button.configure(state=state)

        if not enabled:
            self.amount_paid_entry.configure(state="disabled")

        self.receipt_button.configure(
            state="normal" if self.bill else "disabled"
        )

    # ========================================================
    # 3. AMOUNT HANDLING
    # ========================================================

    @staticmethod
    def parse_amount(value):

        try:
            amount = Decimal(str(value).strip())

            if not amount.is_finite() or amount < 0:
                raise ValueError

            if amount > Decimal("99999999.99"):
                raise ValueError

            if amount.as_tuple().exponent < -2:
                raise ValueError

            return amount.quantize(
                Decimal("0.01"),
                rounding=ROUND_HALF_UP
            )

        except (InvalidOperation, ValueError):
            raise ValueError(
                "Enter a valid amount with up to 2 decimal places."
            )

    def get_fee_details(self):

        consultation = self.parse_amount(
            self.consultation_entry.get()
        )

        medicine = self.parse_amount(
            self.medicine_entry.get()
        )

        other = self.parse_amount(
            self.other_entry.get()
        )

        total = consultation + medicine + other

        if total > Decimal("99999999.99"):
            raise ValueError("Total amount is too large.")

        return consultation, medicine, other, total

    def calculate_total(self):

        try:

            _, _, _, total = self.get_fee_details()

            self.total_label.configure(
                text=f"₹{total:,.2f}"
            )

            if self.payment_status.get() == "Paid":

                self.amount_paid_entry.configure(state="normal")
                self.amount_paid_entry.delete(0, "end")
                self.amount_paid_entry.insert(0, str(total))
                self.amount_paid_entry.configure(state="disabled")

            self.show_message("Total calculated.", True)

            return total

        except ValueError as error:

            self.show_message(str(error))

            return None

    def payment_status_changed(self, status):

        self.amount_paid_entry.configure(state="normal")
        self.amount_paid_entry.delete(0, "end")

        if status == "Unpaid":

            self.amount_paid_entry.insert(0, "0")
            self.amount_paid_entry.configure(state="disabled")

        elif status == "Paid":

            try:
                total = self.get_fee_details()[3]
            except ValueError:
                total = Decimal("0.00")

            self.amount_paid_entry.insert(0, str(total))
            self.amount_paid_entry.configure(state="disabled")

        else:

            self.amount_paid_entry.insert(0, "0")

    # ========================================================
    # 4. SEARCH TOKEN
    # ========================================================

    def search_token(self):

        token = self.token_entry.get().strip().upper()

        if not token:
            self.show_message("Enter a token number.")
            return

        try:
            # Token sequences restart every day. Search all dates, then
            # choose the most recent matching visit unless the doctor
            # explicitly enters a date alongside the token.
            # Supported format: A-004 or A-004 2026-10-13
            parts = token.split()
            if len(parts) == 2:
                token_number, search_date = parts
                try:
                    datetime.strptime(search_date, "%Y-%m-%d")
                except ValueError:
                    self.show_message(
                        "Use A-004 or A-004 YYYY-MM-DD."
                    )
                    return
                visit = fetch_one(
                    """
                    SELECT id FROM visits
                    WHERE UPPER(token_number) = ? AND visit_date = ?
                    ORDER BY id DESC LIMIT 1
                    """,
                    (token_number, search_date)
                )
            elif len(parts) == 1:
                visit = fetch_one(
                    """
                    SELECT id FROM visits
                    WHERE UPPER(token_number) = ?
                    ORDER BY visit_date DESC, id DESC
                    LIMIT 1
                    """,
                    (token,)
                )
            else:
                self.show_message("Use A-004 or A-004 YYYY-MM-DD.")
                return

            if not visit:
                self.visit_id = None
                self.patient = None
                self.bill = None
                for label in self.patient_labels.values():
                    label.configure(text="-")
                self.reset_amount_fields()
                self.set_form_state(False)
                self.show_message("No matching patient token found.")
                return

            self.visit_id = visit["id"]
            self.load_patient()

        except sqlite3.Error as error:
            self.show_message(str(error))

    # ========================================================
    # 5. LOAD PATIENT
    # ========================================================

    def load_patient(self):

        if not self.visit_id:
            return

        try:

            self.patient = fetch_one(
                """
                SELECT
                    v.id AS visit_id,
                    v.patient_id,
                    v.token_number,
                    v.visit_date,
                    v.status,
                    v.doctor_id,
                    p.name,
                    p.mobile,
                    p.gender
                FROM visits v
                JOIN patients p ON p.id = v.patient_id
                WHERE v.id = ?
                """,
                (self.visit_id,)
            )

            if not self.patient:

                self.show_message("Patient visit not found.")
                self.bill = None
                self.set_form_state(False)
                return

            for key in self.patient_labels:

                self.patient_labels[key].configure(
                    text=str(self.patient.get(key, "-"))
                )

            self.token_entry.delete(0, "end")
            self.token_entry.insert(
                0,
                self.patient["token_number"]
            )

            self.bill = fetch_one(
                """
                SELECT *
                FROM bills
                WHERE visit_id = ?
                """,
                (self.visit_id,)
            )

            self.reset_amount_fields()

            if self.bill:

                self.display_existing_bill()

            elif self.patient["status"] == "In Progress":

                if self.patient["doctor_id"] not in (
                    None,
                    self.app.doctor_id
                ):
                    self.set_form_state(False)
                    self.show_message(
                        "This consultation belongs to another doctor."
                    )
                else:
                    self.set_form_state(True)
                    self.show_message(
                        "Enter consultation and medicine fees."
                    )

            else:

                self.set_form_state(False)

                self.show_message(
                    "Start consultation before creating a bill."
                )

        except sqlite3.Error as error:

            self.show_message(str(error))

    def reset_amount_fields(self):

        for entry in [
            self.consultation_entry,
            self.medicine_entry,
            self.other_entry,
            self.amount_paid_entry,
            self.reference_entry
        ]:

            entry.configure(state="normal")
            entry.delete(0, "end")

        for entry in [
            self.consultation_entry,
            self.medicine_entry,
            self.other_entry,
            self.amount_paid_entry
        ]:

            entry.insert(0, "0")

        self.payment_status.configure(state="normal")
        self.payment_method.configure(state="normal")

        self.payment_status.set("Unpaid")
        self.payment_method.set("Cash")

        self.total_label.configure(text="₹0.00")

    def display_existing_bill(self):

        bill = self.bill

        fields = [
            (self.consultation_entry, bill["consultation_fee"]),
            (self.medicine_entry, bill["medicine_fee"]),
            (self.other_entry, bill["other_charges"])
        ]

        for entry, amount in fields:

            entry.configure(state="normal")
            entry.delete(0, "end")
            entry.insert(0, f"{amount:.2f}")

        self.total_label.configure(
            text=f"₹{bill['total_amount']:,.2f}"
        )

        self.payment_status.set(bill["payment_status"])

        if bill["payment_method"]:
            self.payment_method.set(bill["payment_method"])

        paid = fetch_one(
            """
            SELECT COALESCE(SUM(amount), 0) AS total
            FROM payments
            WHERE bill_id = ?
            """,
            (bill["id"],)
        )

        self.amount_paid_entry.configure(state="normal")
        self.amount_paid_entry.delete(0, "end")
        self.amount_paid_entry.insert(
            0,
            f"{paid['total']:.2f}"
        )

        self.set_form_state(False)

        self.show_message(
            f"Bill {bill['bill_number']} already saved.",
            True
        )

    # ========================================================
    # 6. SAVE BILL
    # ========================================================

    def save_bill(self):

        if not self.patient or self.bill:
            return

        try:

            consultation, medicine, other, total = (
                self.get_fee_details()
            )

            status = self.payment_status.get()
            method = self.payment_method.get()

            if status == "Paid":

                amount_paid = total

            elif status == "Partial":

                amount_paid = self.parse_amount(
                    self.amount_paid_entry.get()
                )

                if not (
                    Decimal("0.00") < amount_paid < total
                ):
                    raise ValueError(
                        "Partial payment must be greater than zero "
                        "and less than the total."
                    )

            else:

                amount_paid = Decimal("0.00")

            reference = self.reference_entry.get().strip()

        except ValueError as error:

            self.show_message(str(error))
            return

        if self.patient["status"] != "In Progress":

            self.show_message(
                "Consultation must be In Progress."
            )
            return

        confirm = messagebox.askyesno(
            "Save Bill",
            f"Total Amount: ₹{total:,.2f}\n"
            f"Amount Received: ₹{amount_paid:,.2f}\n\n"
            "Save this bill?",
            parent=self
        )

        if not confirm:
            return

        connection = None

        try:

            connection = get_connection()
            connection.execute("BEGIN IMMEDIATE")

            # Prevent duplicate bills
            existing = connection.execute(
                "SELECT id FROM bills WHERE visit_id = ?",
                (self.visit_id,)
            ).fetchone()

            if existing:
                connection.rollback()
                self.load_patient()
                self.show_message("A bill already exists.")
                return

            # Check visit status
            visit = connection.execute(
                """
                SELECT status, doctor_id
                FROM visits
                WHERE id = ?
                """,
                (self.visit_id,)
            ).fetchone()

            if (
                not visit
                or visit["status"] != "In Progress"
                or visit["doctor_id"] != self.app.doctor_id
            ):
                connection.rollback()
                self.show_message(
                    "Consultation status or doctor assignment changed."
                )
                return

            # Insert using a temporary unique bill number
            temporary_number = (
                "TMP-" + datetime.now().strftime("%Y%m%d%H%M%S%f")
            )

            cursor = connection.execute(
                """
                INSERT INTO bills (
                    bill_number,
                    visit_id,
                    consultation_fee,
                    medicine_fee,
                    other_charges,
                    total_amount,
                    payment_method,
                    payment_status
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    temporary_number,
                    self.visit_id,
                    float(consultation),
                    float(medicine),
                    float(other),
                    float(total),
                    method if amount_paid > 0 else None,
                    status
                )
            )

            bill_id = cursor.lastrowid
            bill_number = f"BILL-{bill_id:06d}"

            connection.execute(
                """
                UPDATE bills
                SET bill_number = ?
                WHERE id = ?
                """,
                (bill_number, bill_id)
            )

            # Store actual collected payment
            if amount_paid > 0:

                connection.execute(
                    """
                    INSERT INTO payments (
                        bill_id,
                        amount,
                        payment_method,
                        payment_reference,
                        paid_at
                    )
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        bill_id,
                        float(amount_paid),
                        method,
                        reference or None,
                        datetime.now().strftime(
                            "%Y-%m-%d %H:%M:%S"
                        )
                    )
                )

            # Complete visit after billing
            connection.execute(
                """
                UPDATE visits
                SET status = 'Completed',
                    completed_at = ?
                WHERE id = ?
                """,
                (
                    datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                    self.visit_id
                )
            )

            connection.commit()

            messagebox.showinfo(
                "Success",
                f"Bill saved successfully.\n\n"
                f"Bill Number: {bill_number}",
                parent=self
            )

            self.load_patient()

        except sqlite3.Error as error:

            if connection:
                connection.rollback()

            self.show_message(
                f"Unable to save bill: {error}"
            )

        finally:

            if connection:
                connection.close()

    # ========================================================
    # 7. GENERATE PDF RECEIPT
    # ========================================================

    def generate_receipt(self):

        if not self.bill:
            self.show_message("Save the bill first.")
            return

        try:

            os.makedirs(RECEIPTS_DIR, exist_ok=True)

            bill = fetch_one(
                """
                SELECT
                    b.*,
                    p.name AS patient_name,
                    p.mobile,
                    v.token_number,
                    v.visit_date,
                    d.name AS doctor_name
                FROM bills b
                JOIN visits v ON v.id = b.visit_id
                JOIN patients p ON p.id = v.patient_id
                LEFT JOIN doctors d ON d.id = v.doctor_id
                WHERE b.id = ?
                """,
                (self.bill["id"],)
            )

            if not bill:
                self.show_message("Bill not found.")
                return

            paid = fetch_one(
                """
                SELECT COALESCE(SUM(amount), 0) AS total
                FROM payments
                WHERE bill_id = ?
                """,
                (bill["id"],)
            )

            filename = f"{bill['bill_number']}.pdf"

            filepath = os.path.join(
                RECEIPTS_DIR,
                filename
            )

            pdf = canvas.Canvas(
                filepath,
                pagesize=A5
            )

            width, height = A5

            y = height - 25 * mm

            # Hospital name
            pdf.setFont("Helvetica-Bold", 16)
            pdf.drawCentredString(
                width / 2,
                y,
                "HOSPITAL"
            )

            y -= 8 * mm

            pdf.setFont("Helvetica", 10)
            pdf.drawCentredString(
                width / 2,
                y,
                "PAYMENT RECEIPT"
            )

            y -= 12 * mm

            pdf.setStrokeColor(colors.grey)
            pdf.line(
                15 * mm,
                y,
                width - 15 * mm,
                y
            )

            y -= 10 * mm

            def line(label, value):

                nonlocal y

                pdf.setFont("Helvetica", 10)

                pdf.drawString(
                    18 * mm,
                    y,
                    str(label)
                )

                pdf.drawRightString(
                    width - 18 * mm,
                    y,
                    str(value)
                )

                y -= 8 * mm

            line("Receipt No.", bill["bill_number"])
            line("Date", bill["created_at"][:10])
            line("Token", bill["token_number"])
            line("Patient ID", str(self.patient["patient_id"]))
            line("Mobile", bill["mobile"])

            # Patient name (Latin PDF font fallback)
            patient_name = bill["patient_name"]

            try:
                patient_name.encode("latin-1")
                line("Patient", patient_name[:32])
            except UnicodeEncodeError:
                line("Patient", f"ID {self.patient['patient_id']}")

            if bill["doctor_name"]:
                doctor_name = bill["doctor_name"]
                try:
                    doctor_name.encode("latin-1")
                    line("Doctor", doctor_name[:32])
                except UnicodeEncodeError:
                    pass

            y -= 3 * mm

            pdf.line(
                15 * mm,
                y,
                width - 15 * mm,
                y
            )

            y -= 10 * mm

            line(
                "Consultation Fee",
                f"INR {bill['consultation_fee']:.2f}"
            )

            line(
                "Medicine Fee",
                f"INR {bill['medicine_fee']:.2f}"
            )

            line(
                "Other Charges",
                f"INR {bill['other_charges']:.2f}"
            )

            y -= 3 * mm

            pdf.line(
                15 * mm,
                y,
                width - 15 * mm,
                y
            )

            y -= 10 * mm

            pdf.setFont("Helvetica-Bold", 12)

            pdf.drawString(
                18 * mm,
                y,
                "TOTAL"
            )

            pdf.drawRightString(
                width - 18 * mm,
                y,
                f"INR {bill['total_amount']:.2f}"
            )

            y -= 12 * mm

            pdf.setFont("Helvetica", 10)

            line(
                "Amount Paid",
                f"INR {paid['total']:.2f}"
            )

            balance = max(
                Decimal("0.00"),
                Decimal(str(bill["total_amount"]))
                - Decimal(str(paid["total"]))
            )

            line(
                "Balance",
                f"INR {balance:.2f}"
            )

            line(
                "Payment Status",
                bill["payment_status"]
            )

            y -= 15 * mm

            pdf.setFont("Helvetica", 10)

            pdf.drawCentredString(
                width / 2,
                y,
                "Thank You! Get Well Soon."
            )

            pdf.save()

            self.show_message(
                f"Receipt generated: {filename}",
                True
            )

            # Open receipt in Ubuntu PDF viewer
            try:
                subprocess.Popen(
                    ["xdg-open", filepath],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            except OSError:
                pass

        except (sqlite3.Error, OSError) as error:

            self.show_message(
                f"Receipt generation failed: {error}"
            )


# ============================================================
# END OF FILE
# ============================================================
