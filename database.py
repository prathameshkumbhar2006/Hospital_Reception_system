# ============================================================
# HOSPITAL RECEPTION SYSTEM
# FILE: database.py
# PURPOSE: SQLite Database Connection and Operations
# ============================================================

import sqlite3

from config import DATABASE_PATH, SQL_FILE


# ============================================================
# 1. GET DATABASE CONNECTION
# ============================================================

def get_connection():
    """
    Creates and returns a SQLite database connection.
    """

    connection = sqlite3.connect(
        DATABASE_PATH,
        timeout=30
    )

    # Return database records as dictionary-like rows
    connection.row_factory = sqlite3.Row

    # Enable foreign key relationships
    connection.execute("PRAGMA foreign_keys = ON")

    # Wait for database locks instead of failing immediately
    connection.execute("PRAGMA busy_timeout = 30000")

    return connection


# ============================================================
# 2. INITIALIZE DATABASE
# ============================================================

def initialize_database():
    """
    Creates database tables using database.sql.

    Existing tables and records are preserved.
    """

    try:
        with open(SQL_FILE, "r", encoding="utf-8") as file:
            sql_script = file.read()

        connection = get_connection()

        try:
            connection.executescript(sql_script)
            connection.commit()

            print("Database initialized successfully.")

            return True

        finally:
            connection.close()

    except (sqlite3.Error, OSError) as error:
        print(f"Database initialization error: {error}")
        return False


# ============================================================
# 3. FETCH ONE RECORD
# ============================================================

def fetch_one(query, params=()):
    """
    Executes a SELECT query and returns one record.

    Example:
        patient = fetch_one(
            "SELECT * FROM patients WHERE mobile = ?",
            ("9876543210",)
        )
    """

    connection = get_connection()

    try:
        cursor = connection.execute(query, params)

        row = cursor.fetchone()

        if row:
            return dict(row)

        return None

    finally:
        connection.close()


# ============================================================
# 4. FETCH ALL RECORDS
# ============================================================

def fetch_all(query, params=()):
    """
    Executes a SELECT query and returns all records.

    Example:
        patients = fetch_all(
            "SELECT * FROM patients"
        )
    """

    connection = get_connection()

    try:
        cursor = connection.execute(query, params)

        rows = cursor.fetchall()

        return [dict(row) for row in rows]

    finally:
        connection.close()


# ============================================================
# 5. EXECUTE INSERT QUERY
# ============================================================

def insert_record(query, params=()):
    """
    Executes an INSERT query.

    Returns the ID of the newly inserted record.
    """

    connection = get_connection()

    try:
        cursor = connection.execute(query, params)

        connection.commit()

        return cursor.lastrowid

    except sqlite3.Error:
        connection.rollback()
        raise

    finally:
        connection.close()


# ============================================================
# 6. EXECUTE UPDATE OR DELETE QUERY
# ============================================================

def execute_query(query, params=()):
    """
    Executes an UPDATE or DELETE query.

    Returns the number of affected rows.
    """

    connection = get_connection()

    try:
        cursor = connection.execute(query, params)

        connection.commit()

        return cursor.rowcount

    except sqlite3.Error:
        connection.rollback()
        raise

    finally:
        connection.close()


# ============================================================
# 7. EXECUTE MULTIPLE INSERTS
# ============================================================

def execute_many(query, records):
    """
    Executes the same SQL query for multiple records.

    Returns the number of affected rows.
    """

    connection = get_connection()

    try:
        cursor = connection.executemany(query, records)

        connection.commit()

        return cursor.rowcount

    except sqlite3.Error:
        connection.rollback()
        raise

    finally:
        connection.close()


# ============================================================
# 8. COUNT RECORDS
# ============================================================

def count_records(table_name):
    """
    Returns the total number of records in a table.
    """

    allowed_tables = {
        "patients",
        "doctors",
        "visits",
        "daily_token_counters",
        "bills",
        "payments"
    }

    if table_name not in allowed_tables:
        raise ValueError("Invalid table name.")

    result = fetch_one(
        f"SELECT COUNT(*) AS total FROM {table_name}"
    )

    return result["total"] if result else 0


# ============================================================
# 9. CHECK DATABASE CONNECTION
# ============================================================

def check_connection():
    """
    Checks whether the SQLite database is accessible.
    """

    try:
        connection = get_connection()

        try:
            connection.execute("SELECT 1")

            return True

        finally:
            connection.close()

    except sqlite3.Error as error:
        print(f"Database connection error: {error}")
        return False


# ============================================================
# 10. GET DATABASE TABLES
# ============================================================

def get_tables():
    """
    Returns a list of application database tables.
    """

    rows = fetch_all(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
          AND name NOT LIKE 'sqlite_%'
        ORDER BY name
        """
    )

    return [row["name"] for row in rows]


# ============================================================
# 11. RUN DATABASE SETUP
# ============================================================

if __name__ == "__main__":

    print("=" * 50)
    print("HOSPITAL RECEPTION SYSTEM")
    print("SQLite Database Setup")
    print("=" * 50)

    if initialize_database():

        if check_connection():

            print("\nDatabase Connection: SUCCESS")

            print("\nDatabase Tables:")

            for table in get_tables():
                print(f" - {table}")

            print("\nRecord Counts:")

            for table in [
                "patients",
                "doctors",
                "visits",
                "bills",
                "payments"
            ]:
                print(f" {table}: {count_records(table)}")

        else:
            print("\nDatabase Connection: FAILED")

    else:
        print("\nDatabase Setup: FAILED")
