# ============================================================
# HOSPITAL RECEPTION SYSTEM
# FILE: models/patient_model.py
# PURPOSE: Patient Database Operations
# DATABASE: SQLite3
# ============================================================

import sqlite3
from datetime import date

from database import (
    fetch_one,
    fetch_all,
    insert_record,
    execute_query,
    get_connection
)


class PatientModel:

    # ========================================================
    # 1. VALIDATION
    # ========================================================

    @staticmethod
    def validate_mobile(mobile):

        mobile = str(mobile).strip()

        return (
            len(mobile) == 10
            and all(character in "0123456789" for character in mobile)
        )

    @staticmethod
    def validate_name(name):

        return bool(str(name).strip())

    @staticmethod
    def validate_gender(gender):

        return gender in ("Male", "Female", "Other")

    # ========================================================
    # 2. CREATE PATIENT
    # ========================================================

    @staticmethod
    def create_patient(name, mobile, gender):

        name = str(name).strip()
        mobile = str(mobile).strip()
        gender = str(gender).strip()

        if not PatientModel.validate_name(name):
            raise ValueError("Patient name is required.")

        if not PatientModel.validate_mobile(mobile):
            raise ValueError(
                "Mobile number must contain exactly 10 digits."
            )

        if not PatientModel.validate_gender(gender):
            raise ValueError("Invalid gender selected.")

        existing = PatientModel.get_by_mobile(mobile)

        if existing:
            raise ValueError(
                "A patient with this mobile number already exists."
            )

        try:

            patient_id = insert_record(
                """
                INSERT INTO patients (
                    name,
                    mobile,
                    gender
                )
                VALUES (?, ?, ?)
                """,
                (name, mobile, gender)
            )

            return patient_id

        except sqlite3.IntegrityError as error:

            raise ValueError(
                "Patient already exists or details are invalid."
            ) from error

    # ========================================================
    # 3. FIND PATIENT BY ID
    # ========================================================

    @staticmethod
    def get_by_id(patient_id):

        return fetch_one(
            """
            SELECT
                id,
                name,
                mobile,
                gender,
                created_at
            FROM patients
            WHERE id = ?
            LIMIT 1
            """,
            (patient_id,)
        )

    # ========================================================
    # 4. FIND PATIENT BY MOBILE
    # ========================================================

    @staticmethod
    def get_by_mobile(mobile):

        mobile = str(mobile).strip()

        return fetch_one(
            """
            SELECT
                id,
                name,
                mobile,
                gender,
                created_at
            FROM patients
            WHERE mobile = ?
            LIMIT 1
            """,
            (mobile,)
        )

    # ========================================================
    # 5. CHECK PATIENT EXISTS
    # ========================================================

    @staticmethod
    def exists(mobile):

        return PatientModel.get_by_mobile(mobile) is not None

    # ========================================================
    # 6. GET ALL PATIENTS
    # ========================================================

    @staticmethod
    def get_all(limit=None):

        query = """
            SELECT
                id,
                name,
                mobile,
                gender,
                created_at
            FROM patients
            ORDER BY id DESC
        """

        if limit is not None:

            limit = int(limit)

            if limit < 1:
                raise ValueError("Limit must be positive.")

            return fetch_all(
                query + " LIMIT ?",
                (limit,)
            )

        return fetch_all(query)

    # ========================================================
    # 7. SEARCH PATIENTS
    # ========================================================

    @staticmethod
    def search(search_text):

        search_text = str(search_text).strip()

        if not search_text:
            return PatientModel.get_all()

        pattern = f"%{search_text}%"

        return fetch_all(
            """
            SELECT
                id,
                name,
                mobile,
                gender,
                created_at
            FROM patients
            WHERE
                CAST(id AS TEXT) LIKE ?
                OR name LIKE ?
                OR mobile LIKE ?
            ORDER BY id DESC
            """,
            (pattern, pattern, pattern)
        )

    # ========================================================
    # 8. UPDATE PATIENT
    # ========================================================

    @staticmethod
    def update_patient(patient_id, name, mobile, gender):

        name = str(name).strip()
        mobile = str(mobile).strip()
        gender = str(gender).strip()

        if not PatientModel.validate_name(name):
            raise ValueError("Patient name is required.")

        if not PatientModel.validate_mobile(mobile):
            raise ValueError("Invalid mobile number.")

        if not PatientModel.validate_gender(gender):
            raise ValueError("Invalid gender.")

        patient = PatientModel.get_by_id(patient_id)

        if not patient:
            raise ValueError("Patient not found.")

        existing = PatientModel.get_by_mobile(mobile)

        if existing and existing["id"] != int(patient_id):
            raise ValueError(
                "Mobile number belongs to another patient."
            )

        try:

            return execute_query(
                """
                UPDATE patients
                SET
                    name = ?,
                    mobile = ?,
                    gender = ?
                WHERE id = ?
                """,
                (
                    name,
                    mobile,
                    gender,
                    patient_id
                )
            )

        except sqlite3.IntegrityError as error:

            raise ValueError(
                "Unable to update patient details."
            ) from error

    # ========================================================
    # 9. COUNT PATIENTS
    # ========================================================

    @staticmethod
    def count_all():

        result = fetch_one(
            """
            SELECT COUNT(*) AS total
            FROM patients
            """
        )

        return result["total"] if result else 0

    # ========================================================
    # 10. COUNT TODAY'S NEW PATIENTS
    # ========================================================

    @staticmethod
    def count_today():

        result = fetch_one(
            """
            SELECT COUNT(*) AS total
            FROM patients
            WHERE DATE(created_at, 'localtime') = ?
            """,
            (date.today().isoformat(),)
        )

        return result["total"] if result else 0

    # ========================================================
    # 11. PATIENT VISIT HISTORY
    # ========================================================

    @staticmethod
    def get_visit_history(patient_id):

        return fetch_all(
            """
            SELECT
                v.id AS visit_id,
                v.token_number,
                v.token_sequence,
                v.visit_date,
                v.visit_time,
                v.status,
                v.completed_at,

                d.id AS doctor_id,
                d.name AS doctor_name,

                b.id AS bill_id,
                b.bill_number,
                b.consultation_fee,
                b.medicine_fee,
                b.other_charges,
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
                v.token_sequence DESC
            """,
            (patient_id,)
        )

    # ========================================================
    # 12. COUNT PATIENT VISITS
    # ========================================================

    @staticmethod
    def count_visits(patient_id):

        result = fetch_one(
            """
            SELECT COUNT(*) AS total
            FROM visits
            WHERE patient_id = ?
            """,
            (patient_id,)
        )

        return result["total"] if result else 0

    # ========================================================
    # 13. GET PATIENT'S LATEST VISIT
    # ========================================================

    @staticmethod
    def get_latest_visit(patient_id):

        return fetch_one(
            """
            SELECT
                v.id,
                v.patient_id,
                v.doctor_id,
                v.token_number,
                v.token_sequence,
                v.visit_date,
                v.visit_time,
                v.status,
                v.completed_at,

                d.name AS doctor_name

            FROM visits v

            LEFT JOIN doctors d
                ON d.id = v.doctor_id

            WHERE v.patient_id = ?

            ORDER BY
                v.visit_date DESC,
                v.id DESC

            LIMIT 1
            """,
            (patient_id,)
        )

    # ========================================================
    # 14. GET TODAY'S VISIT
    # ========================================================

    @staticmethod
    def get_today_visit(patient_id):

        return fetch_one(
            """
            SELECT
                id,
                patient_id,
                doctor_id,
                token_number,
                token_sequence,
                visit_date,
                visit_time,
                status,
                completed_at

            FROM visits

            WHERE patient_id = ?
              AND visit_date = ?
              AND status IN ('Waiting', 'In Progress')

            ORDER BY id DESC

            LIMIT 1
            """,
            (
                patient_id,
                date.today().isoformat()
            )
        )

    # ========================================================
    # 15. PATIENT REGISTRATION REPORT
    # ========================================================

    @staticmethod
    def get_registration_report(start_date=None, end_date=None):

        query = """
            SELECT
                id,
                name,
                mobile,
                gender,
                created_at
            FROM patients
            WHERE 1 = 1
        """

        params = []

        if start_date:
            query += " AND DATE(created_at, 'localtime') >= ?"
            params.append(str(start_date))

        if end_date:
            query += " AND DATE(created_at, 'localtime') <= ?"
            params.append(str(end_date))

        query += " ORDER BY created_at DESC, id DESC"

        return fetch_all(query, tuple(params))

    # ========================================================
    # 16. PATIENT GENDER STATISTICS
    # ========================================================

    @staticmethod
    def get_gender_statistics():

        return fetch_all(
            """
            SELECT
                gender,
                COUNT(*) AS total
            FROM patients
            GROUP BY gender
            ORDER BY gender
            """
        )

    # ========================================================
    # 17. DAILY PATIENT REGISTRATION STATISTICS
    # ========================================================

    @staticmethod
    def get_daily_registration_statistics(
        start_date=None,
        end_date=None
    ):

        query = """
            SELECT
                DATE(created_at, 'localtime') AS registration_date,
                COUNT(*) AS total_patients
            FROM patients
            WHERE 1 = 1
        """

        params = []

        if start_date:
            query += " AND DATE(created_at, 'localtime') >= ?"
            params.append(str(start_date))

        if end_date:
            query += " AND DATE(created_at, 'localtime') <= ?"
            params.append(str(end_date))

        query += """
            GROUP BY DATE(created_at, 'localtime')
            ORDER BY registration_date ASC
        """

        return fetch_all(query, tuple(params))

    # ========================================================
    # 18. GET PATIENT SUMMARY
    # ========================================================

    @staticmethod
    def get_patient_summary(patient_id):

        patient = PatientModel.get_by_id(patient_id)

        if not patient:
            return None

        result = fetch_one(
            """
            SELECT
                COUNT(v.id) AS total_visits,

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

                MAX(v.visit_date) AS last_visit_date,

                COALESCE(
                    SUM(b.total_amount),
                    0
                ) AS total_billing

            FROM visits v

            LEFT JOIN bills b
                ON b.visit_id = v.id

            WHERE v.patient_id = ?
            """,
            (patient_id,)
        )

        summary = dict(patient)

        summary.update({
            "total_visits": result["total_visits"] if result else 0,
            "completed_visits": (
                result["completed_visits"] if result else 0
            ),
            "last_visit_date": (
                result["last_visit_date"] if result else None
            ),
            "total_billing": (
                result["total_billing"] if result else 0
            )
        })

        return summary

    # ========================================================
    # 19. REGISTER OR FIND PATIENT
    # ========================================================

    @staticmethod
    def get_or_create(name, mobile, gender):

        existing = PatientModel.get_by_mobile(mobile)

        if existing:
            return existing["id"], False

        try:

            patient_id = PatientModel.create_patient(
                name,
                mobile,
                gender
            )

            return patient_id, True

        except ValueError:

            existing = PatientModel.get_by_mobile(mobile)

            if existing:
                return existing["id"], False

            raise


# ============================================================
# END OF FILE
# ============================================================
