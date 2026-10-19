# ============================================================
# HOSPITAL RECEPTION SYSTEM
# FILE: doctor/receipts.py
# PURPOSE: View, Search, Generate, Download and Print Receipts
# DATABASE: SQLite3
# GUI: CustomTkinter
# OS: Ubuntu Linux
# ============================================================

import os
import sqlite3
import subprocess
import shutil
from datetime import date
from decimal import Decimal
from tkinter import messagebox, filedialog

import customtkinter as ctk

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A5
from reportlab.lib.units import mm

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

from database import fetch_one, fetch_all


# ============================================================
# RECEIPTS SCREEN
# ============================================================

class ReceiptsScreen(ctk.CTkFrame):

    def __init__(self, parent, app):
        super().__init__(
            parent,
            fg_color=BACKGROUND_COLOR,
            corner_radius=0
        )

        self.app = app
        self.selected_bill_id = None
        self.selected_bill = None

        os.makedirs(RECEIPTS_DIR, exist_ok=True)

        self.create_widgets()
        self.load_receipts()

    # ========================================================
    # 1. CREATE INTERFACE
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
            text="Patient Receipts",
            font=("Arial", 27, "bold"),
            text_color=TEXT_COLOR
        ).pack(side="left")

        ctk.CTkButton(
            header,
            text="Refresh",
            width=110,
            height=40,
            command=self.show_all
        ).pack(side="right")

        # Search
        search_card = self.create_card("Search Receipts")

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
            placeholder_text="Bill number, token, patient name or mobile",
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
            lambda event: self.search_receipts()
        )

        ctk.CTkButton(
            search_row,
            text="Search",
            width=90,
            height=43,
            command=self.search_receipts
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            search_row,
            text="Show All",
            width=90,
            height=43,
            fg_color="#E5E7EB",
            hover_color="#D1D5DB",
            text_color=TEXT_COLOR,
            command=self.show_all
        ).pack(side="left")

        # Filters
        filter_row = ctk.CTkFrame(
            search_card,
            fg_color="transparent"
        )

        filter_row.pack(
            fill="x",
            padx=15,
            pady=(0, 15)
        )

        ctk.CTkLabel(
            filter_row,
            text="Payment Status:",
            text_color=TEXT_COLOR
        ).pack(side="left", padx=(0, 10))

        self.status_filter = ctk.CTkOptionMenu(
            filter_row,
            values=["All", "Paid", "Unpaid", "Partial"],
            width=140,
            command=lambda value: self.search_receipts()
        )

        self.status_filter.pack(side="left", padx=(0, 20))
        self.status_filter.set("All")

        ctk.CTkLabel(
            filter_row,
            text="Date:",
            text_color=TEXT_COLOR
        ).pack(side="left", padx=(0, 10))

        self.date_filter = ctk.CTkOptionMenu(
            filter_row,
            values=["All Dates", "Today"],
            width=140,
            command=lambda value: self.search_receipts()
        )

        self.date_filter.pack(side="left")
        self.date_filter.set("All Dates")

        # Summary
        summary_frame = ctk.CTkFrame(
            self.container,
            fg_color="transparent"
        )

        summary_frame.pack(fill="x", pady=(0, 15))

        self.total_bills_label = self.create_summary_card(
            summary_frame, "Total Bills", 0
        )

        self.total_amount_label = self.create_summary_card(
            summary_frame, "Total Billing", 1
        )

        self.collected_label = self.create_summary_card(
            summary_frame, "Amount Collected", 2
        )

        self.balance_label = self.create_summary_card(
            summary_frame, "Outstanding Balance", 3
        )

        # Receipts table
        table_card = self.create_card("Receipt Records")

        table_card.pack_configure(
            fill="both",
            expand=True
        )

        self.table_frame = ctk.CTkScrollableFrame(
            table_card,
            fg_color="transparent"
        )

        self.table_frame.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=(0, 15)
        )

        # Selected receipt
        selected_card = self.create_card("Selected Receipt")

        self.selected_label = ctk.CTkLabel(
            selected_card,
            text="No receipt selected",
            font=("Arial", 14),
            text_color=MUTED_TEXT_COLOR,
            anchor="w"
        )

        self.selected_label.pack(
            fill="x",
            padx=15,
            pady=(0, 12)
        )

        # Action buttons
        actions = ctk.CTkFrame(
            selected_card,
            fg_color="transparent"
        )

        actions.pack(
            fill="x",
            padx=15,
            pady=(0, 15)
        )

        self.generate_button = ctk.CTkButton(
            actions,
            text="Generate PDF",
            width=130,
            height=43,
            command=self.generate_selected_receipt
        )

        self.generate_button.pack(
            side="left",
            padx=(0, 8)
        )

        self.open_button = ctk.CTkButton(
            actions,
            text="Open Receipt",
            width=130,
            height=43,
            command=self.open_receipt
        )

        self.open_button.pack(
            side="left",
            padx=(0, 8)
        )

        self.download_button = ctk.CTkButton(
            actions,
            text="Download",
            width=120,
            height=43,
            command=self.download_receipt
        )

        self.download_button.pack(
            side="left",
            padx=(0, 8)
        )

        self.print_button = ctk.CTkButton(
            actions,
            text="Print Receipt",
            width=130,
            height=43,
            fg_color=SUCCESS_COLOR,
            hover_color="#15803D",
            command=self.print_receipt
        )

        self.print_button.pack(side="left")

        self.message_label = ctk.CTkLabel(
            self.container,
            text="",
            font=("Arial", 13),
            text_color=ERROR_COLOR
        )

        self.message_label.pack(pady=5)

        self.set_buttons_state(False)

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

        card.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(
            card,
            text=title,
            font=("Arial", 18, "bold"),
            text_color=TEXT_COLOR
        ).pack(
            anchor="w",
            padx=15,
            pady=(15, 10)
        )

        return card

    def create_summary_card(self, parent, title, column):

        parent.grid_columnconfigure(
            column,
            weight=1,
            uniform="receipt_cards"
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
            sticky="nsew"
        )

        ctk.CTkLabel(
            card,
            text=title,
            font=("Arial", 13),
            text_color=MUTED_TEXT_COLOR
        ).pack(pady=(12, 5))

        value_label = ctk.CTkLabel(
            card,
            text="0",
            font=("Arial", 22, "bold"),
            text_color=PRIMARY_COLOR
        )

        value_label.pack(pady=(0, 12))

        return value_label

    def show_message(self, text, success=False):

        self.message_label.configure(
            text=text,
            text_color=SUCCESS_COLOR if success else ERROR_COLOR
        )

    def set_buttons_state(self, enabled):

        state = "normal" if enabled else "disabled"

        self.generate_button.configure(state=state)
        self.open_button.configure(state=state)
        self.download_button.configure(state=state)
        self.print_button.configure(state=state)

    @staticmethod
    def format_amount(amount):

        return f"₹{Decimal(str(amount or 0)):,.2f}"

    # ========================================================
    # 3. DATABASE QUERIES
    # ========================================================

    def get_receipts(self, search="", status="All", date_option="All Dates"):

        query = """
            SELECT
                b.id,
                b.bill_number,
                b.visit_id,
                b.total_amount,
                b.payment_status,
                b.created_at,

                p.id AS patient_id,
                p.name AS patient_name,
                p.mobile,

                v.token_number,
                v.visit_date,

                COALESCE(
                    (
                        SELECT SUM(pay.amount)
                        FROM payments pay
                        WHERE pay.bill_id = b.id
                    ),
                    0
                ) AS amount_paid

            FROM bills b

            JOIN visits v
                ON v.id = b.visit_id

            JOIN patients p
                ON p.id = v.patient_id

            WHERE 1 = 1
        """

        params = []

        if search:

            query += """
                AND (
                    b.bill_number LIKE ?
                    OR v.token_number LIKE ?
                    OR p.name LIKE ?
                    OR p.mobile LIKE ?
                )
            """

            pattern = f"%{search}%"

            params.extend([
                pattern,
                pattern,
                pattern,
                pattern
            ])

        if status != "All":

            query += """
                AND b.payment_status = ?
            """

            params.append(status)

        if date_option == "Today":

            query += """
                AND DATE(b.created_at) = ?
            """

            params.append(date.today().isoformat())

        query += """
            ORDER BY b.id DESC
        """

        return fetch_all(query, tuple(params))

    def get_receipt_details(self, bill_id):

        return fetch_one(
            """
            SELECT
                b.*,

                p.id AS patient_id,
                p.name AS patient_name,
                p.mobile,
                p.gender,

                v.token_number,
                v.visit_date,
                v.visit_time,

                d.name AS doctor_name,

                COALESCE(
                    (
                        SELECT SUM(pay.amount)
                        FROM payments pay
                        WHERE pay.bill_id = b.id
                    ),
                    0
                ) AS amount_paid

            FROM bills b

            JOIN visits v
                ON v.id = b.visit_id

            JOIN patients p
                ON p.id = v.patient_id

            LEFT JOIN doctors d
                ON d.id = v.doctor_id

            WHERE b.id = ?
            """,
            (bill_id,)
        )

    # ========================================================
    # 4. LOAD RECEIPTS
    # ========================================================

    def load_receipts(self):

        try:

            search = self.search_entry.get().strip()

            status = self.status_filter.get()

            date_option = self.date_filter.get()

            records = self.get_receipts(
                search,
                status,
                date_option
            )

            self.update_summary(records)
            self.display_receipts(records)

            self.selected_bill_id = None
            self.selected_bill = None

            self.selected_label.configure(
                text="No receipt selected"
            )

            self.set_buttons_state(False)
            self.message_label.configure(text="")

        except sqlite3.Error as error:

            self.show_message(
                f"Unable to load receipts: {error}"
            )

    def update_summary(self, records):

        total_bills = len(records)

        total_amount = sum(
            (
                Decimal(str(record["total_amount"]))
                for record in records
            ),
            Decimal("0.00")
        )

        collected = sum(
            (
                Decimal(str(record["amount_paid"]))
                for record in records
            ),
            Decimal("0.00")
        )

        balance = total_amount - collected

        self.total_bills_label.configure(
            text=str(total_bills)
        )

        self.total_amount_label.configure(
            text=self.format_amount(total_amount)
        )

        self.collected_label.configure(
            text=self.format_amount(collected)
        )

        self.balance_label.configure(
            text=self.format_amount(balance)
        )

    # ========================================================
    # 5. DISPLAY RECEIPT RECORDS
    # ========================================================

    def display_receipts(self, records):

        for widget in self.table_frame.winfo_children():
            widget.destroy()

        headers = [
            "Bill Number",
            "Patient",
            "Token",
            "Date",
            "Amount",
            "Paid",
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
                font=("Arial", 12, "bold"),
                text_color=TEXT_COLOR,
                anchor="w"
            ).grid(
                row=0,
                column=column,
                padx=8,
                pady=10,
                sticky="w"
            )

        if not records:

            ctk.CTkLabel(
                self.table_frame,
                text="No receipts found.",
                font=("Arial", 15),
                text_color=MUTED_TEXT_COLOR
            ).grid(
                row=1,
                column=0,
                columnspan=8,
                pady=30
            )

            return

        for row_index, record in enumerate(
            records,
            start=1
        ):

            values = [
                record["bill_number"],
                record["patient_name"],
                record["token_number"],
                str(record["created_at"])[:10],
                self.format_amount(record["total_amount"]),
                self.format_amount(record["amount_paid"]),
                record["payment_status"]
            ]

            for column, value in enumerate(values):

                color = TEXT_COLOR

                if column == 6:

                    if value == "Paid":
                        color = SUCCESS_COLOR

                    elif value == "Unpaid":
                        color = ERROR_COLOR

                    else:
                        color = "#D97706"

                ctk.CTkLabel(
                    self.table_frame,
                    text=str(value),
                    font=("Arial", 12),
                    text_color=color,
                    anchor="w"
                ).grid(
                    row=row_index,
                    column=column,
                    padx=8,
                    pady=9,
                    sticky="w"
                )

            ctk.CTkButton(
                self.table_frame,
                text="Select",
                width=75,
                height=32,
                command=lambda item=record: self.select_receipt(item)
            ).grid(
                row=row_index,
                column=7,
                padx=8,
                pady=6
            )

    # ========================================================
    # 6. SEARCH AND SELECT
    # ========================================================

    def search_receipts(self):

        self.load_receipts()

    def show_all(self):

        self.search_entry.delete(0, "end")
        self.status_filter.set("All")
        self.date_filter.set("All Dates")

        self.load_receipts()

    def select_receipt(self, record):

        self.selected_bill_id = record["id"]
        self.selected_bill = record

        self.selected_label.configure(
            text=(
                f"Bill: {record['bill_number']}   |   "
                f"Patient: {record['patient_name']}   |   "
                f"Amount: {self.format_amount(record['total_amount'])}"
            )
        )

        self.set_buttons_state(True)

    # ========================================================
    # 7. RECEIPT FILE PATH
    # ========================================================

    def get_receipt_path(self, bill_number):

        filename = f"{bill_number}.pdf"

        return os.path.join(
            RECEIPTS_DIR,
            filename
        )

    # ========================================================
    # 8. GENERATE PDF
    # ========================================================

    def generate_pdf(self, bill_id):

        bill = self.get_receipt_details(bill_id)

        if not bill:
            raise ValueError("Bill not found.")

        os.makedirs(RECEIPTS_DIR, exist_ok=True)

        filepath = self.get_receipt_path(
            bill["bill_number"]
        )

        pdf = canvas.Canvas(
            filepath,
            pagesize=A5
        )

        width, height = A5

        y = height - 22 * mm

        pdf.setTitle(
            f"Receipt {bill['bill_number']}"
        )

        # Hospital heading
        pdf.setFont("Helvetica-Bold", 16)

        pdf.drawCentredString(
            width / 2,
            y,
            "HOSPITAL"
        )

        y -= 9 * mm

        pdf.setFont("Helvetica", 11)

        pdf.drawCentredString(
            width / 2,
            y,
            "PAYMENT RECEIPT"
        )

        y -= 12 * mm

        pdf.line(
            15 * mm,
            y,
            width - 15 * mm,
            y
        )

        y -= 10 * mm

        def add_line(label, value):

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

        def safe_text(value):

            text = str(value or "")

            try:
                text.encode("latin-1")
                return text[:32]

            except UnicodeEncodeError:
                return "See patient record"

        # Receipt details
        add_line("Receipt No.", bill["bill_number"])

        add_line(
            "Date",
            str(bill["created_at"])[:10]
        )

        add_line(
            "Patient ID",
            bill["patient_id"]
        )

        add_line(
            "Patient",
            safe_text(bill["patient_name"])
        )

        add_line(
            "Mobile",
            bill["mobile"]
        )

        add_line(
            "Token",
            bill["token_number"]
        )

        if bill["doctor_name"]:

            add_line(
                "Doctor",
                safe_text(bill["doctor_name"])
            )

        # Separator
        y -= 3 * mm

        pdf.line(
            15 * mm,
            y,
            width - 15 * mm,
            y
        )

        y -= 10 * mm

        # Billing
        add_line(
            "Consultation Fee",
            f"INR {bill['consultation_fee']:.2f}"
        )

        add_line(
            "Medicine Fee",
            f"INR {bill['medicine_fee']:.2f}"
        )

        add_line(
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

        # Total
        pdf.setFont("Helvetica-Bold", 12)

        pdf.drawString(
            18 * mm,
            y,
            "TOTAL AMOUNT"
        )

        pdf.drawRightString(
            width - 18 * mm,
            y,
            f"INR {bill['total_amount']:.2f}"
        )

        y -= 12 * mm

        paid = Decimal(
            str(bill["amount_paid"])
        )

        total = Decimal(
            str(bill["total_amount"])
        )

        balance = max(
            Decimal("0.00"),
            total - paid
        )

        add_line(
            "Amount Paid",
            f"INR {paid:.2f}"
        )

        add_line(
            "Balance",
            f"INR {balance:.2f}"
        )

        add_line(
            "Payment Status",
            bill["payment_status"]
        )

        y -= 12 * mm

        pdf.line(
            15 * mm,
            y,
            width - 15 * mm,
            y
        )

        y -= 12 * mm

        pdf.setFont("Helvetica", 10)

        pdf.drawCentredString(
            width / 2,
            y,
            "Thank You! Get Well Soon."
        )

        pdf.save()

        return filepath

    # ========================================================
    # 9. GENERATE SELECTED RECEIPT
    # ========================================================

    def generate_selected_receipt(self):

        if not self.selected_bill_id:
            return

        try:

            filepath = self.generate_pdf(
                self.selected_bill_id
            )

            self.show_message(
                f"PDF generated: {os.path.basename(filepath)}",
                True
            )

            messagebox.showinfo(
                "Receipt Generated",
                f"Receipt saved successfully.\n\n{filepath}",
                parent=self
            )

        except (sqlite3.Error, OSError, ValueError) as error:

            self.show_message(str(error))

    # ========================================================
    # 10. ENSURE RECEIPT EXISTS
    # ========================================================

    def ensure_receipt(self):

        if not self.selected_bill_id:
            raise ValueError("Select a receipt first.")

        bill = self.get_receipt_details(
            self.selected_bill_id
        )

        if not bill:
            raise ValueError("Bill no longer exists.")

        filepath = self.get_receipt_path(
            bill["bill_number"]
        )

        if not os.path.isfile(filepath):

            filepath = self.generate_pdf(
                self.selected_bill_id
            )

        return filepath

    # ========================================================
    # 11. OPEN RECEIPT
    # ========================================================

    def open_receipt(self):

        try:

            filepath = self.ensure_receipt()

            subprocess.Popen(
                ["xdg-open", filepath],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            self.show_message(
                "Receipt opened successfully.",
                True
            )

        except (
            sqlite3.Error,
            OSError,
            ValueError
        ) as error:

            messagebox.showerror(
                "Open Receipt",
                str(error),
                parent=self
            )

    # ========================================================
    # 12. DOWNLOAD RECEIPT
    # ========================================================

    def download_receipt(self):

        try:

            source = self.ensure_receipt()

            filename = os.path.basename(source)

            destination = filedialog.asksaveasfilename(
                parent=self,
                title="Save Receipt",
                defaultextension=".pdf",
                initialfile=filename,
                filetypes=[
                    ("PDF Files", "*.pdf")
                ]
            )

            if not destination:
                return

            if os.path.abspath(source) != os.path.abspath(destination):

                shutil.copy2(
                    source,
                    destination
                )

            self.show_message(
                "Receipt saved successfully.",
                True
            )

        except (
            sqlite3.Error,
            OSError,
            ValueError
        ) as error:

            messagebox.showerror(
                "Download Error",
                str(error),
                parent=self
            )

    # ========================================================
    # 13. PRINT RECEIPT
    # ========================================================

    def print_receipt(self):

        if shutil.which("lp") is None:

            messagebox.showerror(
                "Printing Error",
                "Ubuntu printing service is not available.",
                parent=self
            )

            return

        try:

            filepath = self.ensure_receipt()

            confirm = messagebox.askyesno(
                "Print Receipt",
                "Send this receipt to the default printer?",
                parent=self
            )

            if not confirm:
                return

            result = subprocess.run(
                ["lp", filepath],
                capture_output=True,
                text=True,
                timeout=20,
                check=False
            )

            if result.returncode != 0:

                raise RuntimeError(
                    result.stderr.strip()
                    or "Unable to submit the print job."
                )

            self.show_message(
                "Receipt sent to printer.",
                True
            )

            messagebox.showinfo(
                "Printing",
                "Receipt submitted to the printer successfully.",
                parent=self
            )

        except (
            sqlite3.Error,
            OSError,
            ValueError,
            RuntimeError,
            subprocess.TimeoutExpired
        ) as error:

            messagebox.showerror(
                "Printing Error",
                str(error),
                parent=self
            )


# ============================================================
# END OF FILE
# ============================================================
