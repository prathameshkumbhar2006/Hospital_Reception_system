# ============================================================
# HOSPITAL RECEPTION SYSTEM
# FILE: services/analytics_service.py
# PURPOSE: Hospital Patient, Token, Billing and Revenue Analytics
# DATABASE: SQLite3
# LIBRARIES: Python, Pandas
# ============================================================

from datetime import date, datetime, timedelta
from decimal import Decimal

import pandas as pd

from database import fetch_one, fetch_all


class AnalyticsService:

    # ========================================================
    # 1. VALIDATE DATE
    # ========================================================

    @staticmethod
    def validate_date(value):

        if value is None or value == "":
            return None

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
    # 2. VALIDATE DATE RANGE
    # ========================================================

    @staticmethod
    def validate_date_range(start_date=None, end_date=None):

        start_date = AnalyticsService.validate_date(start_date)
        end_date = AnalyticsService.validate_date(end_date)

        if start_date and end_date and start_date > end_date:
            raise ValueError(
                "Start date cannot be after end date."
            )

        return start_date, end_date

    # ========================================================
    # 3. GET DATE RANGE FROM PERIOD
    # ========================================================

    @staticmethod
    def get_period_dates(period="Last 30 Days"):

        today = date.today()

        periods = {
            "Today": (today, today),
            "Last 7 Days": (
                today - timedelta(days=6),
                today
            ),
            "Last 30 Days": (
                today - timedelta(days=29),
                today
            ),
            "Last 90 Days": (
                today - timedelta(days=89),
                today
            ),
            "This Month": (
                today.replace(day=1),
                today
            ),
            "This Year": (
                date(today.year, 1, 1),
                today
            ),
            "All Time": (None, None)
        }

        if period not in periods:
            raise ValueError("Invalid analytics period.")

        start_date, end_date = periods[period]

        return (
            start_date.isoformat() if start_date else None,
            end_date.isoformat() if end_date else None
        )

    # ========================================================
    # 4. BUILD DATE FILTER
    # ========================================================

    @staticmethod
    def build_date_filter(
        column,
        start_date=None,
        end_date=None
    ):

        allowed_columns = {
            "p.created_at",
            "v.visit_date",
            "b.created_at",
            "pay.paid_at",
            "created_at",
            "visit_date",
            "paid_at"
        }

        if column not in allowed_columns:
            raise ValueError("Invalid date column.")

        start_date, end_date = (
            AnalyticsService.validate_date_range(
                start_date,
                end_date
            )
        )

        conditions = []
        parameters = []

        if start_date:
            conditions.append(f"DATE({column}) >= ?")
            parameters.append(start_date)

        if end_date:
            conditions.append(f"DATE({column}) <= ?")
            parameters.append(end_date)

        if conditions:
            return " AND " + " AND ".join(conditions), tuple(parameters)

        return "", ()

    # ========================================================
    # 5. FORMAT CURRENCY
    # ========================================================

    @staticmethod
    def format_currency(amount):

        value = Decimal(str(amount or 0))

        return f"₹{value:,.2f}"

    # ========================================================
    # 6. TOTAL REGISTERED PATIENTS
    # ========================================================

    @staticmethod
    def get_total_patients(start_date=None, end_date=None):

        condition, params = AnalyticsService.build_date_filter(
            "p.created_at",
            start_date,
            end_date
        )

        result = fetch_one(
            """
            SELECT COUNT(*) AS total
            FROM patients p
            WHERE 1 = 1
            """ + condition,
            params
        )

        return int(result["total"] or 0) if result else 0

    # ========================================================
    # 7. TOTAL PATIENT VISITS
    # ========================================================

    @staticmethod
    def get_total_visits(start_date=None, end_date=None):

        condition, params = AnalyticsService.build_date_filter(
            "v.visit_date",
            start_date,
            end_date
        )

        result = fetch_one(
            """
            SELECT COUNT(*) AS total
            FROM visits v
            WHERE 1 = 1
            """ + condition,
            params
        )

        return int(result["total"] or 0) if result else 0

    # ========================================================
    # 8. COUNT VISITS BY STATUS
    # ========================================================

    @staticmethod
    def count_visits_by_status(
        status,
        start_date=None,
        end_date=None
    ):

        valid_statuses = (
            "Waiting",
            "In Progress",
            "Completed",
            "Cancelled"
        )

        if status not in valid_statuses:
            raise ValueError("Invalid visit status.")

        condition, params = AnalyticsService.build_date_filter(
            "v.visit_date",
            start_date,
            end_date
        )

        result = fetch_one(
            """
            SELECT COUNT(*) AS total
            FROM visits v
            WHERE v.status = ?
            """ + condition,
            (status,) + params
        )

        return int(result["total"] or 0) if result else 0

    # ========================================================
    # 9. TOTAL BILLING
    # ========================================================

    @staticmethod
    def get_total_billing(start_date=None, end_date=None):

        condition, params = AnalyticsService.build_date_filter(
            "b.created_at",
            start_date,
            end_date
        )

        result = fetch_one(
            """
            SELECT
                COALESCE(SUM(b.total_amount), 0) AS total
            FROM bills b
            WHERE 1 = 1
            """ + condition,
            params
        )

        return float(result["total"] or 0) if result else 0.0

    # ========================================================
    # 10. TOTAL COLLECTED REVENUE
    # ========================================================

    @staticmethod
    def get_total_revenue(start_date=None, end_date=None):

        condition, params = AnalyticsService.build_date_filter(
            "pay.paid_at",
            start_date,
            end_date
        )

        result = fetch_one(
            """
            SELECT
                COALESCE(SUM(pay.amount), 0) AS total
            FROM payments pay
            WHERE 1 = 1
            """ + condition,
            params
        )

        return float(result["total"] or 0) if result else 0.0

    # ========================================================
    # 11. TOTAL OUTSTANDING BALANCE
    # ========================================================

    @staticmethod
    def get_outstanding_balance(
        start_date=None,
        end_date=None
    ):

        condition, params = AnalyticsService.build_date_filter(
            "b.created_at",
            start_date,
            end_date
        )

        result = fetch_one(
            """
            SELECT
                COALESCE(
                    SUM(
                        MAX(
                            b.total_amount -
                            COALESCE(
                                (
                                    SELECT SUM(pay.amount)
                                    FROM payments pay
                                    WHERE pay.bill_id = b.id
                                ),
                                0
                            ),
                            0
                        )
                    ),
                    0
                ) AS total
            FROM bills b
            WHERE 1 = 1
            """ + condition,
            params
        )

        return float(result["total"] or 0) if result else 0.0

    # ========================================================
    # 12. DASHBOARD OVERVIEW
    # ========================================================

    @staticmethod
    def get_overview(start_date=None, end_date=None):

        start_date, end_date = (
            AnalyticsService.validate_date_range(
                start_date,
                end_date
            )
        )

        return {
            "start_date": start_date,
            "end_date": end_date,
            "total_patients": AnalyticsService.get_total_patients(
                start_date,
                end_date
            ),
            "total_visits": AnalyticsService.get_total_visits(
                start_date,
                end_date
            ),
            "waiting": AnalyticsService.count_visits_by_status(
                "Waiting",
                start_date,
                end_date
            ),
            "in_progress": AnalyticsService.count_visits_by_status(
                "In Progress",
                start_date,
                end_date
            ),
            "completed": AnalyticsService.count_visits_by_status(
                "Completed",
                start_date,
                end_date
            ),
            "cancelled": AnalyticsService.count_visits_by_status(
                "Cancelled",
                start_date,
                end_date
            ),
            "total_billing": AnalyticsService.get_total_billing(
                start_date,
                end_date
            ),
            "total_revenue": AnalyticsService.get_total_revenue(
                start_date,
                end_date
            ),
            "outstanding_balance": (
                AnalyticsService.get_outstanding_balance(
                    start_date,
                    end_date
                )
            )
        }

    # ========================================================
    # 13. TODAY'S OVERVIEW
    # ========================================================

    @staticmethod
    def get_today_overview():

        today = date.today().isoformat()

        return AnalyticsService.get_overview(
            today,
            today
        )

    # ========================================================
    # 14. DAILY PATIENT VISITS
    # ========================================================

    @staticmethod
    def get_daily_patient_visits(
        start_date=None,
        end_date=None
    ):

        condition, params = AnalyticsService.build_date_filter(
            "v.visit_date",
            start_date,
            end_date
        )

        return fetch_all(
            """
            SELECT
                v.visit_date AS day,
                COUNT(*) AS total_visits,
                COUNT(DISTINCT v.patient_id) AS unique_patients,
                SUM(
                    CASE
                        WHEN v.status = 'Completed'
                        THEN 1 ELSE 0
                    END
                ) AS completed_visits
            FROM visits v
            WHERE 1 = 1
            """ + condition + """
            GROUP BY v.visit_date
            ORDER BY v.visit_date ASC
            """,
            params
        )

    # ========================================================
    # 15. MONTHLY PATIENT VISITS
    # ========================================================

    @staticmethod
    def get_monthly_patient_visits(
        start_date=None,
        end_date=None
    ):

        condition, params = AnalyticsService.build_date_filter(
            "v.visit_date",
            start_date,
            end_date
        )

        return fetch_all(
            """
            SELECT
                STRFTIME('%Y-%m', v.visit_date) AS month,
                COUNT(*) AS total_visits,
                COUNT(DISTINCT v.patient_id) AS unique_patients
            FROM visits v
            WHERE 1 = 1
            """ + condition + """
            GROUP BY STRFTIME('%Y-%m', v.visit_date)
            ORDER BY month ASC
            """,
            params
        )

    # ========================================================
    # 16. DAILY PATIENT REGISTRATION
    # ========================================================

    @staticmethod
    def get_daily_registrations(
        start_date=None,
        end_date=None
    ):

        condition, params = AnalyticsService.build_date_filter(
            "p.created_at",
            start_date,
            end_date
        )

        return fetch_all(
            """
            SELECT
                DATE(p.created_at) AS day,
                COUNT(*) AS new_patients
            FROM patients p
            WHERE 1 = 1
            """ + condition + """
            GROUP BY DATE(p.created_at)
            ORDER BY day ASC
            """,
            params
        )

    # ========================================================
    # 17. MONTHLY PATIENT REGISTRATION
    # ========================================================

    @staticmethod
    def get_monthly_registrations(
        start_date=None,
        end_date=None
    ):

        condition, params = AnalyticsService.build_date_filter(
            "p.created_at",
            start_date,
            end_date
        )

        return fetch_all(
            """
            SELECT
                STRFTIME('%Y-%m', p.created_at) AS month,
                COUNT(*) AS new_patients
            FROM patients p
            WHERE 1 = 1
            """ + condition + """
            GROUP BY STRFTIME('%Y-%m', p.created_at)
            ORDER BY month ASC
            """,
            params
        )

    # ========================================================
    # 18. DAILY REVENUE
    # ========================================================

    @staticmethod
    def get_daily_revenue(
        start_date=None,
        end_date=None
    ):

        condition, params = AnalyticsService.build_date_filter(
            "pay.paid_at",
            start_date,
            end_date
        )

        return fetch_all(
            """
            SELECT
                DATE(pay.paid_at) AS day,
                COUNT(*) AS transactions,
                ROUND(SUM(pay.amount), 2) AS revenue
            FROM payments pay
            WHERE 1 = 1
            """ + condition + """
            GROUP BY DATE(pay.paid_at)
            ORDER BY day ASC
            """,
            params
        )

    # ========================================================
    # 19. MONTHLY REVENUE
    # ========================================================

    @staticmethod
    def get_monthly_revenue(
        start_date=None,
        end_date=None
    ):

        condition, params = AnalyticsService.build_date_filter(
            "pay.paid_at",
            start_date,
            end_date
        )

        return fetch_all(
            """
            SELECT
                STRFTIME('%Y-%m', pay.paid_at) AS month,
                COUNT(*) AS transactions,
                ROUND(SUM(pay.amount), 2) AS revenue
            FROM payments pay
            WHERE 1 = 1
            """ + condition + """
            GROUP BY STRFTIME('%Y-%m', pay.paid_at)
            ORDER BY month ASC
            """,
            params
        )

    # ========================================================
    # 20. GENDER DISTRIBUTION
    # ========================================================

    @staticmethod
    def get_gender_distribution(
        start_date=None,
        end_date=None
    ):

        condition, params = AnalyticsService.build_date_filter(
            "p.created_at",
            start_date,
            end_date
        )

        return fetch_all(
            """
            SELECT
                COALESCE(p.gender, 'Other') AS gender,
                COUNT(*) AS total
            FROM patients p
            WHERE 1 = 1
            """ + condition + """
            GROUP BY COALESCE(p.gender, 'Other')
            ORDER BY total DESC
            """,
            params
        )

    # ========================================================
    # 21. TOKEN STATUS DISTRIBUTION
    # ========================================================

    @staticmethod
    def get_token_status_distribution(
        start_date=None,
        end_date=None
    ):

        condition, params = AnalyticsService.build_date_filter(
            "v.visit_date",
            start_date,
            end_date
        )

        return fetch_all(
            """
            SELECT
                v.status,
                COUNT(*) AS total
            FROM visits v
            WHERE 1 = 1
            """ + condition + """
            GROUP BY v.status
            ORDER BY total DESC
            """,
            params
        )

    # ========================================================
    # 22. PAYMENT METHOD DISTRIBUTION
    # ========================================================

    @staticmethod
    def get_payment_method_distribution(
        start_date=None,
        end_date=None
    ):

        condition, params = AnalyticsService.build_date_filter(
            "pay.paid_at",
            start_date,
            end_date
        )

        return fetch_all(
            """
            SELECT
                pay.payment_method,
                COUNT(*) AS transactions,
                ROUND(SUM(pay.amount), 2) AS total_amount
            FROM payments pay
            WHERE 1 = 1
            """ + condition + """
            GROUP BY pay.payment_method
            ORDER BY total_amount DESC
            """,
            params
        )

    # ========================================================
    # 23. PAYMENT STATUS DISTRIBUTION
    # ========================================================

    @staticmethod
    def get_payment_status_distribution(
        start_date=None,
        end_date=None
    ):

        condition, params = AnalyticsService.build_date_filter(
            "b.created_at",
            start_date,
            end_date
        )

        return fetch_all(
            """
            SELECT
                b.payment_status,
                COUNT(*) AS total_bills,
                ROUND(SUM(b.total_amount), 2) AS total_amount
            FROM bills b
            WHERE 1 = 1
            """ + condition + """
            GROUP BY b.payment_status
            ORDER BY total_bills DESC
            """,
            params
        )

    # ========================================================
    # 24. BILLING FEE BREAKDOWN
    # ========================================================

    @staticmethod
    def get_fee_breakdown(
        start_date=None,
        end_date=None
    ):

        condition, params = AnalyticsService.build_date_filter(
            "b.created_at",
            start_date,
            end_date
        )

        result = fetch_one(
            """
            SELECT
                COALESCE(
                    SUM(b.consultation_fee), 0
                ) AS consultation_fee,
                COALESCE(
                    SUM(b.medicine_fee), 0
                ) AS medicine_fee,
                COALESCE(
                    SUM(b.other_charges), 0
                ) AS other_charges,
                COALESCE(
                    SUM(b.total_amount), 0
                ) AS total_amount
            FROM bills b
            WHERE 1 = 1
            """ + condition,
            params
        )

        return {
            "consultation_fee": float(
                result["consultation_fee"] or 0
            ),
            "medicine_fee": float(
                result["medicine_fee"] or 0
            ),
            "other_charges": float(
                result["other_charges"] or 0
            ),
            "total_amount": float(
                result["total_amount"] or 0
            )
        }

    # ========================================================
    # 25. HOURLY PATIENT VISITS
    # ========================================================

    @staticmethod
    def get_hourly_visits(
        start_date=None,
        end_date=None
    ):

        condition, params = AnalyticsService.build_date_filter(
            "v.visit_date",
            start_date,
            end_date
        )

        return fetch_all(
            """
            SELECT
                SUBSTR(v.visit_time, 1, 2) AS hour,
                COUNT(*) AS total_visits
            FROM visits v
            WHERE v.visit_time IS NOT NULL
            """ + condition + """
            GROUP BY SUBSTR(v.visit_time, 1, 2)
            ORDER BY hour ASC
            """,
            params
        )

    # ========================================================
    # 26. BUSIEST DAY OF WEEK
    # ========================================================

    @staticmethod
    def get_weekday_distribution(
        start_date=None,
        end_date=None
    ):

        condition, params = AnalyticsService.build_date_filter(
            "v.visit_date",
            start_date,
            end_date
        )

        rows = fetch_all(
            """
            SELECT
                CAST(
                    STRFTIME('%w', v.visit_date)
                    AS INTEGER
                ) AS weekday_number,
                COUNT(*) AS total_visits
            FROM visits v
            WHERE 1 = 1
            """ + condition + """
            GROUP BY weekday_number
            ORDER BY weekday_number ASC
            """,
            params
        )

        weekdays = {
            0: "Sunday",
            1: "Monday",
            2: "Tuesday",
            3: "Wednesday",
            4: "Thursday",
            5: "Friday",
            6: "Saturday"
        }

        return [
            {
                "weekday": weekdays[row["weekday_number"]],
                "weekday_number": row["weekday_number"],
                "total_visits": row["total_visits"]
            }
            for row in rows
        ]

    # ========================================================
    # 27. DOCTOR CONSULTATION STATISTICS
    # ========================================================

    @staticmethod
    def get_doctor_statistics(
        start_date=None,
        end_date=None
    ):

        condition, params = AnalyticsService.build_date_filter(
            "v.visit_date",
            start_date,
            end_date
        )

        return fetch_all(
            """
            SELECT
                d.id AS doctor_id,
                d.name AS doctor_name,
                COUNT(v.id) AS total_visits,
                COALESCE(
                    SUM(
                        CASE
                            WHEN v.status = 'Completed'
                            THEN 1 ELSE 0
                        END
                    ),
                    0
                ) AS completed_visits,
                COALESCE(
                    SUM(b.consultation_fee),
                    0
                ) AS consultation_fees,
                COALESCE(
                    SUM(b.total_amount),
                    0
                ) AS total_billing
            FROM doctors d
            LEFT JOIN visits v
                ON v.doctor_id = d.id
                """ + condition + """
            LEFT JOIN bills b
                ON b.visit_id = v.id
            GROUP BY d.id, d.name
            ORDER BY total_visits DESC, d.name ASC
            """,
            params
        )

    # ========================================================
    # 28. PATIENT VISIT FREQUENCY
    # ========================================================

    @staticmethod
    def get_patient_visit_frequency(
        start_date=None,
        end_date=None,
        limit=20
    ):

        limit = int(limit)

        if limit < 1:
            raise ValueError("Limit must be positive.")

        condition, params = AnalyticsService.build_date_filter(
            "v.visit_date",
            start_date,
            end_date
        )

        return fetch_all(
            """
            SELECT
                p.id AS patient_id,
                p.name AS patient_name,
                p.mobile,
                COUNT(v.id) AS total_visits,
                MAX(v.visit_date) AS last_visit
            FROM patients p
            JOIN visits v
                ON v.patient_id = p.id
            WHERE 1 = 1
            """ + condition + """
            GROUP BY p.id, p.name, p.mobile
            ORDER BY total_visits DESC, last_visit DESC
            LIMIT ?
            """,
            params + (limit,)
        )

    # ========================================================
    # 29. NEW VS RETURNING PATIENT VISITS
    # ========================================================

    @staticmethod
    def get_new_vs_returning_visits(
        start_date=None,
        end_date=None
    ):

        condition, params = AnalyticsService.build_date_filter(
            "v.visit_date",
            start_date,
            end_date
        )

        result = fetch_one(
            """
            SELECT
                COUNT(*) AS total_visits,
                COALESCE(
                    SUM(
                        CASE
                            WHEN v.id = (
                                SELECT MIN(v2.id)
                                FROM visits v2
                                WHERE v2.patient_id = v.patient_id
                            )
                            THEN 1 ELSE 0
                        END
                    ),
                    0
                ) AS first_visits
            FROM visits v
            WHERE 1 = 1
            """ + condition,
            params
        )

        total = int(result["total_visits"] or 0)
        first = int(result["first_visits"] or 0)

        return {
            "total_visits": total,
            "new_patient_visits": first,
            "returning_patient_visits": total - first
        }

    # ========================================================
    # 30. RECENT VISITS
    # ========================================================

    @staticmethod
    def get_recent_visits(limit=10):

        limit = int(limit)

        if limit < 1:
            raise ValueError("Limit must be positive.")

        return fetch_all(
            """
            SELECT
                v.id AS visit_id,
                v.visit_date,
                v.visit_time,
                v.token_number,
                v.status,
                p.id AS patient_id,
                p.name AS patient_name,
                p.mobile,
                d.name AS doctor_name
            FROM visits v
            JOIN patients p
                ON p.id = v.patient_id
            LEFT JOIN doctors d
                ON d.id = v.doctor_id
            ORDER BY
                v.visit_date DESC,
                v.token_sequence DESC
            LIMIT ?
            """,
            (limit,)
        )

    # ========================================================
    # 31. RECENT PAYMENTS
    # ========================================================

    @staticmethod
    def get_recent_payments(limit=10):

        limit = int(limit)

        if limit < 1:
            raise ValueError("Limit must be positive.")

        return fetch_all(
            """
            SELECT
                pay.id AS payment_id,
                pay.amount,
                pay.payment_method,
                pay.payment_reference,
                pay.paid_at,
                b.bill_number,
                p.name AS patient_name,
                v.token_number
            FROM payments pay
            JOIN bills b
                ON b.id = pay.bill_id
            JOIN visits v
                ON v.id = b.visit_id
            JOIN patients p
                ON p.id = v.patient_id
            ORDER BY pay.id DESC
            LIMIT ?
            """,
            (limit,)
        )

    # ========================================================
    # 32. BILLING SUMMARY
    # ========================================================

    @staticmethod
    def get_billing_summary(
        start_date=None,
        end_date=None
    ):

        condition, params = AnalyticsService.build_date_filter(
            "b.created_at",
            start_date,
            end_date
        )

        result = fetch_one(
            """
            SELECT
                COUNT(*) AS total_bills,
                COALESCE(
                    SUM(b.total_amount), 0
                ) AS total_billing,
                COALESCE(
                    SUM(
                        CASE
                            WHEN b.payment_status = 'Paid'
                            THEN 1 ELSE 0
                        END
                    ),
                    0
                ) AS paid_bills,
                COALESCE(
                    SUM(
                        CASE
                            WHEN b.payment_status = 'Unpaid'
                            THEN 1 ELSE 0
                        END
                    ),
                    0
                ) AS unpaid_bills,
                COALESCE(
                    SUM(
                        CASE
                            WHEN b.payment_status = 'Partial'
                            THEN 1 ELSE 0
                        END
                    ),
                    0
                ) AS partial_bills
            FROM bills b
            WHERE 1 = 1
            """ + condition,
            params
        )

        return {
            "total_bills": int(result["total_bills"] or 0),
            "total_billing": float(
                result["total_billing"] or 0
            ),
            "paid_bills": int(result["paid_bills"] or 0),
            "unpaid_bills": int(result["unpaid_bills"] or 0),
            "partial_bills": int(result["partial_bills"] or 0),
            "collected_revenue": AnalyticsService.get_total_revenue(
                start_date,
                end_date
            ),
            "outstanding_balance": (
                AnalyticsService.get_outstanding_balance(
                    start_date,
                    end_date
                )
            )
        }

    # ========================================================
    # 33. CONVERT DATA TO PANDAS DATAFRAME
    # ========================================================

    @staticmethod
    def to_dataframe(records):

        if not records:
            return pd.DataFrame()

        return pd.DataFrame(
            [dict(row) for row in records]
        )

    # ========================================================
    # 34. FILL MISSING DATES
    # ========================================================

    @staticmethod
    def fill_missing_dates(
        records,
        start_date,
        end_date,
        date_column="day",
        value_column="total_visits"
    ):

        start_date, end_date = (
            AnalyticsService.validate_date_range(
                start_date,
                end_date
            )
        )

        if not start_date or not end_date:
            raise ValueError(
                "Start date and end date are required."
            )

        dates = pd.date_range(
            start=start_date,
            end=end_date,
            freq="D"
        )

        if not records:

            return pd.DataFrame({
                date_column: dates.strftime("%Y-%m-%d"),
                value_column: [0] * len(dates)
            })

        dataframe = AnalyticsService.to_dataframe(records)

        if date_column not in dataframe.columns:
            raise ValueError(
                f"Missing date column: {date_column}"
            )

        if value_column not in dataframe.columns:
            raise ValueError(
                f"Missing value column: {value_column}"
            )

        dataframe[date_column] = pd.to_datetime(
            dataframe[date_column],
            errors="coerce"
        )

        dataframe[value_column] = pd.to_numeric(
            dataframe[value_column],
            errors="coerce"
        ).fillna(0)

        dataframe = dataframe.dropna(
            subset=[date_column]
        )

        dataframe = (
            dataframe.groupby(date_column)[value_column]
            .sum()
            .reindex(dates, fill_value=0)
            .reset_index()
        )

        dataframe.columns = [
            date_column,
            value_column
        ]

        dataframe[date_column] = dataframe[
            date_column
        ].dt.strftime("%Y-%m-%d")

        return dataframe

    # ========================================================
    # 35. DAILY VISIT DATAFRAME
    # ========================================================

    @staticmethod
    def get_daily_visits_dataframe(
        start_date=None,
        end_date=None,
        fill_dates=True
    ):

        if start_date is None:
            start_date = (
                date.today() - timedelta(days=29)
            ).isoformat()

        if end_date is None:
            end_date = date.today().isoformat()

        records = AnalyticsService.get_daily_patient_visits(
            start_date,
            end_date
        )

        if fill_dates:

            return AnalyticsService.fill_missing_dates(
                records,
                start_date,
                end_date,
                date_column="day",
                value_column="total_visits"
            )

        return AnalyticsService.to_dataframe(records)

    # ========================================================
    # 36. DAILY REVENUE DATAFRAME
    # ========================================================

    @staticmethod
    def get_daily_revenue_dataframe(
        start_date=None,
        end_date=None,
        fill_dates=True
    ):

        if start_date is None:
            start_date = (
                date.today() - timedelta(days=29)
            ).isoformat()

        if end_date is None:
            end_date = date.today().isoformat()

        records = AnalyticsService.get_daily_revenue(
            start_date,
            end_date
        )

        if fill_dates:

            return AnalyticsService.fill_missing_dates(
                records,
                start_date,
                end_date,
                date_column="day",
                value_column="revenue"
            )

        return AnalyticsService.to_dataframe(records)

    # ========================================================
    # 37. PATIENT VISIT GROWTH
    # ========================================================

    @staticmethod
    def get_visit_growth(days=30):

        days = int(days)

        if days < 1:
            raise ValueError("Days must be positive.")

        today = date.today()

        current_start = today - timedelta(days=days - 1)

        previous_end = current_start - timedelta(days=1)

        previous_start = previous_end - timedelta(days=days - 1)

        current_visits = AnalyticsService.get_total_visits(
            current_start.isoformat(),
            today.isoformat()
        )

        previous_visits = AnalyticsService.get_total_visits(
            previous_start.isoformat(),
            previous_end.isoformat()
        )

        if previous_visits > 0:

            growth = (
                (current_visits - previous_visits)
                / previous_visits
            ) * 100

        elif current_visits > 0:

            growth = 100.0

        else:

            growth = 0.0

        return {
            "current_visits": current_visits,
            "previous_visits": previous_visits,
            "growth_percentage": round(growth, 2)
        }

    # ========================================================
    # 38. REVENUE GROWTH
    # ========================================================

    @staticmethod
    def get_revenue_growth(days=30):

        days = int(days)

        if days < 1:
            raise ValueError("Days must be positive.")

        today = date.today()

        current_start = today - timedelta(days=days - 1)

        previous_end = current_start - timedelta(days=1)

        previous_start = previous_end - timedelta(days=days - 1)

        current_revenue = AnalyticsService.get_total_revenue(
            current_start.isoformat(),
            today.isoformat()
        )

        previous_revenue = AnalyticsService.get_total_revenue(
            previous_start.isoformat(),
            previous_end.isoformat()
        )

        if previous_revenue > 0:

            growth = (
                (current_revenue - previous_revenue)
                / previous_revenue
            ) * 100

        elif current_revenue > 0:

            growth = 100.0

        else:

            growth = 0.0

        return {
            "current_revenue": current_revenue,
            "previous_revenue": previous_revenue,
            "growth_percentage": round(growth, 2)
        }

    # ========================================================
    # 39. AVERAGE BILL VALUE
    # ========================================================

    @staticmethod
    def get_average_bill_value(
        start_date=None,
        end_date=None
    ):

        condition, params = AnalyticsService.build_date_filter(
            "b.created_at",
            start_date,
            end_date
        )

        result = fetch_one(
            """
            SELECT
                COALESCE(
                    AVG(b.total_amount),
                    0
                ) AS average_bill
            FROM bills b
            WHERE 1 = 1
            """ + condition,
            params
        )

        return round(
            float(result["average_bill"] or 0),
            2
        ) if result else 0.0

    # ========================================================
    # 40. CONSULTATION COMPLETION RATE
    # ========================================================

    @staticmethod
    def get_completion_rate(
        start_date=None,
        end_date=None
    ):

        condition, params = AnalyticsService.build_date_filter(
            "v.visit_date",
            start_date,
            end_date
        )

        result = fetch_one(
            """
            SELECT
                COUNT(*) AS total,
                COALESCE(
                    SUM(
                        CASE
                            WHEN v.status = 'Completed'
                            THEN 1 ELSE 0
                        END
                    ),
                    0
                ) AS completed
            FROM visits v
            WHERE 1 = 1
            """ + condition,
            params
        )

        total = int(result["total"] or 0)
        completed = int(result["completed"] or 0)

        percentage = (
            (completed / total) * 100
            if total > 0
            else 0.0
        )

        return {
            "total_visits": total,
            "completed_visits": completed,
            "completion_percentage": round(
                percentage,
                2
            )
        }

    # ========================================================
    # 41. COMPLETE ANALYTICS DATA
    # ========================================================

    @staticmethod
    def get_complete_analytics(
        start_date=None,
        end_date=None
    ):

        start_date, end_date = (
            AnalyticsService.validate_date_range(
                start_date,
                end_date
            )
        )

        return {
            "overview": AnalyticsService.get_overview(
                start_date,
                end_date
            ),
            "billing_summary": (
                AnalyticsService.get_billing_summary(
                    start_date,
                    end_date
                )
            ),
            "daily_visits": (
                AnalyticsService.get_daily_patient_visits(
                    start_date,
                    end_date
                )
            ),
            "monthly_visits": (
                AnalyticsService.get_monthly_patient_visits(
                    start_date,
                    end_date
                )
            ),
            "daily_revenue": (
                AnalyticsService.get_daily_revenue(
                    start_date,
                    end_date
                )
            ),
            "monthly_revenue": (
                AnalyticsService.get_monthly_revenue(
                    start_date,
                    end_date
                )
            ),
            "gender_distribution": (
                AnalyticsService.get_gender_distribution(
                    start_date,
                    end_date
                )
            ),
            "token_status_distribution": (
                AnalyticsService.get_token_status_distribution(
                    start_date,
                    end_date
                )
            ),
            "payment_method_distribution": (
                AnalyticsService.get_payment_method_distribution(
                    start_date,
                    end_date
                )
            ),
            "payment_status_distribution": (
                AnalyticsService.get_payment_status_distribution(
                    start_date,
                    end_date
                )
            ),
            "fee_breakdown": (
                AnalyticsService.get_fee_breakdown(
                    start_date,
                    end_date
                )
            ),
            "hourly_visits": (
                AnalyticsService.get_hourly_visits(
                    start_date,
                    end_date
                )
            ),
            "weekday_distribution": (
                AnalyticsService.get_weekday_distribution(
                    start_date,
                    end_date
                )
            ),
            "doctor_statistics": (
                AnalyticsService.get_doctor_statistics(
                    start_date,
                    end_date
                )
            ),
            "new_vs_returning": (
                AnalyticsService.get_new_vs_returning_visits(
                    start_date,
                    end_date
                )
            ),
            "completion_rate": (
                AnalyticsService.get_completion_rate(
                    start_date,
                    end_date
                )
            ),
            "average_bill_value": (
                AnalyticsService.get_average_bill_value(
                    start_date,
                    end_date
                )
            )
        }


# ============================================================
# END OF FILE
# ============================================================
