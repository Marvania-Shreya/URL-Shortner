import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

DB = "database.db"


def connect():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row  # allows dict-style access: row["column"]
    return conn


# -----------------------
# Initialize Database
# -----------------------
def init_db():
    con = connect()
    c = con.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT NOT NULL
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS urls (
        id       INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT    NOT NULL,
        long_url TEXT    NOT NULL,
        short_id TEXT    UNIQUE NOT NULL,
        clicks   INTEGER DEFAULT 0,
        expiry   TEXT
    )
    """)

    con.commit()
    con.close()


# -----------------------
# User system
# -----------------------
def create_user(username, password):
    """Return True on success, False if username already exists."""
    try:
        con = connect()
        c = con.cursor()
        # FIX: hash the password before storing — never store plain text
        hashed = generate_password_hash(password)
        c.execute(
            "INSERT INTO users(username, password) VALUES (?, ?)",
            (username, hashed),
        )
        con.commit()
        con.close()
        return True
    except sqlite3.IntegrityError:
        return False


def check_user(username, password):
    """Return True if credentials are valid, False otherwise."""
    con = connect()
    c = con.cursor()
    c.execute("SELECT password FROM users WHERE username=?", (username,))
    row = c.fetchone()
    con.close()

    if row is None:
        return False
    # FIX: use check_password_hash to compare against stored hash
    return check_password_hash(row["password"], password)


# -----------------------
# URL functions
# -----------------------
def short_id_exists(short):
    """Check whether a short_id is already taken."""
    con = connect()
    c = con.cursor()
    c.execute("SELECT 1 FROM urls WHERE short_id=?", (short,))
    exists = c.fetchone() is not None
    con.close()
    return exists


def insert_url(username, long_url, short, expiry):
    con = connect()
    c = con.cursor()
    c.execute(
        "INSERT INTO urls(username, long_url, short_id, expiry) VALUES (?, ?, ?, ?)",
        (username, long_url, short, expiry),
    )
    con.commit()
    con.close()


def get_user_urls(username):
    con = connect()
    c = con.cursor()
    c.execute(
        "SELECT long_url, short_id, clicks, expiry FROM urls WHERE username=?",
        (username,),
    )
    rows = c.fetchall()
    con.close()
    return rows


def get_url(short):
    con = connect()
    c = con.cursor()
    c.execute(
        "SELECT long_url, expiry FROM urls WHERE short_id=?",
        (short,),
    )
    row = c.fetchone()
    con.close()

    if row:
        return {"long_url": row["long_url"], "expiry": row["expiry"]}
    return None


def increment_click(short):
    con = connect()
    c = con.cursor()
    # atomic increment — no read-then-write race condition
    c.execute(
        "UPDATE urls SET clicks = clicks + 1 WHERE short_id=?",
        (short,),
    )
    con.commit()
    con.close()


def delete_url(short):
    con = connect()
    c = con.cursor()
    c.execute("DELETE FROM urls WHERE short_id=?", (short,))
    con.commit()
    con.close()


def get_analytics(short):
    con = connect()
    c = con.cursor()
    c.execute(
        "SELECT long_url, short_id, clicks, expiry FROM urls WHERE short_id=?",
        (short,),
    )
    row = c.fetchone()
    con.close()

    if row:
        return {
            "long_url": row["long_url"],
            "short":    row["short_id"],
            "clicks":   row["clicks"],
            "expiry":   row["expiry"],
        }
    return None
