import sqlite3

DB_NAME = "database.db"

def connect_db():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = connect_db()
    cursor = conn.cursor()

    # USERS TABLE
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    """)

    # URLS TABLE
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_url TEXT,
            short_code TEXT UNIQUE,
            clicks INTEGER DEFAULT 0,
            expiry_date TEXT,
            user_id INTEGER
        )
    """)

    conn.commit()
    conn.close()

# ---------- USER FUNCTIONS ----------
def create_user(username, password):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (username, password) VALUES (?, ?)",
        (username, password)
    )
    conn.commit()
    conn.close()

def get_user(username):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=?", (username,))
    user = cursor.fetchone()
    conn.close()
    return user

# ---------- URL FUNCTIONS ----------
def insert_url(original_url, short_code, expiry_date, user_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO urls (original_url, short_code, expiry_date, user_id) VALUES (?, ?, ?, ?)",
        (original_url, short_code, expiry_date, user_id)
    )
    conn.commit()
    conn.close()

def get_url(short_code):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM urls WHERE short_code=?", (short_code,))
    data = cursor.fetchone()
    conn.close()
    return data

def get_user_urls(user_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM urls WHERE user_id=?", (user_id,))
    data = cursor.fetchall()
    conn.close()
    return data

def increase_click(short_code):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE urls SET clicks = clicks + 1 WHERE short_code=?",
        (short_code,)
    )
    conn.commit()
    conn.close()

def delete_url(short_code):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM urls WHERE short_code=?", (short_code,))
    conn.commit()
    conn.close()
