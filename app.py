from flask import Flask, render_template, request, redirect, session, jsonify
import random, string
from datetime import datetime, timedelta

from models import *

app = Flask(__name__)
app.secret_key = "secret123"

init_db()

def generate_code(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# ---------------- AUTH ----------------
@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        create_user(
            request.form["username"],
            request.form["password"]
        )
        return redirect("/login")
    return render_template("register.html")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        user = get_user(request.form["username"])
        if user and user[2] == request.form["password"]:
            session["user_id"] = user[0]
            return redirect("/")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# ---------------- HOME ----------------
@app.route("/", methods=["GET","POST"])
def index():
    if "user_id" not in session:
        return redirect("/login")

    if request.method == "POST":
        expiry = datetime.now() + timedelta(days=7)
        insert_url(
            request.form["url"],
            generate_code(),
            expiry.strftime("%Y-%m-%d %H:%M:%S"),
            session["user_id"]
        )
        return redirect("/")

    urls = get_user_urls(session["user_id"])
    return render_template("index.html", urls=urls)

# ---------------- REDIRECT ----------------
@app.route("/<code>")
def redirect_url(code):
    url = get_url(code)
    if not url:
        return render_template("404.html")

    if datetime.now() > datetime.strptime(url[4], "%Y-%m-%d %H:%M:%S"):
        return render_template("404.html")

    increase_click(code)
    return redirect(url[1])

# ---------------- ANALYTICS ----------------
@app.route("/analytics/<code>")
def analytics(code):
    url = get_url(code)
    return render_template("analytics.html", url=url)

# ---------------- DELETE ----------------
@app.route("/delete/<code>", methods=["POST"])
def delete(code):
    delete_url(code)
    return redirect("/")

# ---------------- REST API ----------------
@app.route("/api/urls")
def api_urls():
    return jsonify(get_user_urls(session["user_id"]))

if __name__ == "__main__":
    app.run(debug=True)
