import sqlite3

DB = "database.db"


def connect():
    return sqlite3.connect(DB)


def init_db():
    con = connect()
    c = con.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS urls (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        long_url TEXT,
        short_id TEXT UNIQUE,
        clicks INTEGER DEFAULT 0,
        expiry TEXT
    )
    """)

    con.commit()
    con.close()


# User system
def create_user(username, password):
    try:
        con = connect()
        c = con.cursor()
        c.execute("INSERT INTO users VALUES (?,?)", (username, password))
        con.commit()
        return True
    except:
        return False


def check_user(username, password):
    con = connect()
    c = con.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    return c.fetchone()


# URL functions
def insert_url(username, long_url, short, expiry):
    con = connect()
    c = con.cursor()
    c.execute(
        "INSERT INTO urls(username, long_url, short_id, expiry) VALUES (?,?,?,?)",
        (username, long_url, short, expiry)
    )
    con.commit()


def get_user_urls(username):
    con = connect()
    c = con.cursor()
    c.execute("SELECT long_url, short_id, clicks, expiry FROM urls WHERE username=?", (username,))
    return c.fetchall()


def get_url(short):
    con = connect()
    c = con.cursor()
    c.execute("SELECT long_url, expiry FROM urls WHERE short_id=?", (short,))
    row = c.fetchone()
    if row:
        return {"long_url": row[0], "expiry": row[1]}
    return None


def increment_click(short):
    con = connect()
    c = con.cursor()
    c.execute("UPDATE urls SET clicks = clicks + 1 WHERE short_id=?", (short,))
    con.commit()


def delete_url(short):
    con = connect()
    c = con.cursor()
    c.execute("DELETE FROM urls WHERE short_id=?", (short,))
    con.commit()


def get_analytics(short):
    con = connect()
    c = con.cursor()
    c.execute("SELECT long_url, short_id, clicks, expiry FROM urls WHERE short_id=?", (short,))
    row = c.fetchone()
    if row:
        return {
            "long_url": row[0],
            "short": row[1],
            "clicks": row[2],
            "expiry": row[3]
        }
    return None
