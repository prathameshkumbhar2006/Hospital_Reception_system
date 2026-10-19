# ============================================================
# HOSPITAL RECEPTION SYSTEM
# FILE: models/token_model.py
# PURPOSE: Patient Token and Visit Database Operations
# DATABASE: SQLite3
# ============================================================

import sqlite3
from datetime import date, datetime

from database import (
    get_connection,
    fetch_one,
    fetch_all,
    execute_query
)

from config import (
    TOKEN_PREFIX,
    TOKEN_DIGITS,
    TOKEN_START_NUMBER
)


class TokenModel:

    VALID_STATUSES = (
        "Waiting",
        "In Progress",
        "Completed",
        "Cancelled"
    )

    ACTIVE_STATUSES = (
        "Waiting",
        "In Progress"
    )

    # ========================================================
    # 1. GENERATE TOKEN NUMBER
    # ========================================================

    @staticmethod
    def format_token(sequence):

        sequence = int(sequence)

        if sequence < 1:
            raise ValueError("Invalid token sequence.")

        return (
            f"{TOKEN_PREFIX}-"
            f"{sequence:0{TOKEN_DIGITS}d}"
        )

    # ========================================================
    # 2. GET TODAY'S DATE
    # ========================================================

    @staticmethod
    def today():

        return date.today().isoformat()

    # ========================================================
    # 3. GET CURRENT TIME
    # ========================================================

    @staticmethod
    def current_time():

        return datetime.now().strftime("%H:%M:%S")

    # ========================================================
    # 4. CREATE PATIENT TOKEN
    # ========================================================

    @staticmethod
    def create_token(patient_id, doctor_id=None):
        """
        Generate a daily token for a registered patient.

        Token generation is atomic to prevent duplicate
        sequence numbers when multiple kiosks are running.

        If the patient already has a Waiting or In Progress
        visit today, return that visit instead.
        """

        patient_id = int(patient_id)

        connection = get_connection()

        try:

            connection.execute("BEGIN IMMEDIATE")

            patient = connection.execute(
                """
                SELECT id, name, mobile
                FROM patients
                WHERE id = ?
                LIMIT 1
                """,
                (patient_id,)
            ).fetchone()

            if not patient:
                raise ValueError("Patient not found.")

            today = TokenModel.today()

            existing = connection.execute(
                """
                SELECT *
                FROM visits
                WHERE patient_id = ?
                  AND visit_date = ?
                  AND status IN ('Waiting', 'In Progress')
                ORDER BY id DESC
                LIMIT 1
                """,
                (patient_id, today)
            ).fetchone()

            if existing:

                connection.commit()

                return dict(existing)

            if doctor_id is not None:

                doctor = connection.execute(
                    """
                    SELECT id
                    FROM doctors
                    WHERE id = ?
                      AND status = 'Active'
                    LIMIT 1
                    """,
                    (doctor_id,)
                ).fetchone()

                if not doctor:
                    raise ValueError(
                        "Selected doctor is not active."
                    )

            # -----------------------------------------------
            # GET NEXT DAILY SEQUENCE
            # -----------------------------------------------

            counter = connection.execute(
                """
                SELECT last_sequence
                FROM daily_token_counters
                WHERE counter_date = ?
                """,
                (today,)
            ).fetchone()

            if counter:

                next_sequence = counter["last_sequence"] + 1

                connection.execute(
                    """
                    UPDATE daily_token_counters
                    SET last_sequence = ?
                    WHERE counter_date = ?
                    """,
                    (next_sequence, today)
                )

            else:

                next_sequence = max(
                    1,
                    int(TOKEN_START_NUMBER)
                )

                connection.execute(
                    """
                    INSERT INTO daily_token_counters (
                        counter_date,
                        last_sequence
                    )
                    VALUES (?, ?)
                    """,
                    (today, next_sequence)
                )

            token_number = TokenModel.format_token(
                next_sequence
            )

            # -----------------------------------------------
            # CREATE VISIT
            # -----------------------------------------------

            cursor = connection.execute(
                """
                INSERT INTO visits (
                    patient_id,
                    doctor_id,
                    token_number,
                    token_sequence,
                    visit_date,
                    visit_time,
                    status
                )
                VALUES (?, ?, ?, ?, ?, ?, 'Waiting')
                """,
                (
                    patient_id,
                    doctor_id,
                    token_number,
                    next_sequence,
                    today,
                    TokenModel.current_time()
                )
            )

            visit_id = cursor.lastrowid

            visit = connection.execute(
                """
                SELECT *
                FROM visits
                WHERE id = ?
                """,
                (visit_id,)
            ).fetchone()

            connection.commit()

            return dict(visit)

        except Exception:

            connection.rollback()
            raise

        finally:

            connection.close()

    # ========================================================
    # 5. GET TOKEN BY VISIT ID
    # ========================================================

    @staticmethod
    def get_by_id(visit_id):

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
                v.created_at,

                p.name AS patient_name,
                p.mobile,
                p.gender,

                d.name AS doctor_name

            FROM visits v

            JOIN patients p
                ON p.id = v.patient_id

            LEFT JOIN doctors d
                ON d.id = v.doctor_id

            WHERE v.id = ?

            LIMIT 1
            """,
            (visit_id,)
        )

    # ========================================================
    # 6. GET TOKEN BY NUMBER AND DATE
    # ========================================================

    @staticmethod
    def get_by_number(token_number, visit_date=None):

        if visit_date is None:
            visit_date = TokenModel.today()

        token_number = str(token_number).strip().upper()

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

                p.name AS patient_name,
                p.mobile,
                p.gender,

                d.name AS doctor_name

            FROM visits v

            JOIN patients p
                ON p.id = v.patient_id

            LEFT JOIN doctors d
                ON d.id = v.doctor_id

            WHERE UPPER(v.token_number) = ?
              AND v.visit_date = ?

            LIMIT 1
            """,
            (
                token_number,
                str(visit_date)
            )
        )

    # ========================================================
    # 7. GET TODAY'S TOKENS
    # ========================================================

    @staticmethod
    def get_today_tokens(status=None):

        return TokenModel.get_tokens_by_date(
            TokenModel.today(),
            status=status
        )

    # ========================================================
    # 8. GET TOKENS BY DATE
    # ========================================================

    @staticmethod
    def get_tokens_by_date(visit_date, status=None):

        query = """
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

                p.name AS patient_name,
                p.mobile,
                p.gender,

                d.name AS doctor_name

            FROM visits v

            JOIN patients p
                ON p.id = v.patient_id

            LEFT JOIN doctors d
                ON d.id = v.doctor_id

            WHERE v.visit_date = ?
        """

        params = [str(visit_date)]

        if status is not None:

            if status not in TokenModel.VALID_STATUSES:
                raise ValueError("Invalid token status.")

            query += " AND v.status = ?"
            params.append(status)

        query += """
            ORDER BY v.token_sequence ASC
        """

        return fetch_all(query, tuple(params))

    # ========================================================
    # 9. GET TOKENS BY DATE RANGE
    # ========================================================

    @staticmethod
    def get_tokens_by_date_range(
        start_date,
        end_date,
        status=None
    ):

        start_date = str(start_date)
        end_date = str(end_date)

        if start_date > end_date:
            raise ValueError(
                "Start date cannot be after end date."
            )

        query = """
            SELECT
                v.id,
                v.patient_id,
                v.doctor_id,
                v.token_number,
                v.token_sequence,
                v.visit_date,
                v.visit_time,
                v.status,

                p.name AS patient_name,
                p.mobile,
                p.gender,

                d.name AS doctor_name

            FROM visits v

            JOIN patients p
                ON p.id = v.patient_id

            LEFT JOIN doctors d
                ON d.id = v.doctor_id

            WHERE v.visit_date BETWEEN ? AND ?
        """

        params = [start_date, end_date]

        if status:

            if status not in TokenModel.VALID_STATUSES:
                raise ValueError("Invalid token status.")

            query += " AND v.status = ?"
            params.append(status)

        query += """
            ORDER BY
                v.visit_date DESC,
                v.token_sequence ASC
        """

        return fetch_all(query, tuple(params))

    # ========================================================
    # 10. GET PATIENT'S ACTIVE TOKEN
    # ========================================================

    @staticmethod
    def get_active_token(patient_id, visit_date=None):

        if visit_date is None:
            visit_date = TokenModel.today()

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
                str(visit_date)
            )
        )

    # ========================================================
    # 11. GET PATIENT'S VISIT HISTORY
    # ========================================================

    @staticmethod
    def get_patient_tokens(patient_id):

        return fetch_all(
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
            """,
            (patient_id,)
        )

    # ========================================================
    # 12. SEARCH TODAY'S TOKENS
    # ========================================================

    @staticmethod
    def search_today(search_text):

        search_text = str(search_text).strip()

        if not search_text:
            return TokenModel.get_today_tokens()

        pattern = f"%{search_text}%"

        return fetch_all(
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

                p.name AS patient_name,
                p.mobile,
                p.gender,

                d.name AS doctor_name

            FROM visits v

            JOIN patients p
                ON p.id = v.patient_id

            LEFT JOIN doctors d
                ON d.id = v.doctor_id

            WHERE v.visit_date = ?
              AND (
                  v.token_number LIKE ?
                  OR p.name LIKE ?
                  OR p.mobile LIKE ?
                  OR CAST(p.id AS TEXT) LIKE ?
              )

            ORDER BY v.token_sequence ASC
            """,
            (
                TokenModel.today(),
                pattern,
                pattern,
                pattern,
                pattern
            )
        )

    # ========================================================
    # 13. START CONSULTATION
    # ========================================================

    @staticmethod
    def start_consultation(visit_id, doctor_id):

        connection = get_connection()

        try:

            connection.execute("BEGIN IMMEDIATE")

            doctor = connection.execute(
                """
                SELECT id
                FROM doctors
                WHERE id = ?
                  AND status = 'Active'
                """,
                (doctor_id,)
            ).fetchone()

            if not doctor:
                raise ValueError(
                    "Doctor account is not active."
                )

            cursor = connection.execute(
                """
                UPDATE visits
                SET
                    status = 'In Progress',
                    doctor_id = ?

                WHERE id = ?
                  AND visit_date = ?
                  AND status = 'Waiting'
                  AND (
                      doctor_id IS NULL
                      OR doctor_id = ?
                  )
                """,
                (
                    doctor_id,
                    visit_id,
                    TokenModel.today(),
                    doctor_id
                )
            )

            updated = cursor.rowcount

            connection.commit()

            return updated > 0

        except Exception:

            connection.rollback()
            raise

        finally:

            connection.close()

    # ========================================================
    # 14. COMPLETE CONSULTATION
    # ========================================================

    @staticmethod
    def complete_consultation(visit_id, doctor_id=None):

        query = """
            UPDATE visits
            SET
                status = 'Completed',
                completed_at = ?

            WHERE id = ?
              AND status = 'In Progress'
        """

        params = [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            visit_id
        ]

        if doctor_id is not None:

            query += " AND doctor_id = ?"
            params.append(doctor_id)

        updated = execute_query(
            query,
            tuple(params)
        )

        return updated > 0

    # ========================================================
    # 15. CANCEL TOKEN
    # ========================================================

    @staticmethod
    def cancel_token(visit_id):

        updated = execute_query(
            """
            UPDATE visits
            SET
                status = 'Cancelled'

            WHERE id = ?
              AND visit_date = ?
              AND status IN ('Waiting', 'In Progress')
              AND NOT EXISTS (
                  SELECT 1
                  FROM bills
                  WHERE bills.visit_id = visits.id
              )
            """,
            (
                visit_id,
                TokenModel.today()
            )
        )

        return updated > 0

    # ========================================================
    # 16. UPDATE TOKEN STATUS
    # ========================================================

    @staticmethod
    def update_status(visit_id, status, doctor_id=None):

        if status not in TokenModel.VALID_STATUSES:
            raise ValueError("Invalid token status.")

        if status == "Waiting":

            raise ValueError(
                "A token cannot be returned to Waiting."
            )

        if status == "In Progress":

            if doctor_id is None:
                raise ValueError("Doctor ID is required.")

            return TokenModel.start_consultation(
                visit_id,
                doctor_id
            )

        if status == "Completed":

            return TokenModel.complete_consultation(
                visit_id,
                doctor_id
            )

        return TokenModel.cancel_token(visit_id)

    # ========================================================
    # 17. COUNT ALL TOKENS
    # ========================================================

    @staticmethod
    def count_all():

        result = fetch_one(
            """
            SELECT COUNT(*) AS total
            FROM visits
            """
        )

        return int(result["total"]) if result else 0

    # ========================================================
    # 18. COUNT TODAY'S TOKENS
    # ========================================================

    @staticmethod
    def count_today(status=None):

        query = """
            SELECT COUNT(*) AS total
            FROM visits
            WHERE visit_date = ?
        """

        params = [TokenModel.today()]

        if status:

            if status not in TokenModel.VALID_STATUSES:
                raise ValueError("Invalid token status.")

            query += " AND status = ?"
            params.append(status)

        result = fetch_one(
            query,
            tuple(params)
        )

        return int(result["total"]) if result else 0

    # ========================================================
    # 19. TODAY'S TOKEN STATISTICS
    # ========================================================

    @staticmethod
    def get_today_statistics():

        result = fetch_one(
            """
            SELECT
                COUNT(*) AS total,

                COALESCE(
                    SUM(
                        CASE
                            WHEN status = 'Waiting'
                            THEN 1
                            ELSE 0
                        END
                    ),
                    0
                ) AS waiting,

                COALESCE(
                    SUM(
                        CASE
                            WHEN status = 'In Progress'
                            THEN 1
                            ELSE 0
                        END
                    ),
                    0
                ) AS in_progress,

                COALESCE(
                    SUM(
                        CASE
                            WHEN status = 'Completed'
                            THEN 1
                            ELSE 0
                        END
                    ),
                    0
                ) AS completed,

                COALESCE(
                    SUM(
                        CASE
                            WHEN status = 'Cancelled'
                            THEN 1
                            ELSE 0
                        END
                    ),
                    0
                ) AS cancelled

            FROM visits

            WHERE visit_date = ?
            """,
            (TokenModel.today(),)
        )

        return result or {
            "total": 0,
            "waiting": 0,
            "in_progress": 0,
            "completed": 0,
            "cancelled": 0
        }

    # ========================================================
    # 20. GET NEXT TOKEN SEQUENCE
    # ========================================================

    @staticmethod
    def get_next_sequence(visit_date=None):

        if visit_date is None:
            visit_date = TokenModel.today()

        result = fetch_one(
            """
            SELECT last_sequence
            FROM daily_token_counters
            WHERE counter_date = ?
            """,
            (str(visit_date),)
        )

        if not result:

            return max(
                1,
                int(TOKEN_START_NUMBER)
            )

        return int(result["last_sequence"]) + 1

    # ========================================================
    # 21. PREVIEW NEXT TOKEN NUMBER
    # ========================================================

    @staticmethod
    def preview_next_token(visit_date=None):
        """
        Return the likely next token number.

        This is a preview only. The actual number is assigned
        inside create_token() using a database transaction.
        """

        sequence = TokenModel.get_next_sequence(
            visit_date
        )

        return TokenModel.format_token(sequence)

    # ========================================================
    # 22. GET LAST ISSUED TOKEN
    # ========================================================

    @staticmethod
    def get_last_token(visit_date=None):

        if visit_date is None:
            visit_date = TokenModel.today()

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
                status

            FROM visits

            WHERE visit_date = ?

            ORDER BY token_sequence DESC

            LIMIT 1
            """,
            (str(visit_date),)
        )

    # ========================================================
    # 23. GET CURRENT TOKEN
    # ========================================================

    @staticmethod
    def get_current_token(visit_date=None):

        if visit_date is None:
            visit_date = TokenModel.today()

        return fetch_one(
            """
            SELECT
                v.id,
                v.token_number,
                v.token_sequence,
                v.visit_date,
                v.visit_time,
                v.status,

                p.name AS patient_name,
                p.mobile,

                d.name AS doctor_name

            FROM visits v

            JOIN patients p
                ON p.id = v.patient_id

            LEFT JOIN doctors d
                ON d.id = v.doctor_id

            WHERE v.visit_date = ?
              AND v.status = 'In Progress'

            ORDER BY v.token_sequence ASC

            LIMIT 1
            """,
            (str(visit_date),)
        )

    # ========================================================
    # 24. GET NEXT WAITING TOKEN
    # ========================================================

    @staticmethod
    def get_next_waiting_token(visit_date=None):

        if visit_date is None:
            visit_date = TokenModel.today()

        return fetch_one(
            """
            SELECT
                v.id,
                v.patient_id,
                v.token_number,
                v.token_sequence,
                v.visit_date,
                v.visit_time,
                v.status,

                p.name AS patient_name,
                p.mobile,
                p.gender

            FROM visits v

            JOIN patients p
                ON p.id = v.patient_id

            WHERE v.visit_date = ?
              AND v.status = 'Waiting'

            ORDER BY v.token_sequence ASC

            LIMIT 1
            """,
            (str(visit_date),)
        )

    # ========================================================
    # 25. GET DAILY TOKEN COUNTS
    # ========================================================

    @staticmethod
    def get_daily_statistics(
        start_date=None,
        end_date=None
    ):

        query = """
            SELECT
                visit_date,
                COUNT(*) AS total,

                COALESCE(
                    SUM(
                        CASE
                            WHEN status = 'Waiting'
                            THEN 1 ELSE 0
                        END
                    ),
                    0
                ) AS waiting,

                COALESCE(
                    SUM(
                        CASE
                            WHEN status = 'In Progress'
                            THEN 1 ELSE 0
                        END
                    ),
                    0
                ) AS in_progress,

                COALESCE(
                    SUM(
                        CASE
                            WHEN status = 'Completed'
                            THEN 1 ELSE 0
                        END
                    ),
                    0
                ) AS completed,

                COALESCE(
                    SUM(
                        CASE
                            WHEN status = 'Cancelled'
                            THEN 1 ELSE 0
                        END
                    ),
                    0
                ) AS cancelled

            FROM visits

            WHERE 1 = 1
        """

        params = []

        if start_date:

            query += " AND visit_date >= ?"
            params.append(str(start_date))

        if end_date:

            query += " AND visit_date <= ?"
            params.append(str(end_date))

        query += """
            GROUP BY visit_date
            ORDER BY visit_date ASC
        """

        return fetch_all(
            query,
            tuple(params)
        )

    # ========================================================
    # 26. GET STATUS DISTRIBUTION
    # ========================================================

    @staticmethod
    def get_status_distribution(
        start_date=None,
        end_date=None
    ):

        query = """
            SELECT
                status,
                COUNT(*) AS total

            FROM visits

            WHERE 1 = 1
        """

        params = []

        if start_date:

            query += " AND visit_date >= ?"
            params.append(str(start_date))

        if end_date:

            query += " AND visit_date <= ?"
            params.append(str(end_date))

        query += """
            GROUP BY status
            ORDER BY status
        """

        return fetch_all(
            query,
            tuple(params)
        )

    # ========================================================
    # 27. GET TOKEN DETAILS FOR PRINTING
    # ========================================================

    @staticmethod
    def get_print_details(visit_id):

        return fetch_one(
            """
            SELECT
                v.id AS visit_id,
                v.token_number,
                v.token_sequence,
                v.visit_date,
                v.visit_time,
                v.status,

                p.id AS patient_id,
                p.name AS patient_name,
                p.mobile,
                p.gender,

                d.name AS doctor_name

            FROM visits v

            JOIN patients p
                ON p.id = v.patient_id

            LEFT JOIN doctors d
                ON d.id = v.doctor_id

            WHERE v.id = ?

            LIMIT 1
            """,
            (visit_id,)
        )


# ============================================================
# END OF FILE
# ============================================================
