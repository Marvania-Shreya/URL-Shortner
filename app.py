from flask import Flask, render_template, request, redirect, jsonify, session, flash
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
)
import datetime
import random
import string

app = Flask(__name__)
app.secret_key = "supersecretkey"

init_db()


# -----------------------
# Helper – Short code generator
# -----------------------
def generate_short():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=6))


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

    long_url = request.form["long_url"]
    expiry = request.form["expiry"]  # YYYY-MM-DD
    short = generate_short()

    insert_url(session["user"], long_url, short, expiry)
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
    expiry = data["expiry"]

    if expiry:
        expiry_date = datetime.datetime.strptime(expiry, "%Y-%m-%d").date()
        if datetime.date.today() > expiry_date:
            return "❌ This URL has expired."

    increment_click(short)
    return redirect(long_url)


# -----------------------
# Delete URL
# -----------------------
@app.route("/delete/<short>")
def delete(short):
    delete_url(short)
    flash("URL deleted", "info")
    return redirect("/")


# -----------------------
# Analytics
# -----------------------
@app.route("/analytics/<short>")
def analytics(short):
    data = get_analytics(short)
    if not data:
        return render_template("404.html"), 404
    return render_template("analytics.html", url=data)


# -----------------------
# REST API ENDPOINTS
# -----------------------
@app.route("/api/create", methods=["POST"])
def api_create():
    data = request.json
    long_url = data.get("url")

    short = generate_short()
    insert_url("API_USER", long_url, short, None)

    return jsonify({"short_url": f"http://localhost:5000/{short}"})


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
    if request.method == "POST":
        user = request.form["username"]
        pwd = request.form["password"]

        if check_user(user, pwd):
            session["user"] = user
            flash("Login successful!", "success")
            return redirect("/")
        flash("Invalid credentials", "danger")

    return render_template("login.html")


# -----------------------
# Register
# -----------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        user = request.form["username"]
        pwd = request.form["password"]

        created = create_user(user, pwd)
        if created:
            flash("Account created!", "success")
            return redirect("/login")
        flash("Username already exists!", "danger")

    return render_template("register.html")


# -----------------------
# Logout
# -----------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


app.run(debug=True)
