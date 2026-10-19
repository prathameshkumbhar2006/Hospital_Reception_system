# ============================================================
# HOSPITAL RECEPTION SYSTEM
# FILE: services/receipt_service.py
# PURPOSE: Generate, Save, Download, Open and Print Receipts
# DATABASE: SQLite3
# PDF: ReportLab
# OS: Ubuntu Linux
# ============================================================

import os
import re
import shutil
import subprocess
from datetime import datetime
from decimal import Decimal
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A5
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    KeepTogether
)

from config import (
    HOSPITAL_NAME,
    HOSPITAL_ADDRESS,
    HOSPITAL_PHONE,
    HOSPITAL_EMAIL,
    RECEIPT_FOOTER,
    RECEIPTS_DIR,
    PRIMARY_COLOR
)

from models.billing_model import BillingModel


# ============================================================
# RECEIPT SERVICE
# ============================================================

class ReceiptService:

    # ========================================================
    # 1. CONFIGURATION
    # ========================================================

    RECEIPT_WIDTH, RECEIPT_HEIGHT = A5

    FONT_NAME = "Helvetica"
    FONT_BOLD = "Helvetica-Bold"

    # ========================================================
    # 2. CREATE RECEIPT DIRECTORY
    # ========================================================

    @staticmethod
    def create_directory():

        os.makedirs(
            RECEIPTS_DIR,
            exist_ok=True
        )

        return RECEIPTS_DIR

    # ========================================================
    # 3. REGISTER PDF FONT
    # ========================================================

    @classmethod
    def setup_fonts(cls):

        font_paths = [
            (
                "/usr/share/fonts/truetype/dejavu/"
                "DejaVuSans.ttf"
            ),
            (
                "/usr/share/fonts/truetype/freefont/"
                "FreeSans.ttf"
            )
        ]

        bold_paths = [
            (
                "/usr/share/fonts/truetype/dejavu/"
                "DejaVuSans-Bold.ttf"
            ),
            (
                "/usr/share/fonts/truetype/freefont/"
                "FreeSansBold.ttf"
            )
        ]

        regular_font = next(
            (
                path for path in font_paths
                if os.path.isfile(path)
            ),
            None
        )

        bold_font = next(
            (
                path for path in bold_paths
                if os.path.isfile(path)
            ),
            None
        )

        if regular_font:

            try:

                if "HospitalReceipt" not in pdfmetrics.getRegisteredFontNames():

                    pdfmetrics.registerFont(
                        TTFont(
                            "HospitalReceipt",
                            regular_font
                        )
                    )

                cls.FONT_NAME = "HospitalReceipt"

                if bold_font:

                    if (
                        "HospitalReceiptBold"
                        not in pdfmetrics.getRegisteredFontNames()
                    ):

                        pdfmetrics.registerFont(
                            TTFont(
                                "HospitalReceiptBold",
                                bold_font
                            )
                        )

                    cls.FONT_BOLD = "HospitalReceiptBold"

                else:

                    cls.FONT_BOLD = cls.FONT_NAME

            except Exception as error:

                print("Receipt font warning:", error)

                cls.FONT_NAME = "Helvetica"
                cls.FONT_BOLD = "Helvetica-Bold"

        return cls.FONT_NAME

    # ========================================================
    # 4. FORMAT CURRENCY
    # ========================================================

    @staticmethod
    def format_currency(amount):

        value = Decimal(str(amount or 0))

        return f"INR {value:,.2f}"

    # ========================================================
    # 5. SAFE TEXT
    # ========================================================

    @staticmethod
    def safe_text(value):

        if value is None:
            return "-"

        return escape(str(value))

    # ========================================================
    # 6. VALIDATE BILL NUMBER
    # ========================================================

    @staticmethod
    def validate_bill_number(bill_number):

        bill_number = str(bill_number).strip()

        if not bill_number:

            raise ValueError(
                "Bill number is required."
            )

        if not re.fullmatch(
            r"[A-Za-z0-9_-]{1,80}",
            bill_number
        ):

            raise ValueError(
                "Invalid bill number."
            )

        return bill_number

    # ========================================================
    # 7. GET RECEIPT FILE PATH
    # ========================================================

    @classmethod
    def get_receipt_path(cls, bill_number):

        cls.create_directory()

        bill_number = cls.validate_bill_number(
            bill_number
        )

        filename = f"{bill_number}.pdf"

        return os.path.join(
            RECEIPTS_DIR,
            filename
        )

    # ========================================================
    # 8. GET RECEIPT DETAILS
    # ========================================================

    @staticmethod
    def get_receipt_details(bill_id):

        receipt = BillingModel.get_receipt_details(
            bill_id
        )

        if not receipt:

            raise ValueError(
                "Bill not found."
            )

        return receipt

    # ========================================================
    # 9. GET RECEIPT BY BILL NUMBER
    # ========================================================

    @classmethod
    def get_receipt_by_number(cls, bill_number):

        bill = BillingModel.get_by_number(
            bill_number
        )

        if not bill:

            raise ValueError(
                "Bill not found."
            )

        return cls.get_receipt_details(
            bill["id"]
        )

    # ========================================================
    # 10. CREATE PDF STYLES
    # ========================================================

    @classmethod
    def get_styles(cls):

        cls.setup_fonts()

        styles = {}

        styles["hospital"] = ParagraphStyle(
            name="ReceiptHospital",
            fontName=cls.FONT_BOLD,
            fontSize=16,
            leading=21,
            alignment=TA_CENTER,
            textColor=colors.HexColor(
                PRIMARY_COLOR
            ),
            spaceAfter=8
        )

        styles["subtitle"] = ParagraphStyle(
            name="ReceiptSubtitle",
            fontName=cls.FONT_BOLD,
            fontSize=11,
            leading=15,
            alignment=TA_CENTER,
            textColor=colors.HexColor(
                "#1F2937"
            ),
            spaceAfter=5
        )

        styles["center"] = ParagraphStyle(
            name="ReceiptCenter",
            fontName=cls.FONT_NAME,
            fontSize=8,
            leading=12,
            alignment=TA_CENTER,
            textColor=colors.HexColor(
                "#374151"
            )
        )

        styles["label"] = ParagraphStyle(
            name="ReceiptLabel",
            fontName=cls.FONT_NAME,
            fontSize=9,
            leading=14,
            alignment=TA_LEFT,
            textColor=colors.HexColor(
                "#374151"
            )
        )

        styles["value"] = ParagraphStyle(
            name="ReceiptValue",
            fontName=cls.FONT_NAME,
            fontSize=9,
            leading=14,
            alignment=TA_RIGHT,
            textColor=colors.HexColor(
                "#111827"
            )
        )

        styles["bold_label"] = ParagraphStyle(
            name="ReceiptBoldLabel",
            fontName=cls.FONT_BOLD,
            fontSize=10,
            leading=15,
            alignment=TA_LEFT,
            textColor=colors.HexColor(
                "#111827"
            )
        )

        styles["bold_value"] = ParagraphStyle(
            name="ReceiptBoldValue",
            fontName=cls.FONT_BOLD,
            fontSize=10,
            leading=15,
            alignment=TA_RIGHT,
            textColor=colors.HexColor(
                "#111827"
            )
        )

        styles["footer"] = ParagraphStyle(
            name="ReceiptFooter",
            fontName=cls.FONT_NAME,
            fontSize=9,
            leading=13,
            alignment=TA_CENTER,
            textColor=colors.HexColor(
                "#6B7280"
            )
        )

        return styles

    # ========================================================
    # 11. CREATE PDF DETAIL ROW
    # ========================================================

    @classmethod
    def create_detail_row(
        cls,
        label,
        value,
        styles,
        bold=False
    ):

        label_style = (
            styles["bold_label"]
            if bold else styles["label"]
        )

        value_style = (
            styles["bold_value"]
            if bold else styles["value"]
        )

        return [
            Paragraph(
                cls.safe_text(label),
                label_style
            ),
            Paragraph(
                cls.safe_text(value),
                value_style
            )
        ]

    # ========================================================
    # 12. CREATE PDF TABLE
    # ========================================================

    @classmethod
    def create_table(
        cls,
        rows,
        column_widths,
        header=False
    ):

        table = Table(
            rows,
            colWidths=column_widths,
            hAlign="CENTER"
        )

        commands = [
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
                5
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                5
            ),
            (
                "LINEBELOW",
                (0, -1),
                (-1, -1),
                0.5,
                colors.HexColor(
                    "#D1D5DB"
                )
            )
        ]

        if header:

            commands.extend([
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor(
                        "#EFF6FF"
                    )
                ),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.HexColor(
                        "#D1D5DB"
                    )
                )
            ])

        table.setStyle(
            TableStyle(commands)
        )

        return table

    # ========================================================
    # 13. GENERATE PDF RECEIPT
    # ========================================================

    @classmethod
    def generate_receipt(cls, bill_id):

        receipt = cls.get_receipt_details(
            bill_id
        )

        cls.create_directory()

        filepath = cls.get_receipt_path(
            receipt["bill_number"]
        )

        styles = cls.get_styles()

        document = SimpleDocTemplate(
            filepath,
            pagesize=A5,
            rightMargin=13 * mm,
            leftMargin=13 * mm,
            topMargin=15 * mm,
            bottomMargin=15 * mm,
            title=(
                f"Receipt {receipt['bill_number']}"
            ),
            author=HOSPITAL_NAME
        )

        story = []

        page_width = A5[0] - 26 * mm

        column_widths = [
            page_width * 0.43,
            page_width * 0.57
        ]

        # ----------------------------------------------------
        # HOSPITAL HEADER
        # ----------------------------------------------------

        story.append(
            Paragraph(
                cls.safe_text(
                    HOSPITAL_NAME
                ),
                styles["hospital"]
            )
        )

        if HOSPITAL_ADDRESS:

            story.append(
                Paragraph(
                    cls.safe_text(
                        HOSPITAL_ADDRESS
                    ),
                    styles["center"]
                )
            )

        if HOSPITAL_PHONE:

            story.append(
                Paragraph(
                    "Phone: "
                    + cls.safe_text(
                        HOSPITAL_PHONE
                    ),
                    styles["center"]
                )
            )

        if HOSPITAL_EMAIL:

            story.append(
                Paragraph(
                    cls.safe_text(
                        HOSPITAL_EMAIL
                    ),
                    styles["center"]
                )
            )

        story.append(
            Spacer(1, 9 * mm)
        )

        story.append(
            Paragraph(
                "PAYMENT RECEIPT",
                styles["subtitle"]
            )
        )

        story.append(
            Spacer(1, 4 * mm)
        )

        # ----------------------------------------------------
        # RECEIPT INFORMATION
        # ----------------------------------------------------

        receipt_rows = [
            cls.create_detail_row(
                "Receipt Number",
                receipt["bill_number"],
                styles
            ),
            cls.create_detail_row(
                "Bill Date",
                str(
                    receipt["created_at"]
                )[:10],
                styles
            ),
            cls.create_detail_row(
                "Patient ID",
                receipt["patient_id"],
                styles
            ),
            cls.create_detail_row(
                "Patient Name",
                receipt["patient_name"],
                styles
            ),
            cls.create_detail_row(
                "Mobile Number",
                receipt["mobile"],
                styles
            ),
            cls.create_detail_row(
                "Token Number",
                receipt["token_number"],
                styles
            ),
            cls.create_detail_row(
                "Visit Date",
                receipt["visit_date"],
                styles
            )
        ]

        if receipt.get("doctor_name"):

            receipt_rows.append(
                cls.create_detail_row(
                    "Doctor",
                    receipt["doctor_name"],
                    styles
                )
            )

        story.append(
            cls.create_table(
                receipt_rows,
                column_widths
            )
        )

        story.append(
            Spacer(1, 7 * mm)
        )

        # ----------------------------------------------------
        # BILL AMOUNTS
        # ----------------------------------------------------

        amount_rows = [
            cls.create_detail_row(
                "Consultation Fee",
                cls.format_currency(
                    receipt["consultation_fee"]
                ),
                styles
            ),
            cls.create_detail_row(
                "Medicine Fee",
                cls.format_currency(
                    receipt["medicine_fee"]
                ),
                styles
            ),
            cls.create_detail_row(
                "Other Charges",
                cls.format_currency(
                    receipt["other_charges"]
                ),
                styles
            ),
            cls.create_detail_row(
                "Total Amount",
                cls.format_currency(
                    receipt["total_amount"]
                ),
                styles,
                bold=True
            )
        ]

        story.append(
            cls.create_table(
                amount_rows,
                column_widths,
                header=True
            )
        )

        story.append(
            Spacer(1, 7 * mm)
        )

        # ----------------------------------------------------
        # PAYMENT INFORMATION
        # ----------------------------------------------------

        amount_paid = Decimal(
            str(
                receipt.get(
                    "amount_paid",
                    0
                )
            )
        )

        total_amount = Decimal(
            str(
                receipt["total_amount"]
            )
        )

        balance = max(
            Decimal("0.00"),
            total_amount - amount_paid
        )

        payment_rows = [
            cls.create_detail_row(
                "Amount Received",
                cls.format_currency(
                    amount_paid
                ),
                styles
            ),
            cls.create_detail_row(
                "Balance Due",
                cls.format_currency(
                    balance
                ),
                styles,
                bold=True
            ),
            cls.create_detail_row(
                "Payment Status",
                receipt["payment_status"],
                styles
            )
        ]

        story.append(
            cls.create_table(
                payment_rows,
                column_widths
            )
        )

        # ----------------------------------------------------
        # PAYMENT TRANSACTIONS
        # ----------------------------------------------------

        payments = receipt.get(
            "payments",
            []
        )

        if payments:

            story.append(
                Spacer(1, 7 * mm)
            )

            story.append(
                Paragraph(
                    "PAYMENT HISTORY",
                    styles["subtitle"]
                )
            )

            payment_history_rows = []

            for payment in payments:

                payment_date = str(
                    payment["paid_at"]
                )[:16]

                description = (
                    f"{payment_date}<br/>"
                    f"{cls.safe_text(payment['payment_method'])}"
                )

                if payment.get("payment_reference"):

                    description += (
                        "<br/>Ref: "
                        + cls.safe_text(
                            payment["payment_reference"]
                        )
                    )

                payment_history_rows.append([
                    Paragraph(
                        description,
                        styles["label"]
                    ),
                    Paragraph(
                        cls.format_currency(
                            payment["amount"]
                        ),
                        styles["value"]
                    )
                ])

            story.append(
                cls.create_table(
                    payment_history_rows,
                    column_widths
                )
            )

        # ----------------------------------------------------
        # FOOTER
        # ----------------------------------------------------

        footer_content = [
            Spacer(1, 10 * mm),
            Paragraph(
                cls.safe_text(
                    RECEIPT_FOOTER
                ),
                styles["footer"]
            ),
            Spacer(1, 3 * mm),
            Paragraph(
                "Computer-generated receipt",
                styles["footer"]
            )
        ]

        story.append(
            KeepTogether(
                footer_content
            )
        )

        # ----------------------------------------------------
        # CREATE DOCUMENT
        # ----------------------------------------------------

        document.build(story)

        if not os.path.isfile(filepath):

            raise OSError(
                "Receipt PDF could not be created."
            )

        return filepath

    # ========================================================
    # 14. GENERATE RECEIPT BY BILL NUMBER
    # ========================================================

    @classmethod
    def generate_by_number(cls, bill_number):

        bill = BillingModel.get_by_number(
            bill_number
        )

        if not bill:

            raise ValueError(
                "Bill not found."
            )

        return cls.generate_receipt(
            bill["id"]
        )

    # ========================================================
    # 15. GENERATE RECEIPT BY VISIT
    # ========================================================

    @classmethod
    def generate_by_visit(cls, visit_id):

        bill = BillingModel.get_by_visit(
            visit_id
        )

        if not bill:

            raise ValueError(
                "No bill found for this visit."
            )

        return cls.generate_receipt(
            bill["id"]
        )

    # ========================================================
    # 16. CHECK RECEIPT EXISTS
    # ========================================================

    @classmethod
    def receipt_exists(cls, bill_id):

        bill = BillingModel.get_by_id(
            bill_id
        )

        if not bill:
            return False

        filepath = cls.get_receipt_path(
            bill["bill_number"]
        )

        return os.path.isfile(filepath)

    # ========================================================
    # 17. ENSURE LATEST RECEIPT
    # ========================================================

    @classmethod
    def ensure_receipt(cls, bill_id):

        # Regenerate to include the latest payments.
        return cls.generate_receipt(
            bill_id
        )

    # ========================================================
    # 18. OPEN PDF RECEIPT
    # ========================================================

    @classmethod
    def open_receipt(cls, bill_id):

        filepath = cls.ensure_receipt(
            bill_id
        )

        if shutil.which("xdg-open") is None:

            raise RuntimeError(
                "PDF viewer command xdg-open is not installed."
            )

        subprocess.Popen(
            ["xdg-open", filepath],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        return filepath

    # ========================================================
    # 19. DOWNLOAD RECEIPT
    # ========================================================

    @classmethod
    def download_receipt(
        cls,
        bill_id,
        destination_path
    ):

        if not destination_path:

            raise ValueError(
                "Destination path is required."
            )

        source_path = cls.ensure_receipt(
            bill_id
        )

        destination_path = os.path.abspath(
            os.path.expanduser(
                str(destination_path)
            )
        )

        if os.path.isdir(destination_path):

            destination_path = os.path.join(
                destination_path,
                os.path.basename(
                    source_path
                )
            )

        if not destination_path.lower().endswith(".pdf"):

            destination_path += ".pdf"

        destination_directory = os.path.dirname(
            destination_path
        )

        os.makedirs(
            destination_directory,
            exist_ok=True
        )

        if (
            os.path.abspath(source_path)
            != os.path.abspath(destination_path)
        ):

            shutil.copy2(
                source_path,
                destination_path
            )

        return destination_path

    # ========================================================
    # 20. PRINT RECEIPT
    # ========================================================

    @classmethod
    def print_receipt(
        cls,
        bill_id,
        printer_name=None
    ):

        filepath = cls.ensure_receipt(
            bill_id
        )

        if shutil.which("lp") is None:

            raise RuntimeError(
                "Ubuntu printing command 'lp' is unavailable. "
                "Install and configure CUPS printing."
            )

        command = ["lp"]

        if printer_name:

            command.extend([
                "-d",
                str(printer_name)
            ])

        command.append(filepath)

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=30,
            check=False
        )

        if result.returncode != 0:

            raise RuntimeError(
                result.stderr.strip()
                or "Unable to submit the print job."
            )

        return {
            "success": True,
            "message": "Receipt sent to printer.",
            "filepath": filepath,
            "printer": printer_name or "Default",
            "print_output": result.stdout.strip()
        }

    # ========================================================
    # 21. GET AVAILABLE PRINTERS
    # ========================================================

    @staticmethod
    def get_available_printers():

        if shutil.which("lpstat") is None:
            return []

        try:

            result = subprocess.run(
                ["lpstat", "-p"],
                capture_output=True,
                text=True,
                timeout=10,
                check=False
            )

            if result.returncode != 0:
                return []

            printers = []

            for line in result.stdout.splitlines():

                if line.startswith("printer "):

                    parts = line.split()

                    if len(parts) >= 2:

                        printers.append(
                            parts[1]
                        )

            return printers

        except (
            OSError,
            subprocess.TimeoutExpired
        ):

            return []

    # ========================================================
    # 22. GET DEFAULT PRINTER
    # ========================================================

    @staticmethod
    def get_default_printer():

        if shutil.which("lpstat") is None:
            return None

        try:

            result = subprocess.run(
                ["lpstat", "-d"],
                capture_output=True,
                text=True,
                timeout=10,
                check=False
            )

            if result.returncode != 0:
                return None

            output = result.stdout.strip()

            prefix = "system default destination:"

            if output.startswith(prefix):

                return output[len(prefix):].strip()

            return None

        except (
            OSError,
            subprocess.TimeoutExpired
        ):

            return None

    # ========================================================
    # 23. LIST GENERATED RECEIPTS
    # ========================================================

    @classmethod
    def list_receipts(cls):

        cls.create_directory()

        receipts = []

        for filename in os.listdir(
            RECEIPTS_DIR
        ):

            if not filename.lower().endswith(".pdf"):
                continue

            filepath = os.path.join(
                RECEIPTS_DIR,
                filename
            )

            if not os.path.isfile(filepath):
                continue

            file_info = os.stat(
                filepath
            )

            receipts.append({
                "filename": filename,
                "filepath": filepath,
                "file_size": file_info.st_size,
                "modified_at": datetime.fromtimestamp(
                    file_info.st_mtime
                ).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            })

        receipts.sort(
            key=lambda item: item["modified_at"],
            reverse=True
        )

        return receipts

    # ========================================================
    # 24. GET RECEIPT SUMMARY
    # ========================================================

    @classmethod
    def get_receipt_summary(cls, bill_id):

        receipt = cls.get_receipt_details(
            bill_id
        )

        total_amount = Decimal(
            str(
                receipt["total_amount"]
            )
        )

        amount_paid = Decimal(
            str(
                receipt.get(
                    "amount_paid",
                    0
                )
            )
        )

        balance = max(
            Decimal("0.00"),
            total_amount - amount_paid
        )

        return {
            "bill_id": receipt["id"],
            "bill_number": receipt["bill_number"],
            "visit_id": receipt["visit_id"],
            "patient_id": receipt["patient_id"],
            "patient_name": receipt["patient_name"],
            "mobile": receipt["mobile"],
            "token_number": receipt["token_number"],
            "visit_date": receipt["visit_date"],
            "doctor_name": receipt.get("doctor_name"),
            "consultation_fee": float(
                receipt["consultation_fee"]
            ),
            "medicine_fee": float(
                receipt["medicine_fee"]
            ),
            "other_charges": float(
                receipt["other_charges"]
            ),
            "total_amount": float(
                total_amount
            ),
            "amount_paid": float(
                amount_paid
            ),
            "balance": float(
                balance
            ),
            "payment_status": receipt["payment_status"],
            "payments": receipt.get("payments", []),
            "created_at": receipt["created_at"],
            "filepath": cls.get_receipt_path(
                receipt["bill_number"]
            )
        }


# ============================================================
# END OF FILE
# ============================================================
