# ============================================================
# HOSPITAL RECEPTION SYSTEM
# FILE: services/billing_service.py
# PURPOSE: Hospital Billing and Payment Management
# DATABASE: SQLite3
# ============================================================

from datetime import date, datetime
from decimal import Decimal

from models.billing_model import BillingModel
from models.patient_model import PatientModel
from models.token_model import TokenModel


class BillingService:

    PAYMENT_METHODS = ("Cash", "UPI", "Card")
    PAYMENT_STATUSES = ("Paid", "Unpaid", "Partial")

    ZERO = Decimal("0.00")

    # ========================================================
    # 1. VALIDATE AMOUNT
    # ========================================================

    @staticmethod
    def validate_amount(amount):

        return BillingModel.validate_amount(amount)

    # ========================================================
    # 2. CALCULATE BILL TOTAL
    # ========================================================

    @staticmethod
    def calculate_total(
        consultation_fee=0,
        medicine_fee=0,
        other_charges=0
    ):

        return BillingModel.calculate_total(
            consultation_fee,
            medicine_fee,
            other_charges
        )

    # ========================================================
    # 3. FORMAT CURRENCY
    # ========================================================

    @staticmethod
    def format_currency(amount):

        return BillingModel.format_currency(amount)

    # ========================================================
    # 4. VALIDATE PAYMENT METHOD
    # ========================================================

    @staticmethod
    def validate_payment_method(payment_method):

        if payment_method not in BillingService.PAYMENT_METHODS:
            raise ValueError(
                "Payment method must be Cash, UPI or Card."
            )

        return payment_method

    # ========================================================
    # 5. VALIDATE PAYMENT STATUS
    # ========================================================

    @staticmethod
    def validate_payment_status(payment_status):

        if payment_status not in BillingService.PAYMENT_STATUSES:
            raise ValueError(
                "Invalid payment status."
            )

        return payment_status

    # ========================================================
    # 6. GET PATIENT BILLING DETAILS
    # ========================================================

    @staticmethod
    def get_patient_billing_details(visit_id):

        visit = TokenModel.get_by_id(visit_id)

        if not visit:
            raise ValueError("Patient visit not found.")

        patient = PatientModel.get_by_id(
            visit["patient_id"]
        )

        if not patient:
            raise ValueError("Patient not found.")

        bill = BillingModel.get_by_visit(visit_id)

        return {
            "visit": visit,
            "patient": patient,
            "bill": bill
        }

    # ========================================================
    # 7. CHECK BILL EXISTS
    # ========================================================

    @staticmethod
    def bill_exists(visit_id):

        return BillingModel.get_by_visit(visit_id) is not None

    # ========================================================
    # 8. CREATE PATIENT BILL
    # ========================================================

    @staticmethod
    def create_bill(
        visit_id,
        consultation_fee=0,
        medicine_fee=0,
        other_charges=0,
        payment_method="Cash",
        payment_status="Unpaid",
        amount_paid=None,
        payment_reference=None,
        doctor_id=None
    ):

        visit = TokenModel.get_by_id(visit_id)

        if not visit:
            raise ValueError(
                "Patient visit not found."
            )

        if visit["status"] != "In Progress":
            raise ValueError(
                "Consultation must be In Progress before billing."
            )

        if doctor_id is not None:

            if visit["doctor_id"] != int(doctor_id):
                raise ValueError(
                    "This consultation belongs to another doctor."
                )

        existing_bill = BillingModel.get_by_visit(
            visit_id
        )

        if existing_bill:
            raise ValueError(
                "A bill already exists for this patient visit."
            )

        consultation = BillingService.validate_amount(
            consultation_fee
        )

        medicine = BillingService.validate_amount(
            medicine_fee
        )

        other = BillingService.validate_amount(
            other_charges
        )

        total = BillingService.calculate_total(
            consultation,
            medicine,
            other
        )

        BillingService.validate_payment_method(
            payment_method
        )

        BillingService.validate_payment_status(
            payment_status
        )

        if amount_paid is None:

            if payment_status == "Paid":
                amount_paid = total
            else:
                amount_paid = BillingService.ZERO

        amount_paid = BillingService.validate_amount(
            amount_paid
        )

        if payment_status == "Unpaid":

            if amount_paid != BillingService.ZERO:
                raise ValueError(
                    "Unpaid bill must have zero payment."
                )

        elif payment_status == "Paid":

            if amount_paid != total:
                raise ValueError(
                    "Paid amount must equal the total bill."
                )

        elif payment_status == "Partial":

            if not BillingService.ZERO < amount_paid < total:
                raise ValueError(
                    "Partial payment must be greater than zero "
                    "and less than the total bill."
                )

        bill = BillingModel.create_bill(
            visit_id=visit_id,
            consultation_fee=consultation,
            medicine_fee=medicine,
            other_charges=other,
            payment_method=payment_method,
            payment_status=payment_status,
            amount_paid=amount_paid,
            payment_reference=payment_reference,
            doctor_id=doctor_id
        )

        if not bill:
            raise ValueError(
                "Bill could not be created."
            )

        return {
            "success": True,
            "message": "Bill created successfully.",
            "bill": bill,
            "bill_number": bill["bill_number"],
            "total_amount": float(total),
            "amount_paid": float(amount_paid),
            "balance": float(total - amount_paid),
            "payment_status": payment_status
        }

    # ========================================================
    # 9. GENERATE UNPAID BILL
    # ========================================================

    @staticmethod
    def create_unpaid_bill(
        visit_id,
        consultation_fee=0,
        medicine_fee=0,
        other_charges=0,
        doctor_id=None
    ):

        return BillingService.create_bill(
            visit_id=visit_id,
            consultation_fee=consultation_fee,
            medicine_fee=medicine_fee,
            other_charges=other_charges,
            payment_method="Cash",
            payment_status="Unpaid",
            amount_paid=0,
            doctor_id=doctor_id
        )

    # ========================================================
    # 10. CREATE FULLY PAID BILL
    # ========================================================

    @staticmethod
    def create_paid_bill(
        visit_id,
        consultation_fee=0,
        medicine_fee=0,
        other_charges=0,
        payment_method="Cash",
        payment_reference=None,
        doctor_id=None
    ):

        total = BillingService.calculate_total(
            consultation_fee,
            medicine_fee,
            other_charges
        )

        return BillingService.create_bill(
            visit_id=visit_id,
            consultation_fee=consultation_fee,
            medicine_fee=medicine_fee,
            other_charges=other_charges,
            payment_method=payment_method,
            payment_status="Paid",
            amount_paid=total,
            payment_reference=payment_reference,
            doctor_id=doctor_id
        )

    # ========================================================
    # 11. GET BILL DETAILS
    # ========================================================

    @staticmethod
    def get_bill_details(bill_id):

        bill = BillingModel.get_by_id(bill_id)

        if not bill:
            raise ValueError("Bill not found.")

        amount_paid = BillingModel.get_amount_paid(
            bill_id
        )

        balance = BillingModel.get_balance(
            bill_id
        )

        result = dict(bill)

        result["amount_paid"] = float(amount_paid)
        result["balance"] = float(balance)

        result["payments"] = BillingModel.get_payments(
            bill_id
        )

        return result

    # ========================================================
    # 12. GET BILL BY NUMBER
    # ========================================================

    @staticmethod
    def get_bill_by_number(bill_number):

        bill = BillingModel.get_by_number(
            bill_number
        )

        if not bill:
            raise ValueError("Bill not found.")

        return BillingService.get_bill_details(
            bill["id"]
        )

    # ========================================================
    # 13. GET BILL BY VISIT
    # ========================================================

    @staticmethod
    def get_bill_by_visit(visit_id):

        bill = BillingModel.get_by_visit(
            visit_id
        )

        if not bill:
            return None

        return BillingService.get_bill_details(
            bill["id"]
        )

    # ========================================================
    # 14. GET ALL BILLS
    # ========================================================

    @staticmethod
    def get_all_bills(
        start_date=None,
        end_date=None,
        payment_status=None,
        limit=None
    ):

        start_date, end_date = BillingService.validate_date_range(
            start_date,
            end_date
        )

        if payment_status is not None:

            BillingService.validate_payment_status(
                payment_status
            )

        return BillingModel.get_all(
            start_date=start_date,
            end_date=end_date,
            payment_status=payment_status,
            limit=limit
        )

    # ========================================================
    # 15. SEARCH BILLS
    # ========================================================

    @staticmethod
    def search_bills(search_text):

        return BillingModel.search(
            search_text
        )

    # ========================================================
    # 16. RECORD PAYMENT
    # ========================================================

    @staticmethod
    def record_payment(
        bill_id,
        amount,
        payment_method="Cash",
        payment_reference=None
    ):

        bill = BillingModel.get_by_id(
            bill_id
        )

        if not bill:
            raise ValueError("Bill not found.")

        amount = BillingService.validate_amount(
            amount
        )

        BillingService.validate_payment_method(
            payment_method
        )

        if amount <= 0:
            raise ValueError(
                "Payment amount must be greater than zero."
            )

        balance = BillingModel.get_balance(
            bill_id
        )

        if balance <= 0:
            raise ValueError(
                "This bill is already fully paid."
            )

        if amount > balance:
            raise ValueError(
                "Payment cannot exceed the outstanding balance."
            )

        payment_id = BillingModel.record_payment(
            bill_id=bill_id,
            amount=amount,
            payment_method=payment_method,
            payment_reference=payment_reference
        )

        updated_bill = BillingService.get_bill_details(
            bill_id
        )

        return {
            "success": True,
            "message": "Payment recorded successfully.",
            "payment_id": payment_id,
            "bill_id": bill_id,
            "bill_number": updated_bill["bill_number"],
            "amount_received": float(amount),
            "total_paid": updated_bill["amount_paid"],
            "balance": updated_bill["balance"],
            "payment_status": updated_bill["payment_status"]
        }

    # ========================================================
    # 17. PAY OUTSTANDING BALANCE
    # ========================================================

    @staticmethod
    def pay_remaining_balance(
        bill_id,
        payment_method="Cash",
        payment_reference=None
    ):

        balance = BillingModel.get_balance(
            bill_id
        )

        if balance <= 0:
            raise ValueError(
                "No outstanding balance for this bill."
            )

        return BillingService.record_payment(
            bill_id=bill_id,
            amount=balance,
            payment_method=payment_method,
            payment_reference=payment_reference
        )

    # ========================================================
    # 18. GET PAYMENT DETAILS
    # ========================================================

    @staticmethod
    def get_payment_details(payment_id):

        payment = BillingModel.get_payment_by_id(
            payment_id
        )

        if not payment:
            raise ValueError("Payment not found.")

        return payment

    # ========================================================
    # 19. GET BILL PAYMENT HISTORY
    # ========================================================

    @staticmethod
    def get_payment_history(bill_id):

        bill = BillingModel.get_by_id(
            bill_id
        )

        if not bill:
            raise ValueError("Bill not found.")

        return BillingModel.get_payments(
            bill_id
        )

    # ========================================================
    # 20. GET ALL PAYMENTS
    # ========================================================

    @staticmethod
    def get_all_payments(
        start_date=None,
        end_date=None,
        payment_method=None
    ):

        start_date, end_date = BillingService.validate_date_range(
            start_date,
            end_date
        )

        if payment_method is not None:

            BillingService.validate_payment_method(
                payment_method
            )

        return BillingModel.get_all_payments(
            start_date=start_date,
            end_date=end_date,
            payment_method=payment_method
        )

    # ========================================================
    # 21. GET TOTAL BILLING
    # ========================================================

    @staticmethod
    def get_total_billing(
        start_date=None,
        end_date=None
    ):

        start_date, end_date = BillingService.validate_date_range(
            start_date,
            end_date
        )

        return BillingModel.get_total_billing(
            start_date,
            end_date
        )

    # ========================================================
    # 22. GET TOTAL REVENUE
    # ========================================================

    @staticmethod
    def get_total_revenue(
        start_date=None,
        end_date=None
    ):

        start_date, end_date = BillingService.validate_date_range(
            start_date,
            end_date
        )

        return BillingModel.get_total_revenue(
            start_date,
            end_date
        )

    # ========================================================
    # 23. GET TODAY'S REVENUE
    # ========================================================

    @staticmethod
    def get_today_revenue():

        return BillingModel.get_today_revenue()

    # ========================================================
    # 24. GET OUTSTANDING BILLS
    # ========================================================

    @staticmethod
    def get_outstanding_bills(
        start_date=None,
        end_date=None
    ):

        start_date, end_date = BillingService.validate_date_range(
            start_date,
            end_date
        )

        return BillingModel.get_outstanding_bills(
            start_date,
            end_date
        )

    # ========================================================
    # 25. GET OUTSTANDING TOTAL
    # ========================================================

    @staticmethod
    def get_outstanding_total(
        start_date=None,
        end_date=None
    ):

        start_date, end_date = BillingService.validate_date_range(
            start_date,
            end_date
        )

        return BillingModel.get_outstanding_total(
            start_date,
            end_date
        )

    # ========================================================
    # 26. GET BILLING STATISTICS
    # ========================================================

    @staticmethod
    def get_billing_statistics(
        start_date=None,
        end_date=None
    ):

        start_date, end_date = BillingService.validate_date_range(
            start_date,
            end_date
        )

        return BillingModel.get_statistics(
            start_date,
            end_date
        )

    # ========================================================
    # 27. GET DAILY REVENUE
    # ========================================================

    @staticmethod
    def get_daily_revenue(
        start_date=None,
        end_date=None
    ):

        start_date, end_date = BillingService.validate_date_range(
            start_date,
            end_date
        )

        return BillingModel.get_daily_revenue(
            start_date,
            end_date
        )

    # ========================================================
    # 28. GET MONTHLY REVENUE
    # ========================================================

    @staticmethod
    def get_monthly_revenue(
        start_date=None,
        end_date=None
    ):

        start_date, end_date = BillingService.validate_date_range(
            start_date,
            end_date
        )

        return BillingModel.get_monthly_revenue(
            start_date,
            end_date
        )

    # ========================================================
    # 29. GET PAYMENT METHOD STATISTICS
    # ========================================================

    @staticmethod
    def get_payment_method_statistics(
        start_date=None,
        end_date=None
    ):

        start_date, end_date = BillingService.validate_date_range(
            start_date,
            end_date
        )

        return BillingModel.get_payment_method_statistics(
            start_date,
            end_date
        )

    # ========================================================
    # 30. GET PATIENT BILLING HISTORY
    # ========================================================

    @staticmethod
    def get_patient_billing_history(patient_id):

        patient = PatientModel.get_by_id(
            patient_id
        )

        if not patient:
            raise ValueError("Patient not found.")

        visits = PatientModel.get_visit_history(
            patient_id
        )

        bills = []

        for visit in visits:

            if visit["bill_id"] is not None:

                bill = BillingService.get_bill_details(
                    visit["bill_id"]
                )

                bills.append(bill)

        return {
            "patient": patient,
            "total_bills": len(bills),
            "bills": bills
        }

    # ========================================================
    # 31. GET TODAY'S BILLING SUMMARY
    # ========================================================

    @staticmethod
    def get_today_summary():

        today = date.today().isoformat()

        statistics = BillingModel.get_statistics(
            today,
            today
        )

        return {
            "date": today,
            "total_bills": statistics["total_bills"],
            "total_billing": float(
                statistics["total_billing"] or 0
            ),
            "consultation_fees": float(
                statistics["consultation_fees"] or 0
            ),
            "medicine_fees": float(
                statistics["medicine_fees"] or 0
            ),
            "other_charges": float(
                statistics["other_charges"] or 0
            ),
            "collected_revenue": float(
                statistics["collected_revenue"] or 0
            ),
            "outstanding_balance": float(
                statistics["outstanding_balance"] or 0
            ),
            "paid_bills": statistics["paid_bills"],
            "unpaid_bills": statistics["unpaid_bills"],
            "partial_bills": statistics["partial_bills"]
        }

    # ========================================================
    # 32. GET OVERALL BILLING SUMMARY
    # ========================================================

    @staticmethod
    def get_overall_summary():

        statistics = BillingModel.get_statistics()

        return {
            "total_bills": statistics["total_bills"],
            "total_billing": float(
                statistics["total_billing"] or 0
            ),
            "consultation_fees": float(
                statistics["consultation_fees"] or 0
            ),
            "medicine_fees": float(
                statistics["medicine_fees"] or 0
            ),
            "other_charges": float(
                statistics["other_charges"] or 0
            ),
            "collected_revenue": float(
                statistics["collected_revenue"] or 0
            ),
            "outstanding_balance": float(
                statistics["outstanding_balance"] or 0
            ),
            "paid_bills": statistics["paid_bills"],
            "unpaid_bills": statistics["unpaid_bills"],
            "partial_bills": statistics["partial_bills"]
        }

    # ========================================================
    # 33. GET RECEIPT DETAILS
    # ========================================================

    @staticmethod
    def get_receipt_details(bill_id):

        receipt = BillingModel.get_receipt_details(
            bill_id
        )

        if not receipt:
            raise ValueError("Receipt not found.")

        return receipt

    # ========================================================
    # 34. GET PAYMENT STATUS
    # ========================================================

    @staticmethod
    def get_payment_status(bill_id):

        bill = BillingModel.get_by_id(
            bill_id
        )

        if not bill:
            raise ValueError("Bill not found.")

        total = BillingService.validate_amount(
            bill["total_amount"]
        )

        amount_paid = BillingModel.get_amount_paid(
            bill_id
        )

        if amount_paid >= total:
            return "Paid"

        if amount_paid > 0:
            return "Partial"

        return "Unpaid"

    # ========================================================
    # 35. VALIDATE DATE
    # ========================================================

    @staticmethod
    def validate_date(value):

        if isinstance(value, datetime):
            return value.date().isoformat()

        if isinstance(value, date):
            return value.isoformat()

        try:
            return date.fromisoformat(
                str(value).strip()
            ).isoformat()

        except (ValueError, TypeError):
            raise ValueError(
                "Invalid date. Use YYYY-MM-DD format."
            )

    # ========================================================
    # 36. VALIDATE DATE RANGE
    # ========================================================

    @staticmethod
    def validate_date_range(
        start_date=None,
        end_date=None
    ):

        if start_date is not None:
            start_date = BillingService.validate_date(
                start_date
            )

        if end_date is not None:
            end_date = BillingService.validate_date(
                end_date
            )

        if (
            start_date is not None
            and end_date is not None
            and start_date > end_date
        ):
            raise ValueError(
                "Start date cannot be after end date."
            )

        return start_date, end_date


# ============================================================
# END OF FILE
# ============================================================
