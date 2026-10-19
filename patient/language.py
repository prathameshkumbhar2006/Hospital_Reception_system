# ============================================================
# HOSPITAL RECEPTION SYSTEM
# FILE: patient/language.py
# PURPOSE: English and Marathi Language Support
# ============================================================


# ============================================================
# 1. LANGUAGE TRANSLATIONS
# ============================================================

TRANSLATIONS = {

    # --------------------------------------------------------
    # ENGLISH
    # --------------------------------------------------------

    "English": {

        # General
        "hospital": "Hospital Reception System",
        "welcome": "Welcome to Our Hospital",
        "welcome_message": "Welcome to our hospital",
        "select_language": "Select Your Language",
        "continue": "Continue",
        "back": "Back",
        "home": "Home",
        "cancel": "Cancel",
        "clear": "Clear",
        "delete": "Delete",
        "submit": "Submit",
        "yes": "Yes",
        "no": "No",
        "ok": "OK",
        "close": "Close",
        "loading": "Please Wait...",
        "success": "Success",
        "error": "Error",
        "warning": "Warning",

        # Mobile Number Screen
        "enter_mobile": "Enter Mobile Number",
        "mobile_number": "Mobile Number",
        "mobile_placeholder": "Enter 10-digit mobile number",
        "search_patient": "Search Patient",
        "checking_mobile": "Checking Mobile Number...",
        "invalid_mobile": "Please enter a valid 10-digit mobile number.",
        "mobile_required": "Please enter your mobile number.",
        "mobile_digits_only": "Mobile number must contain only digits.",
        "mobile_not_found": "Mobile number not registered.",
        "mobile_found": "Patient record found.",

        # Existing Patient
        "existing_patient": "Existing Patient",
        "welcome_back": "Welcome Back",
        "patient_found": "Patient Found",
        "patient_exists": "Your mobile number is already registered.",
        "generate_token": "Generate Token",
        "continue_token": "Continue to Token",
        "confirm_details": "Please confirm your details.",

        # New Patient
        "new_patient": "New Patient Registration",
        "new_patient_message": "Please enter your details.",
        "register_patient": "Register Patient",
        "registration": "Registration",
        "enter_name": "Enter Patient Name",
        "full_name": "Full Name",
        "name_placeholder": "Enter your full name",
        "name_required": "Please enter your name.",
        "invalid_name": "Please enter a valid name.",
        "registration_success": "Patient registered successfully.",
        "registration_failed": "Patient registration failed.",

        # Gender
        "select_gender": "Select Gender",
        "gender": "Gender",
        "male": "Male",
        "female": "Female",
        "other": "Other",
        "gender_required": "Please select your gender.",

        # Patient Details
        "patient_details": "Patient Details",
        "patient_id": "Patient ID",
        "patient_name": "Patient Name",
        "registered_mobile": "Registered Mobile Number",
        "registration_date": "Registration Date",

        # Token
        "token": "Token",
        "token_number": "Token Number",
        "token_generated": "Token Generated Successfully",
        "your_token": "Your Token Number",
        "token_success": "Your token has been generated successfully.",
        "token_failed": "Unable to generate token.",
        "token_exists": "You already have an active token today.",
        "token_not_found": "Token not found.",
        "token_date": "Token Date",
        "token_time": "Token Time",
        "please_wait": "Please wait for your turn.",
        "print_token": "Print Token",
        "finish": "Finish",
        "thank_you": "Thank You",
        "visit_again": "Thank you for visiting our hospital.",
        "get_well_soon": "Get Well Soon",

        # Token Status
        "waiting": "Waiting",
        "in_progress": "In Progress",
        "completed": "Completed",
        "cancelled": "Cancelled",
        "status": "Status",

        # Date and Time
        "date": "Date",
        "time": "Time",
        "today": "Today",

        # Instructions
        "touch_to_continue": "Touch the button to continue.",
        "enter_details": "Please enter your details.",
        "check_information": "Please check your information.",
        "wait_for_doctor": "Please wait until your token is called.",
        "contact_reception": "Please contact reception for assistance.",

        # System Messages
        "database_error": "Database connection error.",
        "something_wrong": "Something went wrong. Please try again.",
        "try_again": "Please Try Again",
        "network_error": "Unable to connect to the system.",
        "processing": "Processing...",
        "operation_success": "Operation completed successfully.",
        "operation_failed": "Operation failed.",

        # Navigation
        "go_back": "Go Back",
        "go_home": "Go to Home",
        "start_again": "Start Again",
        "next": "Next",

        # Keypad
        "keypad": "Keypad",
        "backspace": "Backspace",
        "space": "Space",
        "keyboard": "Keyboard",

        # Footer
        "footer": "Patient Self-Registration & Token System"
    },

    # --------------------------------------------------------
    # MARATHI
    # --------------------------------------------------------

    "मराठी": {

        # General
        "hospital": "रुग्णालय स्वागत प्रणाली",
        "welcome": "आमच्या रुग्णालयात आपले स्वागत आहे",
        "welcome_message": "रुग्णालयात आपले स्वागत आहे",
        "select_language": "आपली भाषा निवडा",
        "continue": "पुढे जा",
        "back": "मागे जा",
        "home": "मुख्य पृष्ठ",
        "cancel": "रद्द करा",
        "clear": "पुसून टाका",
        "delete": "हटवा",
        "submit": "जमा करा",
        "yes": "होय",
        "no": "नाही",
        "ok": "ठीक आहे",
        "close": "बंद करा",
        "loading": "कृपया प्रतीक्षा करा...",
        "success": "यशस्वी",
        "error": "त्रुटी",
        "warning": "सूचना",

        # Mobile Number Screen
        "enter_mobile": "मोबाईल नंबर टाका",
        "mobile_number": "मोबाईल नंबर",
        "mobile_placeholder": "१० अंकी मोबाईल नंबर टाका",
        "search_patient": "रुग्ण शोधा",
        "checking_mobile": "मोबाईल नंबर तपासत आहे...",
        "invalid_mobile": "कृपया योग्य १० अंकी मोबाईल नंबर टाका.",
        "mobile_required": "कृपया मोबाईल नंबर टाका.",
        "mobile_digits_only": "मोबाईल नंबरमध्ये फक्त अंक असावेत.",
        "mobile_not_found": "हा मोबाईल नंबर नोंदणीकृत नाही.",
        "mobile_found": "रुग्णाची नोंद सापडली.",

        # Existing Patient
        "existing_patient": "नोंदणीकृत रुग्ण",
        "welcome_back": "पुन्हा स्वागत आहे",
        "patient_found": "रुग्ण सापडला",
        "patient_exists": "आपला मोबाईल नंबर आधीच नोंदणीकृत आहे.",
        "generate_token": "टोकन तयार करा",
        "continue_token": "टोकनसाठी पुढे जा",
        "confirm_details": "कृपया आपली माहिती तपासा.",

        # New Patient
        "new_patient": "नवीन रुग्ण नोंदणी",
        "new_patient_message": "कृपया आपली माहिती भरा.",
        "register_patient": "रुग्ण नोंदणी करा",
        "registration": "नोंदणी",
        "enter_name": "रुग्णाचे नाव टाका",
        "full_name": "पूर्ण नाव",
        "name_placeholder": "आपले पूर्ण नाव टाका",
        "name_required": "कृपया आपले नाव टाका.",
        "invalid_name": "कृपया योग्य नाव टाका.",
        "registration_success": "रुग्णाची नोंदणी यशस्वी झाली.",
        "registration_failed": "रुग्णाची नोंदणी होऊ शकली नाही.",

        # Gender
        "select_gender": "लिंग निवडा",
        "gender": "लिंग",
        "male": "पुरुष",
        "female": "स्त्री",
        "other": "इतर",
        "gender_required": "कृपया लिंग निवडा.",

        # Patient Details
        "patient_details": "रुग्णाची माहिती",
        "patient_id": "रुग्ण क्रमांक",
        "patient_name": "रुग्णाचे नाव",
        "registered_mobile": "नोंदणीकृत मोबाईल नंबर",
        "registration_date": "नोंदणी दिनांक",

        # Token
        "token": "टोकन",
        "token_number": "टोकन क्रमांक",
        "token_generated": "टोकन यशस्वीपणे तयार झाले",
        "your_token": "आपला टोकन क्रमांक",
        "token_success": "आपले टोकन यशस्वीपणे तयार झाले आहे.",
        "token_failed": "टोकन तयार करता आले नाही.",
        "token_exists": "आपल्याकडे आजचे सक्रिय टोकन आधीच आहे.",
        "token_not_found": "टोकन सापडले नाही.",
        "token_date": "टोकन दिनांक",
        "token_time": "टोकन वेळ",
        "please_wait": "कृपया आपल्या क्रमांकाची प्रतीक्षा करा.",
        "print_token": "टोकन प्रिंट करा",
        "finish": "पूर्ण करा",
        "thank_you": "धन्यवाद",
        "visit_again": "आमच्या रुग्णालयाला भेट दिल्याबद्दल धन्यवाद.",
        "get_well_soon": "लवकर बरे व्हा",

        # Token Status
        "waiting": "प्रतीक्षेत",
        "in_progress": "तपासणी सुरू",
        "completed": "पूर्ण झाले",
        "cancelled": "रद्द झाले",
        "status": "स्थिती",

        # Date and Time
        "date": "दिनांक",
        "time": "वेळ",
        "today": "आज",

        # Instructions
        "touch_to_continue": "पुढे जाण्यासाठी बटण दाबा.",
        "enter_details": "कृपया आपली माहिती भरा.",
        "check_information": "कृपया आपली माहिती तपासा.",
        "wait_for_doctor": "आपला टोकन क्रमांक पुकारेपर्यंत प्रतीक्षा करा.",
        "contact_reception": "मदतीसाठी कृपया स्वागत कक्षाशी संपर्क साधा.",

        # System Messages
        "database_error": "डेटाबेस जोडणीमध्ये त्रुटी आली.",
        "something_wrong": "काहीतरी चूक झाली. कृपया पुन्हा प्रयत्न करा.",
        "try_again": "पुन्हा प्रयत्न करा",
        "network_error": "प्रणालीशी संपर्क साधता आला नाही.",
        "processing": "प्रक्रिया सुरू आहे...",
        "operation_success": "प्रक्रिया यशस्वी झाली.",
        "operation_failed": "प्रक्रिया अयशस्वी झाली.",

        # Navigation
        "go_back": "मागे जा",
        "go_home": "मुख्य पृष्ठावर जा",
        "start_again": "पुन्हा सुरू करा",
        "next": "पुढे",

        # Keypad
        "keypad": "अंकपटल",
        "backspace": "मागील अंक पुसा",
        "space": "जागा",
        "keyboard": "कीबोर्ड",

        # Footer
        "footer": "रुग्ण स्व-नोंदणी आणि टोकन प्रणाली"
    }
}


# ============================================================
# 2. GET TRANSLATED TEXT
# ============================================================

def get_text(key, language="English"):
    """
    Return text in the selected language.

    If the translation does not exist, use English.

    Example:
        get_text("enter_mobile", "मराठी")
    """

    # Get selected language dictionary
    language_data = TRANSLATIONS.get(
        language,
        TRANSLATIONS["English"]
    )

    # Return translated text if available
    if key in language_data:
        return language_data[key]

    # Fall back to English
    return TRANSLATIONS["English"].get(
        key,
        key
    )


# ============================================================
# 3. GET AVAILABLE LANGUAGES
# ============================================================

def get_languages():
    """
    Return available languages.
    """

    return list(TRANSLATIONS.keys())


# ============================================================
# 4. CHECK LANGUAGE
# ============================================================

def is_valid_language(language):
    """
    Check whether a language is supported.
    """

    return language in TRANSLATIONS


# ============================================================
# 5. TEST TRANSLATIONS
# ============================================================

if __name__ == "__main__":

    print("=" * 55)
    print("HOSPITAL RECEPTION SYSTEM")
    print("Language Translation Test")
    print("=" * 55)

    test_keys = [
        "welcome",
        "select_language",
        "enter_mobile",
        "new_patient",
        "select_gender",
        "generate_token",
        "thank_you"
    ]

    print("\nENGLISH:")
    print("-" * 55)

    for key in test_keys:
        print(f"{key}: {get_text(key, 'English')}")

    print("\nMARATHI:")
    print("-" * 55)

    for key in test_keys:
        print(f"{key}: {get_text(key, 'मराठी')}")

    print("\nTranslation test completed.")
