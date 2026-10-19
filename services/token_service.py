# ============================================================
# HOSPITAL RECEPTION SYSTEM
# FILE: services/token_service.py
# PURPOSE: Patient Token Generation and Management
# DATABASE: SQLite3
# ============================================================

from datetime import date, datetime

from models.patient_model import PatientModel
from models.doctor_model import DoctorModel
from models.token_model import TokenModel


class TokenService:

    VALID_STATUSES = (
        "Waiting",
        "In Progress",
        "Completed",
        "Cancelled"
    )

    # ========================================================
    # 1. GENERATE TOKEN FOR EXISTING PATIENT
    # ========================================================

    @staticmethod
    def generate_token(patient_id, doctor_id=None):

        patient = PatientModel.get_by_id(patient_id)

        if not patient:
            raise ValueError("Patient not found.")

        if doctor_id is not None:

            if not DoctorModel.is_active(doctor_id):
                raise ValueError(
                    "Selected doctor is not active."
                )

        existing_token = TokenModel.get_active_token(
            patient_id
        )

        if existing_token:

            return {
                "success": True,
                "message": "Patient already has an active token.",
                "is_existing": True,
                "token": TokenModel.get_by_id(
                    existing_token["id"]
                )
            }

        token = TokenModel.create_token(
            patient_id=patient_id,
            doctor_id=doctor_id
        )

        return {
            "success": True,
            "message": "Token generated successfully.",
            "is_existing": False,
            "token": TokenModel.get_by_id(
                token["id"]
            )
        }

    # ========================================================
    # 2. REGISTER PATIENT AND GENERATE TOKEN
    # ========================================================

    @staticmethod
    def register_and_generate_token(
        name,
        mobile,
        gender,
        doctor_id=None
    ):

        name = str(name).strip()
        mobile = str(mobile).strip()
        gender = str(gender).strip()

        if not PatientModel.validate_name(name):
            raise ValueError(
                "Patient name is required."
            )

        if not PatientModel.validate_mobile(mobile):
            raise ValueError(
                "Mobile number must contain exactly 10 digits."
            )

        if not PatientModel.validate_gender(gender):
            raise ValueError(
                "Please select a valid gender."
            )

        if doctor_id is not None:

            if not DoctorModel.is_active(doctor_id):
                raise ValueError(
                    "Selected doctor is not active."
                )

        patient_id, is_new_patient = (
            PatientModel.get_or_create(
                name=name,
                mobile=mobile,
                gender=gender
            )
        )

        result = TokenService.generate_token(
            patient_id=patient_id,
            doctor_id=doctor_id
        )

        result["patient"] = PatientModel.get_by_id(
            patient_id
        )

        result["is_new_patient"] = is_new_patient

        return result

    # ========================================================
    # 3. GENERATE TOKEN USING MOBILE NUMBER
    # ========================================================

    @staticmethod
    def generate_token_by_mobile(
        mobile,
        doctor_id=None
    ):

        mobile = str(mobile).strip()

        if not PatientModel.validate_mobile(mobile):
            raise ValueError(
                "Invalid mobile number."
            )

        patient = PatientModel.get_by_mobile(
            mobile
        )

        if not patient:

            return {
                "success": False,
                "message": "Patient not registered.",
                "patient_exists": False,
                "patient": None,
                "token": None
            }

        result = TokenService.generate_token(
            patient_id=patient["id"],
            doctor_id=doctor_id
        )

        result["patient_exists"] = True
        result["patient"] = patient

        return result

    # ========================================================
    # 4. CHECK EXISTING ACTIVE TOKEN
    # ========================================================

    @staticmethod
    def check_existing_token(patient_id):

        patient = PatientModel.get_by_id(
            patient_id
        )

        if not patient:
            return None

        token = TokenModel.get_active_token(
            patient_id
        )

        if not token:
            return None

        return TokenModel.get_by_id(
            token["id"]
        )

    # ========================================================
    # 5. GET TOKEN DETAILS
    # ========================================================

    @staticmethod
    def get_token_details(visit_id):

        return TokenModel.get_by_id(
            visit_id
        )

    # ========================================================
    # 6. SEARCH TOKEN
    # ========================================================

    @staticmethod
    def search_token(
        token_number,
        visit_date=None
    ):

        token_number = str(
            token_number
        ).strip().upper()

        if not token_number:
            raise ValueError(
                "Token number is required."
            )

        if visit_date is None:
            visit_date = date.today().isoformat()

        return TokenModel.get_by_number(
            token_number,
            visit_date
        )

    # ========================================================
    # 7. GET TODAY'S TOKENS
    # ========================================================

    @staticmethod
    def get_today_tokens(status=None):

        if status is not None:

            if status not in TokenService.VALID_STATUSES:
                raise ValueError(
                    "Invalid token status."
                )

        return TokenModel.get_today_tokens(
            status=status
        )

    # ========================================================
    # 8. SEARCH TODAY'S PATIENT TOKENS
    # ========================================================

    @staticmethod
    def search_today_tokens(search_text):

        return TokenModel.search_today(
            search_text
        )

    # ========================================================
    # 9. GET TOKENS BY DATE
    # ========================================================

    @staticmethod
    def get_tokens_by_date(
        visit_date,
        status=None
    ):

        visit_date = TokenService.validate_date(
            visit_date
        )

        if status is not None:

            if status not in TokenService.VALID_STATUSES:
                raise ValueError(
                    "Invalid token status."
                )

        return TokenModel.get_tokens_by_date(
            visit_date,
            status
        )

    # ========================================================
    # 10. GET TOKENS BY DATE RANGE
    # ========================================================

    @staticmethod
    def get_tokens_by_date_range(
        start_date,
        end_date,
        status=None
    ):

        start_date = TokenService.validate_date(
            start_date
        )

        end_date = TokenService.validate_date(
            end_date
        )

        if start_date > end_date:
            raise ValueError(
                "Start date cannot be after end date."
            )

        if status is not None:

            if status not in TokenService.VALID_STATUSES:
                raise ValueError(
                    "Invalid token status."
                )

        return TokenModel.get_tokens_by_date_range(
            start_date,
            end_date,
            status
        )

    # ========================================================
    # 11. START CONSULTATION
    # ========================================================

    @staticmethod
    def start_consultation(
        visit_id,
        doctor_id
    ):

        token = TokenModel.get_by_id(
            visit_id
        )

        if not token:
            raise ValueError(
                "Token not found."
            )

        if not DoctorModel.is_active(doctor_id):
            raise ValueError(
                "Doctor account is not active."
            )

        if token["visit_date"] != date.today().isoformat():
            raise ValueError(
                "Only today's tokens can start consultation."
            )

        if token["status"] != "Waiting":
            raise ValueError(
                "Only waiting tokens can start consultation."
            )

        if token["doctor_id"] is not None:

            if int(token["doctor_id"]) != int(doctor_id):
                raise ValueError(
                    "This token is assigned to another doctor."
                )

        updated = TokenModel.start_consultation(
            visit_id,
            doctor_id
        )

        if not updated:
            raise ValueError(
                "Unable to start consultation. "
                "Token status may have changed."
            )

        return {
            "success": True,
            "message": "Consultation started successfully.",
            "token": TokenModel.get_by_id(
                visit_id
            )
        }

    # ========================================================
    # 12. COMPLETE CONSULTATION
    # ========================================================

    @staticmethod
    def complete_consultation(
        visit_id,
        doctor_id=None
    ):

        token = TokenModel.get_by_id(
            visit_id
        )

        if not token:
            raise ValueError(
                "Token not found."
            )

        if token["status"] != "In Progress":
            raise ValueError(
                "Only consultations in progress can be completed."
            )

        if doctor_id is not None:

            if token["doctor_id"] != int(doctor_id):
                raise ValueError(
                    "This consultation belongs to another doctor."
                )

        updated = TokenModel.complete_consultation(
            visit_id,
            doctor_id
        )

        if not updated:
            raise ValueError(
                "Unable to complete consultation."
            )

        return {
            "success": True,
            "message": "Consultation completed successfully.",
            "token": TokenModel.get_by_id(
                visit_id
            )
        }

    # ========================================================
    # 13. CANCEL TOKEN
    # ========================================================

    @staticmethod
    def cancel_token(visit_id):

        token = TokenModel.get_by_id(
            visit_id
        )

        if not token:
            raise ValueError(
                "Token not found."
            )

        if token["status"] not in (
            "Waiting",
            "In Progress"
        ):
            raise ValueError(
                "Only active tokens can be cancelled."
            )

        updated = TokenModel.cancel_token(
            visit_id
        )

        if not updated:
            raise ValueError(
                "Unable to cancel token. "
                "A bill may already exist."
            )

        return {
            "success": True,
            "message": "Token cancelled successfully.",
            "token": TokenModel.get_by_id(
                visit_id
            )
        }

    # ========================================================
    # 14. GET NEXT WAITING TOKEN
    # ========================================================

    @staticmethod
    def get_next_waiting_token():

        return TokenModel.get_next_waiting_token()

    # ========================================================
    # 15. GET CURRENT CONSULTATION
    # ========================================================

    @staticmethod
    def get_current_token():

        return TokenModel.get_current_token()

    # ========================================================
    # 16. GET NEXT TOKEN PREVIEW
    # ========================================================

    @staticmethod
    def get_next_token_number():

        return TokenModel.preview_next_token()

    # ========================================================
    # 17. GET LAST GENERATED TOKEN
    # ========================================================

    @staticmethod
    def get_last_generated_token():

        return TokenModel.get_last_token()

    # ========================================================
    # 18. GET TODAY'S TOKEN STATISTICS
    # ========================================================

    @staticmethod
    def get_today_statistics():

        return TokenModel.get_today_statistics()

    # ========================================================
    # 19. COUNT TODAY'S TOKENS
    # ========================================================

    @staticmethod
    def count_today(status=None):

        return TokenModel.count_today(
            status=status
        )

    # ========================================================
    # 20. GET PATIENT TOKEN HISTORY
    # ========================================================

    @staticmethod
    def get_patient_token_history(patient_id):

        patient = PatientModel.get_by_id(
            patient_id
        )

        if not patient:
            raise ValueError(
                "Patient not found."
            )

        return TokenModel.get_patient_tokens(
            patient_id
        )

    # ========================================================
    # 21. GET DAILY TOKEN STATISTICS
    # ========================================================

    @staticmethod
    def get_daily_statistics(
        start_date=None,
        end_date=None
    ):

        if start_date is not None:

            start_date = TokenService.validate_date(
                start_date
            )

        if end_date is not None:

            end_date = TokenService.validate_date(
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

        return TokenModel.get_daily_statistics(
            start_date,
            end_date
        )

    # ========================================================
    # 22. GET TOKEN STATUS DISTRIBUTION
    # ========================================================

    @staticmethod
    def get_status_distribution(
        start_date=None,
        end_date=None
    ):

        if start_date is not None:

            start_date = TokenService.validate_date(
                start_date
            )

        if end_date is not None:

            end_date = TokenService.validate_date(
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

        return TokenModel.get_status_distribution(
            start_date,
            end_date
        )

    # ========================================================
    # 23. GET TOKEN PRINT DETAILS
    # ========================================================

    @staticmethod
    def get_print_details(visit_id):

        details = TokenModel.get_print_details(
            visit_id
        )

        if not details:
            raise ValueError(
                "Token not found."
            )

        return details

    # ========================================================
    # 24. FORMAT TOKEN INFORMATION
    # ========================================================

    @staticmethod
    def format_token_information(visit_id):

        token = TokenService.get_print_details(
            visit_id
        )

        return {
            "visit_id": token["visit_id"],
            "token_number": token["token_number"],
            "patient_id": token["patient_id"],
            "patient_name": token["patient_name"],
            "mobile": token["mobile"],
            "gender": token["gender"],
            "visit_date": token["visit_date"],
            "visit_time": token["visit_time"],
            "status": token["status"],
            "doctor_name": token["doctor_name"] or "Not Assigned"
        }

    # ========================================================
    # 25. VALIDATE DATE
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
    # 26. GET TOKEN STATUS MESSAGE
    # ========================================================

    @staticmethod
    def get_status_message(status):

        messages = {
            "Waiting": "Please wait for your consultation.",
            "In Progress": "Consultation is in progress.",
            "Completed": "Consultation completed.",
            "Cancelled": "Token has been cancelled."
        }

        return messages.get(
            status,
            "Unknown token status."
        )

    # ========================================================
    # 27. GET TOKEN SUMMARY
    # ========================================================

    @staticmethod
    def get_token_summary():

        statistics = TokenModel.get_today_statistics()

        next_token = TokenModel.preview_next_token()

        current_token = TokenModel.get_current_token()

        waiting_token = TokenModel.get_next_waiting_token()

        return {
            "date": date.today().isoformat(),
            "total": statistics["total"],
            "waiting": statistics["waiting"],
            "in_progress": statistics["in_progress"],
            "completed": statistics["completed"],
            "cancelled": statistics["cancelled"],
            "next_token_number": next_token,
            "current_token": (
                current_token["token_number"]
                if current_token else None
            ),
            "next_waiting_token": (
                waiting_token["token_number"]
                if waiting_token else None
            )
        }


# ============================================================
# END OF FILE
# ============================================================
