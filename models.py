import sqlite3

DB_NAME = "database.db"

def connect_db():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_url TEXT NOT NULL,
            short_code TEXT UNIQUE NOT NULL,
            clicks INTEGER DEFAULT 0
        )
    """)

    conn.commit()
    conn.close()

def insert_url(original_url, short_code):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO urls (original_url, short_code) VALUES (?, ?)",
        (original_url, short_code)
    )
    conn.commit()
    conn.close()

def get_url(short_code):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM urls WHERE short_code = ?",
        (short_code,)
    )
    data = cursor.fetchone()
    conn.close()
    return data

def get_all_urls():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM urls")
    data = cursor.fetchall()
    conn.close()
    return data

def increase_click(short_code):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE urls SET clicks = clicks + 1 WHERE short_code = ?",
        (short_code,)
    )
    conn.commit()
    conn.close()

def delete_url(short_code):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM urls WHERE short_code = ?",
        (short_code,)
    )
    conn.commit()
    conn.close()

