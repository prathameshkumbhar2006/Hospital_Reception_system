-- ============================================================
-- HOSPITAL RECEPTION SYSTEM
-- DATABASE: SQLite3
-- FILE: database.sql
-- ============================================================


-- ============================================================
-- 1. PATIENTS TABLE
-- ============================================================

CREATE TABLE IF NOT EXISTS patients (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    name TEXT NOT NULL,

    mobile TEXT NOT NULL UNIQUE,

    gender TEXT NOT NULL
        CHECK (gender IN ('Male', 'Female', 'Other')),

    created_at TEXT DEFAULT CURRENT_TIMESTAMP

);


-- ============================================================
-- 2. DOCTORS TABLE
-- ============================================================

CREATE TABLE IF NOT EXISTS doctors (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    name TEXT NOT NULL,

    email TEXT NOT NULL UNIQUE,

    password_hash TEXT NOT NULL,

    status TEXT NOT NULL DEFAULT 'Active'
        CHECK (status IN ('Active', 'Inactive')),

    created_at TEXT DEFAULT CURRENT_TIMESTAMP

);


-- ============================================================
-- 3. DAILY TOKEN COUNTERS TABLE
-- ============================================================

CREATE TABLE IF NOT EXISTS daily_token_counters (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    counter_date TEXT NOT NULL UNIQUE,

    last_sequence INTEGER NOT NULL DEFAULT 0
        CHECK (last_sequence >= 0)

);


-- ============================================================
-- 4. PATIENT VISITS TABLE
-- ============================================================

CREATE TABLE IF NOT EXISTS visits (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    patient_id INTEGER NOT NULL,

    doctor_id INTEGER,

    token_number TEXT NOT NULL,

    token_sequence INTEGER NOT NULL,

    visit_date TEXT NOT NULL,

    visit_time TEXT NOT NULL,

    status TEXT NOT NULL DEFAULT 'Waiting'
        CHECK (
            status IN (
                'Waiting',
                'In Progress',
                'Completed',
                'Cancelled'
            )
        ),

    completed_at TEXT,

    created_at TEXT DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (patient_id)
        REFERENCES patients(id)
        ON DELETE RESTRICT,

    FOREIGN KEY (doctor_id)
        REFERENCES doctors(id)
        ON DELETE SET NULL,

    UNIQUE (visit_date, token_sequence),

    CHECK (token_sequence > 0)

);


-- ============================================================
-- 5. BILLS TABLE
-- ============================================================

CREATE TABLE IF NOT EXISTS bills (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    bill_number TEXT NOT NULL UNIQUE,

    visit_id INTEGER NOT NULL UNIQUE,

    consultation_fee REAL NOT NULL DEFAULT 0,

    medicine_fee REAL NOT NULL DEFAULT 0,

    other_charges REAL NOT NULL DEFAULT 0,

    total_amount REAL NOT NULL DEFAULT 0,

    payment_method TEXT
        CHECK (
            payment_method IN (
                'Cash',
                'UPI',
                'Card'
            )
        ),

    payment_status TEXT NOT NULL DEFAULT 'Unpaid'
        CHECK (
            payment_status IN (
                'Paid',
                'Unpaid',
                'Partial'
            )
        ),

    created_at TEXT DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (visit_id)
        REFERENCES visits(id)
        ON DELETE RESTRICT,

    CHECK (consultation_fee >= 0),
    CHECK (medicine_fee >= 0),
    CHECK (other_charges >= 0),
    CHECK (total_amount >= 0)

);


-- ============================================================
-- 6. PAYMENTS TABLE
-- ============================================================

CREATE TABLE IF NOT EXISTS payments (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    bill_id INTEGER NOT NULL,

    amount REAL NOT NULL,

    payment_method TEXT NOT NULL
        CHECK (
            payment_method IN (
                'Cash',
                'UPI',
                'Card'
            )
        ),

    payment_reference TEXT,

    paid_at TEXT DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (bill_id)
        REFERENCES bills(id)
        ON DELETE RESTRICT,

    CHECK (amount > 0)

);


-- ============================================================
-- 7. INDEXES
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_patient_name
ON patients(name);

CREATE INDEX IF NOT EXISTS idx_visit_patient
ON visits(patient_id);

CREATE INDEX IF NOT EXISTS idx_visit_date
ON visits(visit_date);

CREATE INDEX IF NOT EXISTS idx_visit_status
ON visits(status);

CREATE INDEX IF NOT EXISTS idx_visit_token
ON visits(token_number);

CREATE INDEX IF NOT EXISTS idx_bill_date
ON bills(created_at);

CREATE INDEX IF NOT EXISTS idx_payment_status
ON bills(payment_status);

CREATE INDEX IF NOT EXISTS idx_payment_bill
ON payments(bill_id);

CREATE INDEX IF NOT EXISTS idx_payment_date
ON payments(paid_at);


-- ============================================================
-- DATABASE SETUP COMPLETED
-- ============================================================
