# ============================================================
# HOSPITAL RECEPTION SYSTEM
# FILE: models/doctor_model.py
# PURPOSE: Doctor Database Operations and Authentication
# DATABASE: SQLite3
# ============================================================

import hashlib
import hmac
import secrets
import sqlite3

from database import (
    fetch_one,
    fetch_all,
    insert_record,
    execute_query
)


class DoctorModel:

    # ========================================================
    # 1. PASSWORD HASHING
    # ========================================================

    @staticmethod
    def hash_password(password):

        if not isinstance(password, str) or not password:
            raise ValueError("Password is required.")

        salt = secrets.token_hex(16)
        iterations = 600000

        hashed_password = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            bytes.fromhex(salt),
            iterations
        ).hex()

        return (
            f"pbkdf2_sha256${iterations}$"
            f"{salt}${hashed_password}"
        )

    # ========================================================
    # 2. VERIFY PASSWORD
    # ========================================================

    @staticmethod
    def verify_password(password, stored_hash):

        if not isinstance(password, str):
            return False

        if not isinstance(stored_hash, str):
            return False

        try:

            algorithm, iterations, salt, expected_hash = (
                stored_hash.split("$")
            )

            if algorithm != "pbkdf2_sha256":
                return False

            iterations = int(iterations)

            if iterations < 100000 or iterations > 2000000:
                return False

            calculated_hash = hashlib.pbkdf2_hmac(
                "sha256",
                password.encode("utf-8"),
                bytes.fromhex(salt),
                iterations
            )

            return hmac.compare_digest(
                calculated_hash,
                bytes.fromhex(expected_hash)
            )

        except (ValueError, TypeError, OverflowError):
            return False

    # ========================================================
    # 3. VALIDATE DOCTOR DETAILS
    # ========================================================

    @staticmethod
    def validate_name(name):

        return isinstance(name, str) and bool(name.strip())

    @staticmethod
    def validate_email(email):

        if not isinstance(email, str):
            return False

        email = email.strip()

        return (
            "@" in email
            and "." in email.split("@")[-1]
            and " " not in email
            and len(email) <= 254
        )

    @staticmethod
    def validate_password(password):

        return (
            isinstance(password, str)
            and len(password) >= 8
        )

    # ========================================================
    # 4. CREATE DOCTOR
    # ========================================================

    @staticmethod
    def create_doctor(name, email, password):

        name = str(name).strip()
        email = str(email).strip().lower()

        if not DoctorModel.validate_name(name):
            raise ValueError("Doctor name is required.")

        if not DoctorModel.validate_email(email):
            raise ValueError("Invalid email address.")

        if not DoctorModel.validate_password(password):
            raise ValueError(
                "Password must contain at least 8 characters."
            )

        existing = DoctorModel.get_by_email(email)

        if existing:
            raise ValueError(
                "A doctor with this email already exists."
            )

        password_hash = DoctorModel.hash_password(password)

        try:

            return insert_record(
                """
                INSERT INTO doctors (
                    name,
                    email,
                    password_hash,
                    status
                )
                VALUES (?, ?, ?, 'Active')
                """,
                (
                    name,
                    email,
                    password_hash
                )
            )

        except sqlite3.IntegrityError as error:

            raise ValueError(
                "Unable to create doctor account."
            ) from error

    # ========================================================
    # 5. GET DOCTOR BY ID
    # ========================================================

    @staticmethod
    def get_by_id(doctor_id):

        return fetch_one(
            """
            SELECT
                id,
                name,
                email,
                status,
                created_at
            FROM doctors
            WHERE id = ?
            LIMIT 1
            """,
            (doctor_id,)
        )

    # ========================================================
    # 6. GET DOCTOR BY EMAIL
    # ========================================================

    @staticmethod
    def get_by_email(email):

        email = str(email).strip().lower()

        return fetch_one(
            """
            SELECT
                id,
                name,
                email,
                status,
                created_at
            FROM doctors
            WHERE LOWER(email) = ?
            LIMIT 1
            """,
            (email,)
        )

    # ========================================================
    # 7. AUTHENTICATE DOCTOR
    # ========================================================

    @staticmethod
    def authenticate(email, password):

        email = str(email).strip().lower()

        if not DoctorModel.validate_email(email):
            return None

        if not isinstance(password, str) or not password:
            return None

        doctor = fetch_one(
            """
            SELECT
                id,
                name,
                email,
                password_hash,
                status
            FROM doctors
            WHERE LOWER(email) = ?
            LIMIT 1
            """,
            (email,)
        )

        if not doctor:
            return None

        if doctor["status"] != "Active":
            return None

        if not DoctorModel.verify_password(
            password,
            doctor["password_hash"]
        ):
            return None

        return {
            "id": doctor["id"],
            "name": doctor["name"],
            "email": doctor["email"],
            "status": doctor["status"]
        }

    # ========================================================
    # 8. GET ALL DOCTORS
    # ========================================================

    @staticmethod
    def get_all(status=None):

        if status is not None:

            if status not in ("Active", "Inactive"):
                raise ValueError("Invalid doctor status.")

            return fetch_all(
                """
                SELECT
                    id,
                    name,
                    email,
                    status,
                    created_at
                FROM doctors
                WHERE status = ?
                ORDER BY name ASC
                """,
                (status,)
            )

        return fetch_all(
            """
            SELECT
                id,
                name,
                email,
                status,
                created_at
            FROM doctors
            ORDER BY name ASC
            """
        )

    # ========================================================
    # 9. GET ACTIVE DOCTORS
    # ========================================================

    @staticmethod
    def get_active_doctors():

        return DoctorModel.get_all("Active")

    # ========================================================
    # 10. SEARCH DOCTORS
    # ========================================================

    @staticmethod
    def search(search_text):

        search_text = str(search_text).strip()

        if not search_text:
            return DoctorModel.get_all()

        pattern = f"%{search_text}%"

        return fetch_all(
            """
            SELECT
                id,
                name,
                email,
                status,
                created_at
            FROM doctors
            WHERE
                CAST(id AS TEXT) LIKE ?
                OR name LIKE ?
                OR email LIKE ?
            ORDER BY name ASC
            """,
            (
                pattern,
                pattern,
                pattern
            )
        )

    # ========================================================
    # 11. UPDATE DOCTOR DETAILS
    # ========================================================

    @staticmethod
    def update_doctor(doctor_id, name, email):

        name = str(name).strip()
        email = str(email).strip().lower()

        if not DoctorModel.validate_name(name):
            raise ValueError("Doctor name is required.")

        if not DoctorModel.validate_email(email):
            raise ValueError("Invalid email address.")

        doctor = DoctorModel.get_by_id(doctor_id)

        if not doctor:
            raise ValueError("Doctor not found.")

        existing = DoctorModel.get_by_email(email)

        if existing and existing["id"] != int(doctor_id):
            raise ValueError(
                "Email address belongs to another doctor."
            )

        try:

            return execute_query(
                """
                UPDATE doctors
                SET
                    name = ?,
                    email = ?
                WHERE id = ?
                """,
                (
                    name,
                    email,
                    doctor_id
                )
            )

        except sqlite3.IntegrityError as error:

            raise ValueError(
                "Unable to update doctor details."
            ) from error

    # ========================================================
    # 12. CHANGE PASSWORD
    # ========================================================

    @staticmethod
    def change_password(
        doctor_id,
        current_password,
        new_password
    ):

        if not DoctorModel.validate_password(new_password):
            raise ValueError(
                "New password must contain at least 8 characters."
            )

        doctor = fetch_one(
            """
            SELECT
                id,
                password_hash,
                status
            FROM doctors
            WHERE id = ?
            LIMIT 1
            """,
            (doctor_id,)
        )

        if not doctor:
            raise ValueError("Doctor account not found.")

        if doctor["status"] != "Active":
            raise ValueError("Doctor account is inactive.")

        if not DoctorModel.verify_password(
            current_password,
            doctor["password_hash"]
        ):
            raise ValueError("Current password is incorrect.")

        if current_password == new_password:
            raise ValueError(
                "New password must be different."
            )

        new_hash = DoctorModel.hash_password(new_password)

        updated = execute_query(
            """
            UPDATE doctors
            SET password_hash = ?
            WHERE id = ?
              AND password_hash = ?
            """,
            (
                new_hash,
                doctor_id,
                doctor["password_hash"]
            )
        )

        return updated > 0

    # ========================================================
    # 13. RESET DOCTOR PASSWORD
    # ========================================================

    @staticmethod
    def reset_password(doctor_id, new_password):
        """
        Administrative password reset.

        This method must only be called from a trusted,
        administrator-authorized workflow.
        """

        if not DoctorModel.validate_password(new_password):
            raise ValueError(
                "Password must contain at least 8 characters."
            )

        doctor = DoctorModel.get_by_id(doctor_id)

        if not doctor:
            raise ValueError("Doctor not found.")

        password_hash = DoctorModel.hash_password(new_password)

        return execute_query(
            """
            UPDATE doctors
            SET password_hash = ?
            WHERE id = ?
            """,
            (
                password_hash,
                doctor_id
            )
        )

    # ========================================================
    # 14. UPDATE DOCTOR STATUS
    # ========================================================

    @staticmethod
    def update_status(doctor_id, status):
        """
        Administrative status change.

        Call only after administrator authorization.
        """

        if status not in ("Active", "Inactive"):
            raise ValueError(
                "Status must be Active or Inactive."
            )

        doctor = DoctorModel.get_by_id(doctor_id)

        if not doctor:
            raise ValueError("Doctor not found.")

        return execute_query(
            """
            UPDATE doctors
            SET status = ?
            WHERE id = ?
            """,
            (
                status,
                doctor_id
            )
        )

    # ========================================================
    # 15. CHECK ACTIVE STATUS
    # ========================================================

    @staticmethod
    def is_active(doctor_id):

        doctor = DoctorModel.get_by_id(doctor_id)

        return bool(
            doctor and doctor["status"] == "Active"
        )

    # ========================================================
    # 16. COUNT ALL DOCTORS
    # ========================================================

    @staticmethod
    def count_all():

        result = fetch_one(
            """
            SELECT COUNT(*) AS total
            FROM doctors
            """
        )

        return result["total"] if result else 0

    # ========================================================
    # 17. COUNT ACTIVE DOCTORS
    # ========================================================

    @staticmethod
    def count_active():

        result = fetch_one(
            """
            SELECT COUNT(*) AS total
            FROM doctors
            WHERE status = 'Active'
            """
        )

        return result["total"] if result else 0

    # ========================================================
    # 18. GET DOCTOR CONSULTATIONS
    # ========================================================

    @staticmethod
    def get_consultations(
        doctor_id,
        start_date=None,
        end_date=None
    ):

        query = """
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

                b.id AS bill_id,
                b.bill_number,
                b.consultation_fee,
                b.medicine_fee,
                b.other_charges,
                b.total_amount,
                b.payment_status

            FROM visits v

            JOIN patients p
                ON p.id = v.patient_id

            LEFT JOIN bills b
                ON b.visit_id = v.id

            WHERE v.doctor_id = ?
        """

        params = [doctor_id]

        if start_date:
            query += " AND v.visit_date >= ?"
            params.append(str(start_date))

        if end_date:
            query += " AND v.visit_date <= ?"
            params.append(str(end_date))

        query += """
            ORDER BY
                v.visit_date DESC,
                v.token_sequence DESC
        """

        return fetch_all(query, tuple(params))

    # ========================================================
    # 19. GET DOCTOR CONSULTATION STATISTICS
    # ========================================================

    @staticmethod
    def get_consultation_statistics(
        doctor_id,
        start_date=None,
        end_date=None
    ):

        query = """
            SELECT
                COUNT(v.id) AS total_visits,

                COALESCE(
                    SUM(
                        CASE
                            WHEN v.status = 'Waiting'
                            THEN 1
                            ELSE 0
                        END
                    ),
                    0
                ) AS waiting_visits,

                COALESCE(
                    SUM(
                        CASE
                            WHEN v.status = 'In Progress'
                            THEN 1
                            ELSE 0
                        END
                    ),
                    0
                ) AS in_progress_visits,

                COALESCE(
                    SUM(
                        CASE
                            WHEN v.status = 'Completed'
                            THEN 1
                            ELSE 0
                        END
                    ),
                    0
                ) AS completed_visits,

                COALESCE(
                    SUM(
                        CASE
                            WHEN v.status = 'Cancelled'
                            THEN 1
                            ELSE 0
                        END
                    ),
                    0
                ) AS cancelled_visits,

                COALESCE(
                    SUM(b.consultation_fee),
                    0
                ) AS total_consultation_fees,

                COALESCE(
                    SUM(b.total_amount),
                    0
                ) AS total_billing

            FROM visits v

            LEFT JOIN bills b
                ON b.visit_id = v.id

            WHERE v.doctor_id = ?
        """

        params = [doctor_id]

        if start_date:
            query += " AND v.visit_date >= ?"
            params.append(str(start_date))

        if end_date:
            query += " AND v.visit_date <= ?"
            params.append(str(end_date))

        result = fetch_one(query, tuple(params))

        return result or {
            "total_visits": 0,
            "waiting_visits": 0,
            "in_progress_visits": 0,
            "completed_visits": 0,
            "cancelled_visits": 0,
            "total_consultation_fees": 0,
            "total_billing": 0
        }

    # ========================================================
    # 20. GET DOCTOR REVENUE
    # ========================================================

    @staticmethod
    def get_revenue(
        doctor_id,
        start_date=None,
        end_date=None
    ):

        query = """
            SELECT
                COALESCE(SUM(pay.amount), 0) AS total_revenue

            FROM payments pay

            JOIN bills b
                ON b.id = pay.bill_id

            JOIN visits v
                ON v.id = b.visit_id

            WHERE v.doctor_id = ?
        """

        params = [doctor_id]

        if start_date:
            query += " AND DATE(pay.paid_at) >= ?"
            params.append(str(start_date))

        if end_date:
            query += " AND DATE(pay.paid_at) <= ?"
            params.append(str(end_date))

        result = fetch_one(query, tuple(params))

        return float(
            result["total_revenue"] or 0
        ) if result else 0.0

    # ========================================================
    # 21. GET DOCTOR SUMMARY
    # ========================================================

    @staticmethod
    def get_doctor_summary(doctor_id):

        doctor = DoctorModel.get_by_id(doctor_id)

        if not doctor:
            return None

        statistics = DoctorModel.get_consultation_statistics(
            doctor_id
        )

        summary = dict(doctor)

        summary.update(statistics)

        summary["total_revenue"] = DoctorModel.get_revenue(
            doctor_id
        )

        return summary


# ============================================================
# END OF FILE
# ============================================================
