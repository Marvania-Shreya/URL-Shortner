import os
import datetime
import random
import string

from flask import (
    Flask, render_template, request,
    redirect, jsonify, session, flash
)
from urllib.parse import urlparse

from models import (
    init_db,
    create_user,
    check_user,
    insert_url,
    get_user_urls,
    get_url,
    increment_click,
    delete_url,
    get_analytics,
    short_id_exists,
)

app = Flask(__name__)

# FIX: read secret key from environment variable; fall back to a default
# only for local development. In production, always set the SECRET_KEY env var.
app.secret_key = os.environ.get("SECRET_KEY", "dev-only-change-in-production")

# Initialize database on startup
init_db()


# -----------------------
# Helper – Short code generator (collision-safe)
# -----------------------
def generate_short():
    """Generate a unique 6-character alphanumeric short code."""
    chars = string.ascii_letters + string.digits  # 62 chars → 62^6 ≈ 56 billion
    for _ in range(10):  # FIX: retry up to 10 times to avoid collisions
        code = ''.join(random.choices(chars, k=6))
        if not short_id_exists(code):
            return code
    raise RuntimeError("Could not generate a unique short code. Try again.")


# -----------------------
# Helper – URL validation
# -----------------------
def is_valid_url(url):
    """FIX: only allow http/https URLs — blocks javascript: and internal URIs."""
    try:
        parsed = urlparse(url)
        return parsed.scheme in ("http", "https") and bool(parsed.netloc)
    except Exception:
        return False


# -----------------------
# Home → Dashboard
# -----------------------
@app.route("/")
def home():
    if "user" not in session:
        return redirect("/login")

    username = session["user"]
    urls = get_user_urls(username)
    return render_template("dashboard.html", urls=urls, username=username)


# -----------------------
# Create Short URL
# -----------------------
@app.route("/shorten", methods=["POST"])
def shorten():
    if "user" not in session:
        return redirect("/login")

    long_url = request.form.get("long_url", "").strip()
    expiry   = request.form.get("expiry", "")

    # FIX: validate URL before storing
    if not is_valid_url(long_url):
        flash("Please enter a valid URL starting with http:// or https://", "danger")
        return redirect("/")

    short = generate_short()
    insert_url(session["user"], long_url, short, expiry or None)

    flash("Short URL created!", "success")
    return redirect("/")


# -----------------------
# Redirect → Track Clicks
# -----------------------
@app.route("/<short>")
def redirect_short(short):
    data = get_url(short)

    if not data:
        return render_template("404.html"), 404

    long_url = data["long_url"]
    expiry   = data["expiry"]

    if expiry:
        expiry_date = datetime.datetime.strptime(expiry, "%Y-%m-%d").date()
        if datetime.date.today() > expiry_date:
            flash("This short URL has expired.", "danger")
            return render_template("404.html"), 410  # 410 Gone is more accurate

    increment_click(short)
    return redirect(long_url)


# -----------------------
# Delete URL
# -----------------------
@app.route("/delete/<short>")
def delete(short):
    if "user" not in session:
        return redirect("/login")
    delete_url(short)
    flash("URL deleted.", "info")
    return redirect("/")


# -----------------------
# Analytics
# -----------------------
@app.route("/analytics/<short>")
def analytics(short):
    if "user" not in session:
        return redirect("/login")
    data = get_analytics(short)

    if not data:
        return render_template("404.html"), 404

    return render_template("analytics.html", url=data)


# -----------------------
# REST API
# -----------------------
@app.route("/api/create", methods=["POST"])
def api_create():
    data     = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    long_url = data.get("url", "").strip()

    # FIX: validate URL in API too
    if not is_valid_url(long_url):
        return jsonify({"error": "Invalid URL. Must start with http:// or https://"}), 400

    short = generate_short()
    insert_url("API_USER", long_url, short, None)

    return jsonify({"short_url": f"http://localhost:5000/{short}"}), 201


@app.route("/api/analytics/<short>")
def api_analytics(short):
    data = get_analytics(short)

    if data:
        return jsonify(data)

    return jsonify({"error": "Not found"}), 404


# -----------------------
# Login
# -----------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if "user" in session:
        return redirect("/")

    if request.method == "POST":
        user = request.form.get("username", "").strip()
        pwd  = request.form.get("password", "")

        if check_user(user, pwd):
            session["user"] = user
            flash("Login successful!", "success")
            return redirect("/")

        flash("Invalid username or password.", "danger")

    return render_template("login.html")


# -----------------------
# Register
# -----------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if "user" in session:
        return redirect("/")

    if request.method == "POST":
        user = request.form.get("username", "").strip()
        pwd  = request.form.get("password", "")

        # FIX: basic input length validation
        if len(user) < 3:
            flash("Username must be at least 3 characters.", "danger")
            return render_template("register.html")

        if len(pwd) < 6:
            flash("Password must be at least 6 characters.", "danger")
            return render_template("register.html")

        if create_user(user, pwd):
            flash("Account created! Please log in.", "success")
            return redirect("/login")

        flash("Username already exists.", "danger")

    return render_template("register.html")


# -----------------------
# Logout
# -----------------------
@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect("/login")


# Run server
if __name__ == "__main__":
    # debug=True only for development — never use in production
    app.run(debug=True)
