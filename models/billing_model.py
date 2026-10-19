# ============================================================
# HOSPITAL RECEPTION SYSTEM
# FILE: models/billing_model.py
# PURPOSE: Billing and Payment Database Operations
# DATABASE: SQLite3
# ============================================================

import sqlite3
from datetime import date, datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from database import (
    get_connection,
    fetch_one,
    fetch_all
)


class BillingModel:

    PAYMENT_METHODS = ("Cash", "UPI", "Card")
    PAYMENT_STATUSES = ("Paid", "Unpaid", "Partial")

    MAX_AMOUNT = Decimal("99999999.99")
    ZERO = Decimal("0.00")

    # ========================================================
    # 1. AMOUNT VALIDATION
    # ========================================================

    @staticmethod
    def validate_amount(amount):

        try:
            value = Decimal(str(amount).strip())

            if not value.is_finite():
                raise ValueError("Amount must be finite.")

            if value < 0:
                raise ValueError("Amount cannot be negative.")

            if value > BillingModel.MAX_AMOUNT:
                raise ValueError("Amount exceeds the allowed limit.")

            rounded = value.quantize(
                Decimal("0.01"),
                rounding=ROUND_HALF_UP
            )

            if rounded != value:
                raise ValueError(
                    "Amount cannot have more than two decimal places."
                )

            return rounded

        except (InvalidOperation, TypeError):
            raise ValueError("Invalid amount.")

    # ========================================================
    # 2. CALCULATE BILL TOTAL
    # ========================================================

    @staticmethod
    def calculate_total(
        consultation_fee=0,
        medicine_fee=0,
        other_charges=0
    ):

        consultation = BillingModel.validate_amount(
            consultation_fee
        )

        medicine = BillingModel.validate_amount(
            medicine_fee
        )

        other = BillingModel.validate_amount(
            other_charges
        )

        total = consultation + medicine + other

        if total > BillingModel.MAX_AMOUNT:
            raise ValueError("Total amount exceeds the allowed limit.")

        return total

    # ========================================================
    # 3. FORMAT CURRENCY
    # ========================================================

    @staticmethod
    def format_currency(amount):

        value = BillingModel.validate_amount(amount)

        return f"₹{value:,.2f}"

    # ========================================================
    # 4. GET BILL BY ID
    # ========================================================

    @staticmethod
    def get_by_id(bill_id):

        return fetch_one(
            """
            SELECT
                b.*,
                v.patient_id,
                v.doctor_id,
                v.token_number,
                v.visit_date,
                v.visit_time,
                v.status AS visit_status,
                p.name AS patient_name,
                p.mobile,
                p.gender,
                d.name AS doctor_name
            FROM bills b
            JOIN visits v ON v.id = b.visit_id
            JOIN patients p ON p.id = v.patient_id
            LEFT JOIN doctors d ON d.id = v.doctor_id
            WHERE b.id = ?
            LIMIT 1
            """,
            (bill_id,)
        )

    # ========================================================
    # 5. GET BILL BY NUMBER
    # ========================================================

    @staticmethod
    def get_by_number(bill_number):

        result = fetch_one(
            """
            SELECT id
            FROM bills
            WHERE bill_number = ?
            LIMIT 1
            """,
            (str(bill_number).strip(),)
        )

        if not result:
            return None

        return BillingModel.get_by_id(result["id"])

    # ========================================================
    # 6. GET BILL BY VISIT
    # ========================================================

    @staticmethod
    def get_by_visit(visit_id):

        result = fetch_one(
            """
            SELECT id
            FROM bills
            WHERE visit_id = ?
            LIMIT 1
            """,
            (visit_id,)
        )

        if not result:
            return None

        return BillingModel.get_by_id(result["id"])

    # ========================================================
    # 7. CREATE BILL
    # ========================================================

    @staticmethod
    def create_bill(
        visit_id,
        consultation_fee=0,
        medicine_fee=0,
        other_charges=0,
        payment_method="Cash",
        payment_status="Unpaid",
        amount_paid=0,
        payment_reference=None,
        doctor_id=None
    ):

        consultation = BillingModel.validate_amount(
            consultation_fee
        )

        medicine = BillingModel.validate_amount(
            medicine_fee
        )

        other = BillingModel.validate_amount(
            other_charges
        )

        total = BillingModel.calculate_total(
            consultation,
            medicine,
            other
        )

        amount_paid = BillingModel.validate_amount(
            amount_paid
        )

        if payment_method not in BillingModel.PAYMENT_METHODS:
            raise ValueError("Invalid payment method.")

        if payment_status not in BillingModel.PAYMENT_STATUSES:
            raise ValueError("Invalid payment status.")

        if payment_status == "Unpaid":
            if amount_paid != BillingModel.ZERO:
                raise ValueError(
                    "Unpaid bills cannot contain a payment."
                )

        elif payment_status == "Paid":
            if amount_paid != total:
                raise ValueError(
                    "Paid amount must equal the total bill."
                )

        elif payment_status == "Partial":
            if not BillingModel.ZERO < amount_paid < total:
                raise ValueError(
                    "Partial payment must be greater than zero "
                    "and less than the total bill."
                )

        connection = get_connection()

        try:
            connection.execute("BEGIN IMMEDIATE")

            visit = connection.execute(
                """
                SELECT id, status, doctor_id
                FROM visits
                WHERE id = ?
                LIMIT 1
                """,
                (visit_id,)
            ).fetchone()

            if not visit:
                raise ValueError("Patient visit not found.")

            if visit["status"] != "In Progress":
                raise ValueError(
                    "Consultation must be In Progress before billing."
                )

            if doctor_id is not None:
                if visit["doctor_id"] != int(doctor_id):
                    raise ValueError(
                        "This consultation belongs to another doctor."
                    )

            existing = connection.execute(
                """
                SELECT id
                FROM bills
                WHERE visit_id = ?
                LIMIT 1
                """,
                (visit_id,)
            ).fetchone()

            if existing:
                raise ValueError(
                    "A bill already exists for this visit."
                )

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
                    visit_id,
                    float(consultation),
                    float(medicine),
                    float(other),
                    float(total),
                    payment_method if amount_paid > 0 else None,
                    payment_status
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
                        payment_method,
                        str(payment_reference).strip()
                        if payment_reference else None,
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    )
                )

            connection.execute(
                """
                UPDATE visits
                SET status = 'Completed',
                    completed_at = ?
                WHERE id = ?
                  AND status = 'In Progress'
                """,
                (
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    visit_id
                )
            )

            connection.commit()

            return BillingModel.get_by_id(bill_id)

        except Exception:
            connection.rollback()
            raise

        finally:
            connection.close()

    # ========================================================
    # 8. GET ALL BILLS
    # ========================================================

    @staticmethod
    def get_all(
        start_date=None,
        end_date=None,
        payment_status=None,
        limit=None
    ):

        query = """
            SELECT
                b.id,
                b.bill_number,
                b.visit_id,
                b.consultation_fee,
                b.medicine_fee,
                b.other_charges,
                b.total_amount,
                b.payment_method,
                b.payment_status,
                b.created_at,
                v.token_number,
                v.visit_date,
                p.id AS patient_id,
                p.name AS patient_name,
                p.mobile,
                COALESCE(
                    (
                        SELECT SUM(pay.amount)
                        FROM payments pay
                        WHERE pay.bill_id = b.id
                    ),
                    0
                ) AS amount_paid
            FROM bills b
            JOIN visits v ON v.id = b.visit_id
            JOIN patients p ON p.id = v.patient_id
            WHERE 1 = 1
        """

        params = []

        if start_date:
            query += " AND DATE(b.created_at) >= ?"
            params.append(str(start_date))

        if end_date:
            query += " AND DATE(b.created_at) <= ?"
            params.append(str(end_date))

        if payment_status:
            if payment_status not in BillingModel.PAYMENT_STATUSES:
                raise ValueError("Invalid payment status.")

            query += " AND b.payment_status = ?"
            params.append(payment_status)

        query += " ORDER BY b.id DESC"

        if limit is not None:
            limit = int(limit)

            if limit < 1:
                raise ValueError("Limit must be positive.")

            query += " LIMIT ?"
            params.append(limit)

        return fetch_all(query, tuple(params))

    # ========================================================
    # 9. SEARCH BILLS
    # ========================================================

    @staticmethod
    def search(search_text):

        search_text = str(search_text).strip()

        if not search_text:
            return BillingModel.get_all()

        pattern = f"%{search_text}%"

        return fetch_all(
            """
            SELECT
                b.id,
                b.bill_number,
                b.visit_id,
                b.total_amount,
                b.payment_status,
                b.created_at,
                v.token_number,
                v.visit_date,
                p.name AS patient_name,
                p.mobile,
                COALESCE(
                    (
                        SELECT SUM(pay.amount)
                        FROM payments pay
                        WHERE pay.bill_id = b.id
                    ),
                    0
                ) AS amount_paid
            FROM bills b
            JOIN visits v ON v.id = b.visit_id
            JOIN patients p ON p.id = v.patient_id
            WHERE b.bill_number LIKE ?
               OR v.token_number LIKE ?
               OR p.name LIKE ?
               OR p.mobile LIKE ?
            ORDER BY b.id DESC
            """,
            (pattern, pattern, pattern, pattern)
        )

    # ========================================================
    # 10. GET BILL PAYMENTS
    # ========================================================

    @staticmethod
    def get_payments(bill_id):

        return fetch_all(
            """
            SELECT
                id,
                bill_id,
                amount,
                payment_method,
                payment_reference,
                paid_at
            FROM payments
            WHERE bill_id = ?
            ORDER BY paid_at ASC, id ASC
            """,
            (bill_id,)
        )

    # ========================================================
    # 11. GET AMOUNT PAID
    # ========================================================

    @staticmethod
    def get_amount_paid(bill_id):

        result = fetch_one(
            """
            SELECT COALESCE(SUM(amount), 0) AS total
            FROM payments
            WHERE bill_id = ?
            """,
            (bill_id,)
        )

        return Decimal(str(result["total"] or 0)).quantize(
            Decimal("0.01")
        )

    # ========================================================
    # 12. GET OUTSTANDING BALANCE
    # ========================================================

    @staticmethod
    def get_balance(bill_id):

        bill = BillingModel.get_by_id(bill_id)

        if not bill:
            raise ValueError("Bill not found.")

        total = Decimal(str(bill["total_amount"]))

        paid = BillingModel.get_amount_paid(bill_id)

        return max(
            BillingModel.ZERO,
            (total - paid).quantize(Decimal("0.01"))
        )

    # ========================================================
    # 13. RECORD PAYMENT
    # ========================================================

    @staticmethod
    def record_payment(
        bill_id,
        amount,
        payment_method="Cash",
        payment_reference=None
    ):

        amount = BillingModel.validate_amount(amount)

        if amount <= 0:
            raise ValueError("Payment amount must be greater than zero.")

        if payment_method not in BillingModel.PAYMENT_METHODS:
            raise ValueError("Invalid payment method.")

        connection = get_connection()

        try:
            connection.execute("BEGIN IMMEDIATE")

            bill = connection.execute(
                """
                SELECT id, total_amount
                FROM bills
                WHERE id = ?
                LIMIT 1
                """,
                (bill_id,)
            ).fetchone()

            if not bill:
                raise ValueError("Bill not found.")

            result = connection.execute(
                """
                SELECT COALESCE(SUM(amount), 0) AS total
                FROM payments
                WHERE bill_id = ?
                """,
                (bill_id,)
            ).fetchone()

            paid = Decimal(str(result["total"] or 0))

            total = Decimal(str(bill["total_amount"]))

            balance = (total - paid).quantize(
                Decimal("0.01"),
                rounding=ROUND_HALF_UP
            )

            if balance <= 0:
                raise ValueError("This bill is already fully paid.")

            if amount > balance:
                raise ValueError(
                    "Payment cannot exceed the outstanding balance."
                )

            cursor = connection.execute(
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
                    float(amount),
                    payment_method,
                    str(payment_reference).strip()
                    if payment_reference else None,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                )
            )

            payment_id = cursor.lastrowid

            new_paid = paid + amount

            if new_paid >= total:
                new_status = "Paid"
            elif new_paid > 0:
                new_status = "Partial"
            else:
                new_status = "Unpaid"

            connection.execute(
                """
                UPDATE bills
                SET payment_status = ?,
                    payment_method = ?
                WHERE id = ?
                """,
                (
                    new_status,
                    payment_method,
                    bill_id
                )
            )

            connection.commit()

            return payment_id

        except Exception:
            connection.rollback()
            raise

        finally:
            connection.close()

    # ========================================================
    # 14. GET PAYMENT BY ID
    # ========================================================

    @staticmethod
    def get_payment_by_id(payment_id):

        return fetch_one(
            """
            SELECT
                pay.id,
                pay.bill_id,
                pay.amount,
                pay.payment_method,
                pay.payment_reference,
                pay.paid_at,
                b.bill_number,
                p.name AS patient_name,
                p.mobile
            FROM payments pay
            JOIN bills b ON b.id = pay.bill_id
            JOIN visits v ON v.id = b.visit_id
            JOIN patients p ON p.id = v.patient_id
            WHERE pay.id = ?
            LIMIT 1
            """,
            (payment_id,)
        )

    # ========================================================
    # 15. GET ALL PAYMENTS
    # ========================================================

    @staticmethod
    def get_all_payments(
        start_date=None,
        end_date=None,
        payment_method=None
    ):

        query = """
            SELECT
                pay.id,
                pay.bill_id,
                pay.amount,
                pay.payment_method,
                pay.payment_reference,
                pay.paid_at,
                b.bill_number,
                p.name AS patient_name,
                p.mobile
            FROM payments pay
            JOIN bills b ON b.id = pay.bill_id
            JOIN visits v ON v.id = b.visit_id
            JOIN patients p ON p.id = v.patient_id
            WHERE 1 = 1
        """

        params = []

        if start_date:
            query += " AND DATE(pay.paid_at) >= ?"
            params.append(str(start_date))

        if end_date:
            query += " AND DATE(pay.paid_at) <= ?"
            params.append(str(end_date))

        if payment_method:
            if payment_method not in BillingModel.PAYMENT_METHODS:
                raise ValueError("Invalid payment method.")

            query += " AND pay.payment_method = ?"
            params.append(payment_method)

        query += " ORDER BY pay.id DESC"

        return fetch_all(query, tuple(params))

    # ========================================================
    # 16. GET REVENUE TOTAL
    # ========================================================

    @staticmethod
    def get_total_revenue(start_date=None, end_date=None):

        query = """
            SELECT COALESCE(SUM(amount), 0) AS total
            FROM payments
            WHERE 1 = 1
        """

        params = []

        if start_date:
            query += " AND DATE(paid_at) >= ?"
            params.append(str(start_date))

        if end_date:
            query += " AND DATE(paid_at) <= ?"
            params.append(str(end_date))

        result = fetch_one(query, tuple(params))

        return float(result["total"] or 0) if result else 0.0

    # ========================================================
    # 17. GET TODAY'S REVENUE
    # ========================================================

    @staticmethod
    def get_today_revenue():

        today = date.today().isoformat()

        return BillingModel.get_total_revenue(
            start_date=today,
            end_date=today
        )

    # ========================================================
    # 18. GET BILLING TOTAL
    # ========================================================

    @staticmethod
    def get_total_billing(start_date=None, end_date=None):

        query = """
            SELECT COALESCE(SUM(total_amount), 0) AS total
            FROM bills
            WHERE 1 = 1
        """

        params = []

        if start_date:
            query += " AND DATE(created_at) >= ?"
            params.append(str(start_date))

        if end_date:
            query += " AND DATE(created_at) <= ?"
            params.append(str(end_date))

        result = fetch_one(query, tuple(params))

        return float(result["total"] or 0) if result else 0.0

    # ========================================================
    # 19. GET OUTSTANDING BILLS
    # ========================================================

    @staticmethod
    def get_outstanding_bills(
        start_date=None,
        end_date=None
    ):

        query = """
            SELECT
                b.id,
                b.bill_number,
                b.visit_id,
                b.total_amount,
                b.payment_status,
                b.created_at,
                v.token_number,
                p.name AS patient_name,
                p.mobile,
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
        """

        params = []

        if start_date:
            query += " AND DATE(b.created_at) >= ?"
            params.append(str(start_date))

        if end_date:
            query += " AND DATE(b.created_at) <= ?"
            params.append(str(end_date))

        query += " ORDER BY b.id DESC"

        return fetch_all(query, tuple(params))

    # ========================================================
    # 20. GET OUTSTANDING TOTAL
    # ========================================================

    @staticmethod
    def get_outstanding_total(
        start_date=None,
        end_date=None
    ):

        records = BillingModel.get_outstanding_bills(
            start_date,
            end_date
        )

        return float(
            sum(
                (
                    Decimal(str(record["balance"]))
                    for record in records
                ),
                BillingModel.ZERO
            )
        )

    # ========================================================
    # 21. GET BILLING STATISTICS
    # ========================================================

    @staticmethod
    def get_statistics(
        start_date=None,
        end_date=None
    ):

        query = """
            SELECT
                COUNT(*) AS total_bills,
                COALESCE(SUM(total_amount), 0) AS total_billing,
                COALESCE(SUM(consultation_fee), 0)
                    AS consultation_fees,
                COALESCE(SUM(medicine_fee), 0)
                    AS medicine_fees,
                COALESCE(SUM(other_charges), 0)
                    AS other_charges,
                COALESCE(
                    SUM(
                        CASE
                            WHEN payment_status = 'Paid'
                            THEN 1 ELSE 0
                        END
                    ),
                    0
                ) AS paid_bills,
                COALESCE(
                    SUM(
                        CASE
                            WHEN payment_status = 'Unpaid'
                            THEN 1 ELSE 0
                        END
                    ),
                    0
                ) AS unpaid_bills,
                COALESCE(
                    SUM(
                        CASE
                            WHEN payment_status = 'Partial'
                            THEN 1 ELSE 0
                        END
                    ),
                    0
                ) AS partial_bills
            FROM bills
            WHERE 1 = 1
        """

        params = []

        if start_date:
            query += " AND DATE(created_at) >= ?"
            params.append(str(start_date))

        if end_date:
            query += " AND DATE(created_at) <= ?"
            params.append(str(end_date))

        result = fetch_one(query, tuple(params))

        statistics = dict(result) if result else {}

        statistics["collected_revenue"] = (
            BillingModel.get_total_revenue(
                start_date,
                end_date
            )
        )

        statistics["outstanding_balance"] = (
            BillingModel.get_outstanding_total(
                start_date,
                end_date
            )
        )

        return statistics

    # ========================================================
    # 22. DAILY REVENUE STATISTICS
    # ========================================================

    @staticmethod
    def get_daily_revenue(
        start_date=None,
        end_date=None
    ):

        query = """
            SELECT
                DATE(paid_at) AS payment_date,
                COUNT(*) AS transactions,
                COALESCE(SUM(amount), 0) AS revenue
            FROM payments
            WHERE 1 = 1
        """

        params = []

        if start_date:
            query += " AND DATE(paid_at) >= ?"
            params.append(str(start_date))

        if end_date:
            query += " AND DATE(paid_at) <= ?"
            params.append(str(end_date))

        query += """
            GROUP BY DATE(paid_at)
            ORDER BY payment_date ASC
        """

        return fetch_all(query, tuple(params))

    # ========================================================
    # 23. MONTHLY REVENUE STATISTICS
    # ========================================================

    @staticmethod
    def get_monthly_revenue(
        start_date=None,
        end_date=None
    ):

        query = """
            SELECT
                STRFTIME('%Y-%m', paid_at) AS month,
                COUNT(*) AS transactions,
                COALESCE(SUM(amount), 0) AS revenue
            FROM payments
            WHERE 1 = 1
        """

        params = []

        if start_date:
            query += " AND DATE(paid_at) >= ?"
            params.append(str(start_date))

        if end_date:
            query += " AND DATE(paid_at) <= ?"
            params.append(str(end_date))

        query += """
            GROUP BY STRFTIME('%Y-%m', paid_at)
            ORDER BY month ASC
        """

        return fetch_all(query, tuple(params))

    # ========================================================
    # 24. PAYMENT METHOD STATISTICS
    # ========================================================

    @staticmethod
    def get_payment_method_statistics(
        start_date=None,
        end_date=None
    ):

        query = """
            SELECT
                payment_method,
                COUNT(*) AS transactions,
                COALESCE(SUM(amount), 0) AS total_amount
            FROM payments
            WHERE 1 = 1
        """

        params = []

        if start_date:
            query += " AND DATE(paid_at) >= ?"
            params.append(str(start_date))

        if end_date:
            query += " AND DATE(paid_at) <= ?"
            params.append(str(end_date))

        query += """
            GROUP BY payment_method
            ORDER BY total_amount DESC
        """

        return fetch_all(query, tuple(params))

    # ========================================================
    # 25. COUNT BILLS
    # ========================================================

    @staticmethod
    def count_bills(payment_status=None):

        query = """
            SELECT COUNT(*) AS total
            FROM bills
            WHERE 1 = 1
        """

        params = []

        if payment_status:
            if payment_status not in BillingModel.PAYMENT_STATUSES:
                raise ValueError("Invalid payment status.")

            query += " AND payment_status = ?"
            params.append(payment_status)

        result = fetch_one(query, tuple(params))

        return int(result["total"]) if result else 0

    # ========================================================
    # 26. GET RECEIPT DETAILS
    # ========================================================

    @staticmethod
    def get_receipt_details(bill_id):

        bill = BillingModel.get_by_id(bill_id)

        if not bill:
            return None

        receipt = dict(bill)

        receipt["payments"] = BillingModel.get_payments(
            bill_id
        )

        receipt["amount_paid"] = float(
            BillingModel.get_amount_paid(bill_id)
        )

        receipt["balance"] = float(
            BillingModel.get_balance(bill_id)
        )

        return receipt


# ============================================================
# END OF FILE
# ============================================================
