# ============================================================
# HOSPITAL RECEPTION SYSTEM
# FILE: doctor/reports.py
# PURPOSE: Hospital Reports and PDF/CSV Export
# DATABASE: SQLite3
# GUI: CustomTkinter
# OS: Ubuntu Linux
# ============================================================

import csv
import os
import sqlite3
from datetime import date, timedelta
from tkinter import filedialog, messagebox

import customtkinter as ctk

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    LongTable
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

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
    REPORTS_DIR
)

from database import fetch_all


# ============================================================
# REPORT CONFIGURATION
# ============================================================

REPORT_TYPES = [
    "Daily Patient Registration",
    "Monthly Patient Registration",
    "Patient Directory",
    "Patient Visit History",
    "Daily Revenue",
    "Monthly Revenue",
    "Consultation Fee Report",
    "Medicine Fee Report",
    "Token Management",
    "Payment Collection",
    "Outstanding Payments",
    "Doctor Consultation Report"
]


# ============================================================
# REPORTS SCREEN
# ============================================================

class ReportsScreen(ctk.CTkFrame):

    def __init__(self, parent, app):

        super().__init__(
            parent,
            fg_color=BACKGROUND_COLOR,
            corner_radius=0
        )

        self.app = app

        self.report_data = []
        self.report_columns = []

        os.makedirs(REPORTS_DIR, exist_ok=True)

        self.setup_pdf_font()
        self.create_widgets()

    # ========================================================
    # 1. PDF FONT
    # ========================================================

    def setup_pdf_font(self):

        self.pdf_font = "Helvetica"

        font_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Regular.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSans.ttf"
        ]

        for path in font_paths:

            if os.path.isfile(path):

                try:

                    pdfmetrics.registerFont(
                        TTFont("HospitalFont", path)
                    )

                    self.pdf_font = "HospitalFont"

                    break

                except Exception:
                    continue

    # ========================================================
    # 2. CREATE GUI
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

        # ----------------------------------------------------
        # HEADER
        # ----------------------------------------------------

        header = ctk.CTkFrame(
            self.container,
            fg_color="transparent"
        )

        header.pack(
            fill="x",
            pady=(0, 20)
        )

        ctk.CTkLabel(
            header,
            text="Hospital Reports",
            font=("Arial", 27, "bold"),
            text_color=TEXT_COLOR
        ).pack(side="left")

        # ----------------------------------------------------
        # REPORT FILTER CARD
        # ----------------------------------------------------

        filter_card = ctk.CTkFrame(
            self.container,
            fg_color=CARD_COLOR,
            corner_radius=10,
            border_width=1,
            border_color=BORDER_COLOR
        )

        filter_card.pack(
            fill="x",
            pady=(0, 15)
        )

        ctk.CTkLabel(
            filter_card,
            text="Generate Report",
            font=("Arial", 20, "bold"),
            text_color=TEXT_COLOR
        ).pack(
            anchor="w",
            padx=20,
            pady=(15, 15)
        )

        # ----------------------------------------------------
        # REPORT TYPE
        # ----------------------------------------------------

        ctk.CTkLabel(
            filter_card,
            text="Select Report",
            font=("Arial", 15, "bold"),
            text_color=TEXT_COLOR
        ).pack(
            anchor="w",
            padx=20,
            pady=(0, 5)
        )

        self.report_type = ctk.CTkOptionMenu(
            filter_card,
            values=REPORT_TYPES,
            width=380,
            height=42
        )

        self.report_type.pack(
            anchor="w",
            padx=20,
            pady=(0, 15)
        )

        self.report_type.set(REPORT_TYPES[0])

        # ----------------------------------------------------
        # DATE FILTER
        # ----------------------------------------------------

        date_frame = ctk.CTkFrame(
            filter_card,
            fg_color="transparent"
        )

        date_frame.pack(
            fill="x",
            padx=20,
            pady=(0, 15)
        )

        date_frame.grid_columnconfigure(0, weight=1)
        date_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            date_frame,
            text="Start Date (YYYY-MM-DD)",
            font=("Arial", 14, "bold"),
            text_color=TEXT_COLOR
        ).grid(
            row=0,
            column=0,
            sticky="w",
            pady=(0, 5)
        )

        ctk.CTkLabel(
            date_frame,
            text="End Date (YYYY-MM-DD)",
            font=("Arial", 14, "bold"),
            text_color=TEXT_COLOR
        ).grid(
            row=0,
            column=1,
            sticky="w",
            padx=(15, 0),
            pady=(0, 5)
        )

        self.start_date_entry = ctk.CTkEntry(
            date_frame,
            height=42,
            font=("Arial", 15)
        )

        self.start_date_entry.grid(
            row=1,
            column=0,
            sticky="ew"
        )

        self.end_date_entry = ctk.CTkEntry(
            date_frame,
            height=42,
            font=("Arial", 15)
        )

        self.end_date_entry.grid(
            row=1,
            column=1,
            padx=(15, 0),
            sticky="ew"
        )

        today = date.today()
        start = today - timedelta(days=29)

        self.start_date_entry.insert(
            0,
            start.isoformat()
        )

        self.end_date_entry.insert(
            0,
            today.isoformat()
        )

        # ----------------------------------------------------
        # QUICK DATE FILTERS
        # ----------------------------------------------------

        quick_frame = ctk.CTkFrame(
            filter_card,
            fg_color="transparent"
        )

        quick_frame.pack(
            fill="x",
            padx=20,
            pady=(0, 15)
        )

        periods = [
            ("Today", "today"),
            ("Last 7 Days", "7"),
            ("Last 30 Days", "30"),
            ("This Month", "month"),
            ("All Time", "all")
        ]

        for title, period in periods:

            ctk.CTkButton(
                quick_frame,
                text=title,
                width=110,
                height=35,
                fg_color="#E5E7EB",
                hover_color="#D1D5DB",
                text_color=TEXT_COLOR,
                command=lambda p=period: self.set_period(p)
            ).pack(
                side="left",
                padx=(0, 8)
            )

        # ----------------------------------------------------
        # GENERATE BUTTON
        # ----------------------------------------------------

        ctk.CTkButton(
            filter_card,
            text="Generate Report",
            width=200,
            height=45,
            font=("Arial", 16, "bold"),
            fg_color=PRIMARY_COLOR,
            hover_color=PRIMARY_HOVER_COLOR,
            command=self.generate_report
        ).pack(
            anchor="w",
            padx=20,
            pady=(0, 20)
        )

        # ----------------------------------------------------
        # REPORT SUMMARY
        # ----------------------------------------------------

        summary_card = ctk.CTkFrame(
            self.container,
            fg_color=CARD_COLOR,
            corner_radius=10,
            border_width=1,
            border_color=BORDER_COLOR
        )

        summary_card.pack(
            fill="x",
            pady=(0, 15)
        )

        self.report_name_label = ctk.CTkLabel(
            summary_card,
            text="No report generated",
            font=("Arial", 18, "bold"),
            text_color=TEXT_COLOR
        )

        self.report_name_label.pack(
            anchor="w",
            padx=20,
            pady=(15, 5)
        )

        self.record_count_label = ctk.CTkLabel(
            summary_card,
            text="Total Records: 0",
            font=("Arial", 15),
            text_color=MUTED_TEXT_COLOR
        )

        self.record_count_label.pack(
            anchor="w",
            padx=20,
            pady=(0, 15)
        )

        # ----------------------------------------------------
        # REPORT PREVIEW
        # ----------------------------------------------------

        preview_card = ctk.CTkFrame(
            self.container,
            fg_color=CARD_COLOR,
            corner_radius=10,
            border_width=1,
            border_color=BORDER_COLOR
        )

        preview_card.pack(
            fill="both",
            expand=True,
            pady=(0, 15)
        )

        ctk.CTkLabel(
            preview_card,
            text="Report Preview",
            font=("Arial", 19, "bold"),
            text_color=TEXT_COLOR
        ).pack(
            anchor="w",
            padx=20,
            pady=(15, 10)
        )

        self.preview_frame = ctk.CTkScrollableFrame(
            preview_card,
            fg_color="transparent",
            height=280
        )

        self.preview_frame.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=(0, 15)
        )

        # ----------------------------------------------------
        # DOWNLOAD BUTTONS
        # ----------------------------------------------------

        button_frame = ctk.CTkFrame(
            self.container,
            fg_color="transparent"
        )

        button_frame.pack(
            fill="x",
            pady=(0, 15)
        )

        self.pdf_button = ctk.CTkButton(
            button_frame,
            text="Download PDF",
            width=160,
            height=45,
            fg_color=PRIMARY_COLOR,
            hover_color=PRIMARY_HOVER_COLOR,
            command=self.download_pdf,
            state="disabled"
        )

        self.pdf_button.pack(
            side="left",
            padx=(0, 10)
        )

        self.csv_button = ctk.CTkButton(
            button_frame,
            text="Download CSV",
            width=160,
            height=45,
            fg_color=SUCCESS_COLOR,
            hover_color="#15803D",
            command=self.download_csv,
            state="disabled"
        )

        self.csv_button.pack(side="left")

        self.message_label = ctk.CTkLabel(
            self.container,
            text="",
            font=("Arial", 14),
            text_color=ERROR_COLOR
        )

        self.message_label.pack(
            pady=(0, 10)
        )

    # ========================================================
    # 3. DATE FILTER FUNCTIONS
    # ========================================================

    def set_period(self, period):

        today = date.today()

        if period == "today":

            start = today
            end = today

        elif period == "7":

            start = today - timedelta(days=6)
            end = today

        elif period == "30":

            start = today - timedelta(days=29)
            end = today

        elif period == "month":

            start = today.replace(day=1)
            end = today

        else:

            start = None
            end = None

        self.start_date_entry.delete(0, "end")
        self.end_date_entry.delete(0, "end")

        if start:
            self.start_date_entry.insert(
                0,
                start.isoformat()
            )

        if end:
            self.end_date_entry.insert(
                0,
                end.isoformat()
            )

    def validate_dates(self):

        start_text = self.start_date_entry.get().strip()
        end_text = self.end_date_entry.get().strip()

        if not start_text and not end_text:
            return None, None

        if not start_text or not end_text:
            raise ValueError(
                "Enter both dates or leave both empty."
            )

        try:

            start = date.fromisoformat(start_text)
            end = date.fromisoformat(end_text)

        except ValueError:

            raise ValueError(
                "Invalid date. Use YYYY-MM-DD format."
            )

        if start > end:
            raise ValueError(
                "Start date cannot be after end date."
            )

        return start.isoformat(), end.isoformat()

    # ========================================================
    # 4. REPORT QUERIES
    # ========================================================

    def get_report_query(self, report_name):

        reports = {

            # ------------------------------------------------
            # 1. DAILY PATIENT REGISTRATION
            # ------------------------------------------------

            "Daily Patient Registration": (
                """
                SELECT
                    DATE(created_at) AS registration_date,
                    COUNT(*) AS total_patients
                FROM patients
                WHERE 1 = 1
                """,
                "created_at",
                """
                GROUP BY DATE(created_at)
                ORDER BY registration_date DESC
                """
            ),

            # ------------------------------------------------
            # 2. MONTHLY PATIENT REGISTRATION
            # ------------------------------------------------

            "Monthly Patient Registration": (
                """
                SELECT
                    STRFTIME('%Y-%m', created_at) AS month,
                    COUNT(*) AS total_patients
                FROM patients
                WHERE 1 = 1
                """,
                "created_at",
                """
                GROUP BY STRFTIME('%Y-%m', created_at)
                ORDER BY month DESC
                """
            ),

            # ------------------------------------------------
            # 3. PATIENT DIRECTORY
            # ------------------------------------------------

            "Patient Directory": (
                """
                SELECT
                    p.id AS patient_id,
                    p.name,
                    p.mobile,
                    p.gender,
                    DATE(p.created_at) AS registered_on,
                    COUNT(v.id) AS total_visits
                FROM patients p
                LEFT JOIN visits v ON v.patient_id = p.id
                WHERE 1 = 1
                """,
                "p.created_at",
                """
                GROUP BY
                    p.id,
                    p.name,
                    p.mobile,
                    p.gender,
                    p.created_at
                ORDER BY p.id DESC
                """
            ),

            # ------------------------------------------------
            # 4. PATIENT VISIT HISTORY
            # ------------------------------------------------

            "Patient Visit History": (
                """
                SELECT
                    v.id AS visit_id,
                    v.visit_date,
                    v.token_number,
                    p.id AS patient_id,
                    p.name AS patient_name,
                    p.mobile,
                    v.status,
                    COALESCE(d.name, '-') AS doctor
                FROM visits v
                JOIN patients p ON p.id = v.patient_id
                LEFT JOIN doctors d ON d.id = v.doctor_id
                WHERE 1 = 1
                """,
                "v.visit_date",
                """
                ORDER BY v.visit_date DESC, v.id DESC
                """
            ),

            # ------------------------------------------------
            # 5. DAILY REVENUE
            # ------------------------------------------------

            "Daily Revenue": (
                """
                SELECT
                    DATE(paid_at) AS payment_date,
                    COUNT(*) AS transactions,
                    ROUND(SUM(amount), 2) AS revenue
                FROM payments
                WHERE 1 = 1
                """,
                "paid_at",
                """
                GROUP BY DATE(paid_at)
                ORDER BY payment_date DESC
                """
            ),

            # ------------------------------------------------
            # 6. MONTHLY REVENUE
            # ------------------------------------------------

            "Monthly Revenue": (
                """
                SELECT
                    STRFTIME('%Y-%m', paid_at) AS month,
                    COUNT(*) AS transactions,
                    ROUND(SUM(amount), 2) AS revenue
                FROM payments
                WHERE 1 = 1
                """,
                "paid_at",
                """
                GROUP BY STRFTIME('%Y-%m', paid_at)
                ORDER BY month DESC
                """
            ),

            # ------------------------------------------------
            # 7. CONSULTATION FEE REPORT
            # ------------------------------------------------

            "Consultation Fee Report": (
                """
                SELECT
                    b.bill_number,
                    DATE(b.created_at) AS bill_date,
                    p.name AS patient,
                    v.token_number,
                    b.consultation_fee,
                    b.payment_status
                FROM bills b
                JOIN visits v ON v.id = b.visit_id
                JOIN patients p ON p.id = v.patient_id
                WHERE 1 = 1
                """,
                "b.created_at",
                """
                ORDER BY b.id DESC
                """
            ),

            # ------------------------------------------------
            # 8. MEDICINE FEE REPORT
            # ------------------------------------------------

            "Medicine Fee Report": (
                """
                SELECT
                    b.bill_number,
                    DATE(b.created_at) AS bill_date,
                    p.name AS patient,
                    v.token_number,
                    b.medicine_fee,
                    b.payment_status
                FROM bills b
                JOIN visits v ON v.id = b.visit_id
                JOIN patients p ON p.id = v.patient_id
                WHERE 1 = 1
                """,
                "b.created_at",
                """
                ORDER BY b.id DESC
                """
            ),

            # ------------------------------------------------
            # 9. TOKEN MANAGEMENT
            # ------------------------------------------------

            "Token Management": (
                """
                SELECT
                    v.visit_date,
                    v.token_number,
                    p.name AS patient,
                    p.mobile,
                    v.visit_time,
                    v.status
                FROM visits v
                JOIN patients p ON p.id = v.patient_id
                WHERE 1 = 1
                """,
                "v.visit_date",
                """
                ORDER BY v.visit_date DESC,
                         v.token_sequence ASC
                """
            ),

            # ------------------------------------------------
            # 10. PAYMENT COLLECTION
            # ------------------------------------------------

            "Payment Collection": (
                """
                SELECT
                    pay.id AS payment_id,
                    DATE(pay.paid_at) AS payment_date,
                    b.bill_number,
                    p.name AS patient,
                    pay.payment_method,
                    pay.payment_reference,
                    pay.amount
                FROM payments pay
                JOIN bills b ON b.id = pay.bill_id
                JOIN visits v ON v.id = b.visit_id
                JOIN patients p ON p.id = v.patient_id
                WHERE 1 = 1
                """,
                "pay.paid_at",
                """
                ORDER BY pay.id DESC
                """
            ),

            # ------------------------------------------------
            # 11. OUTSTANDING PAYMENTS
            # ------------------------------------------------

            "Outstanding Payments": (
                """
                SELECT
                    b.bill_number,
                    DATE(b.created_at) AS bill_date,
                    p.name AS patient,
                    p.mobile,
                    b.total_amount,
                    COALESCE(
                        (
                            SELECT SUM(pay.amount)
                            FROM payments pay
                            WHERE pay.bill_id = b.id
                        ),
                        0
                    ) AS amount_paid,

                    ROUND(
                        b.total_amount -
                        COALESCE(
                            (
                                SELECT SUM(pay.amount)
                                FROM payments pay
                                WHERE pay.bill_id = b.id
                            ),
                            0
                        ),
                        2
                    ) AS balance

                FROM bills b
                JOIN visits v ON v.id = b.visit_id
                JOIN patients p ON p.id = v.patient_id
                WHERE b.total_amount >
                    COALESCE(
                        (
                            SELECT SUM(pay.amount)
                            FROM payments pay
                            WHERE pay.bill_id = b.id
                        ),
                        0
                    )
                """,
                "b.created_at",
                """
                ORDER BY b.id DESC
                """
            ),

            # ------------------------------------------------
            # 12. DOCTOR CONSULTATION REPORT
            # ------------------------------------------------

            "Doctor Consultation Report": (
                """
                SELECT
                    v.visit_date,
                    v.token_number,
                    p.name AS patient,
                    COALESCE(d.name, '-') AS doctor,
                    v.status,
                    COALESCE(b.consultation_fee, 0)
                        AS consultation_fee,
                    COALESCE(b.total_amount, 0)
                        AS total_bill
                FROM visits v
                JOIN patients p ON p.id = v.patient_id
                LEFT JOIN doctors d ON d.id = v.doctor_id
                LEFT JOIN bills b ON b.visit_id = v.id
                WHERE 1 = 1
                """,
                "v.visit_date",
                """
                ORDER BY v.visit_date DESC, v.id DESC
                """
            )
        }

        if report_name not in reports:
            raise ValueError("Invalid report type.")

        return reports[report_name]

    # ========================================================
    # 5. FETCH REPORT DATA
    # ========================================================

    def fetch_report_data(self):

        report_name = self.report_type.get()

        start_date, end_date = self.validate_dates()

        query, date_column, order_query = (
            self.get_report_query(report_name)
        )

        params = []

        if start_date:

            query += f"""
                AND DATE({date_column}) BETWEEN ? AND ?
            """

            params.extend([
                start_date,
                end_date
            ])

        query += order_query

        return fetch_all(query, tuple(params))

    # ========================================================
    # 6. GENERATE REPORT
    # ========================================================

    def generate_report(self):

        try:

            records = self.fetch_report_data()

            self.report_data = records

            if records:
                self.report_columns = list(records[0].keys())
            else:
                self.report_columns = []

            self.report_name_label.configure(
                text=self.report_type.get()
            )

            self.record_count_label.configure(
                text=f"Total Records: {len(records)}"
            )

            self.display_preview()

            state = "normal" if records else "disabled"

            self.pdf_button.configure(state=state)
            self.csv_button.configure(state=state)

            self.show_message(
                f"Report generated successfully. "
                f"{len(records)} records found.",
                True
            )

        except (
            sqlite3.Error,
            ValueError
        ) as error:

            self.report_data = []
            self.report_columns = []

            self.pdf_button.configure(state="disabled")
            self.csv_button.configure(state="disabled")

            self.show_message(str(error))

    # ========================================================
    # 7. DISPLAY REPORT PREVIEW
    # ========================================================

    def display_preview(self):

        for widget in self.preview_frame.winfo_children():
            widget.destroy()

        if not self.report_data:

            ctk.CTkLabel(
                self.preview_frame,
                text="No records found.",
                font=("Arial", 15),
                text_color=MUTED_TEXT_COLOR
            ).pack(pady=30)

            return

        for column, heading in enumerate(self.report_columns):

            self.preview_frame.grid_columnconfigure(
                column,
                weight=1
            )

            ctk.CTkLabel(
                self.preview_frame,
                text=heading.replace("_", " ").title(),
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

        # Preview first 20 records
        for row_index, record in enumerate(
            self.report_data[:20],
            start=1
        ):

            for column, key in enumerate(self.report_columns):

                value = record.get(key)

                if value is None:
                    value = "-"

                ctk.CTkLabel(
                    self.preview_frame,
                    text=str(value),
                    font=("Arial", 12),
                    text_color=TEXT_COLOR,
                    anchor="w"
                ).grid(
                    row=row_index,
                    column=column,
                    padx=8,
                    pady=6,
                    sticky="w"
                )

        if len(self.report_data) > 20:

            ctk.CTkLabel(
                self.preview_frame,
                text=(
                    f"Showing first 20 of "
                    f"{len(self.report_data)} records."
                ),
                font=("Arial", 12),
                text_color=MUTED_TEXT_COLOR
            ).grid(
                row=21,
                column=0,
                columnspan=len(self.report_columns),
                pady=15
            )

    # ========================================================
    # 8. SHOW MESSAGE
    # ========================================================

    def show_message(self, message, success=False):

        self.message_label.configure(
            text=message,
            text_color=SUCCESS_COLOR if success else ERROR_COLOR
        )

    # ========================================================
    # 9. DEFAULT REPORT FILENAME
    # ========================================================

    def get_filename(self, extension):

        report_name = self.report_type.get()

        filename = report_name.lower().replace(" ", "_")

        timestamp = date.today().strftime("%Y%m%d")

        return f"{filename}_{timestamp}.{extension}"

    # ========================================================
    # 10. DOWNLOAD CSV
    # ========================================================

    def download_csv(self):

        if not self.report_data:
            return

        filename = self.get_filename("csv")

        filepath = filedialog.asksaveasfilename(
            parent=self,
            title="Save CSV Report",
            initialdir=REPORTS_DIR,
            initialfile=filename,
            defaultextension=".csv",
            filetypes=[
                ("CSV Files", "*.csv")
            ]
        )

        if not filepath:
            return

        try:

            with open(
                filepath,
                "w",
                newline="",
                encoding="utf-8-sig"
            ) as file:

                writer = csv.DictWriter(
                    file,
                    fieldnames=self.report_columns
                )

                writer.writeheader()

                writer.writerows(self.report_data)

            self.show_message(
                "CSV report saved successfully.",
                True
            )

            messagebox.showinfo(
                "Success",
                f"Report saved successfully.\n\n{filepath}",
                parent=self
            )

        except (OSError, csv.Error) as error:

            messagebox.showerror(
                "Export Error",
                str(error),
                parent=self
            )

    # ========================================================
    # 11. DOWNLOAD PDF
    # ========================================================

    def download_pdf(self):

        if not self.report_data:
            return

        filename = self.get_filename("pdf")

        filepath = filedialog.asksaveasfilename(
            parent=self,
            title="Save PDF Report",
            initialdir=REPORTS_DIR,
            initialfile=filename,
            defaultextension=".pdf",
            filetypes=[
                ("PDF Files", "*.pdf")
            ]
        )

        if not filepath:
            return

        try:

            self.create_pdf(filepath)

            self.show_message(
                "PDF report saved successfully.",
                True
            )

            messagebox.showinfo(
                "Success",
                f"PDF report saved successfully.\n\n{filepath}",
                parent=self
            )

        except Exception as error:

            messagebox.showerror(
                "PDF Error",
                str(error),
                parent=self
            )

    # ========================================================
    # 12. GENERATE PDF DOCUMENT
    # ========================================================

    def create_pdf(self, filepath):

        document = SimpleDocTemplate(
            filepath,
            pagesize=landscape(A4),
            rightMargin=12 * mm,
            leftMargin=12 * mm,
            topMargin=15 * mm,
            bottomMargin=15 * mm
        )

        styles = getSampleStyleSheet()

        title_style = styles["Title"]
        title_style.fontName = self.pdf_font
        title_style.fontSize = 17
        title_style.leading = 22

        normal_style = styles["Normal"]
        normal_style.fontName = self.pdf_font
        normal_style.fontSize = 9

        story = []

        # Hospital name
        story.append(
            Paragraph(
                self.escape_pdf_text(HOSPITAL_NAME),
                title_style
            )
        )

        story.append(Spacer(1, 8))

        # Report heading
        story.append(
            Paragraph(
                self.escape_pdf_text(self.report_type.get()),
                title_style
            )
        )

        story.append(Spacer(1, 10))

        # Date range
        start_date = self.start_date_entry.get().strip()
        end_date = self.end_date_entry.get().strip()

        if start_date and end_date:

            date_text = (
                f"Period: {start_date} to {end_date}"
            )

        else:

            date_text = "Period: All Time"

        story.append(
            Paragraph(date_text, normal_style)
        )

        story.append(Spacer(1, 5))

        story.append(
            Paragraph(
                f"Total Records: {len(self.report_data)}",
                normal_style
            )
        )

        story.append(Spacer(1, 15))

        # ----------------------------------------------------
        # TABLE HEADERS
        # ----------------------------------------------------

        headers = [
            key.replace("_", " ").title()
            for key in self.report_columns
        ]

        table_data = [headers]

        # ----------------------------------------------------
        # TABLE RECORDS
        # ----------------------------------------------------

        for record in self.report_data:

            row = []

            for key in self.report_columns:

                value = record.get(key)

                if value is None:
                    value = "-"

                row.append(str(value))

            table_data.append(row)

        # ----------------------------------------------------
        # TABLE WIDTHS
        # ----------------------------------------------------

        available_width = (
            landscape(A4)[0] - 24 * mm
        )

        column_count = len(headers)

        column_width = available_width / column_count

        # Wrap values to avoid clipping long names.
        cell_style = styles["BodyText"].clone("HospitalCell")
        cell_style.fontName = self.pdf_font
        cell_style.fontSize = 7
        cell_style.leading = 10

        formatted_data = []

        for row in table_data:

            formatted_row = []

            for value in row:

                formatted_row.append(
                    Paragraph(
                        self.escape_pdf_text(value),
                        cell_style
                    )
                )

            formatted_data.append(formatted_row)

        table = LongTable(
            formatted_data,
            colWidths=[column_width] * column_count,
            repeatRows=1,
            hAlign="LEFT"
        )

        table.setStyle(
            TableStyle([
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor(PRIMARY_COLOR)
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.white
                ),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [
                        colors.white,
                        colors.HexColor("#F3F4F6")
                    ]
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.3,
                    colors.HexColor(BORDER_COLOR)
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP"
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    5
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    5
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    6
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    6
                )
            ])
        )

        story.append(table)

        story.append(Spacer(1, 15))

        story.append(
            Paragraph(
                "Generated by Hospital Reception System",
                normal_style
            )
        )

        document.build(story)

    # ========================================================
    # 13. ESCAPE PDF TEXT
    # ========================================================

    @staticmethod
    def escape_pdf_text(value):

        value = str(value)

        value = value.replace("&", "&amp;")
        value = value.replace("<", "&lt;")
        value = value.replace(">", "&gt;")

        return value


# ============================================================
# END OF FILE
# ============================================================
