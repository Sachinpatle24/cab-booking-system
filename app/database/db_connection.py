import pyodbc
from flask import current_app
from contextlib import contextmanager

def get_db_connection():
    try:
        connection_string = (
            f"DRIVER={{{current_app.config['DB_DRIVER']}}};"
            f"SERVER={current_app.config['DB_SERVER']};"
            f"DATABASE={current_app.config['DB_NAME']};"
            "Trusted_Connection=yes;"
            "TrustServerCertificate=yes;"
        )
        return pyodbc.connect(connection_string, timeout=10)
    except Exception as e:
        print(f"Database connection failed: {e}")
        return None

@contextmanager
def get_db_cursor():
    conn = get_db_connection()
    if not conn:
        raise Exception("Database connection failed")
    try:
        cursor = conn.cursor()
        yield cursor
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
