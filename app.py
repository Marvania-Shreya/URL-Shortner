from flask import Flask, request, redirect, render_template
import random
import string

from models import (
    init_db,
    insert_url,
    get_url,
    get_all_urls,
    increase_click,
    delete_url
)

app = Flask(__name__)

# Create database table
init_db()

def generate_short_code(length=6):
    return ''.join(
        random.choices(string.ascii_letters + string.digits, k=length)
    )

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        original_url = request.form["url"]
        short_code = generate_short_code()
        insert_url(original_url, short_code)
        return redirect("/")

    all_urls = get_all_urls()
    return render_template("index.html", all_urls=all_urls)

@app.route("/<short_code>")
def redirect_url(short_code):
    url = get_url(short_code)

    if url:
        increase_click(short_code)
        return redirect(url[1])
    else:
        return render_template("404.html"), 404

@app.route("/delete/<short_code>", methods=["POST"])
def delete(short_code):
    delete_url(short_code)
    return redirect("/")

@app.route("/analytics/<short_code>")
def analytics(short_code):
    url = get_url(short_code)
    if url:
        return render_template("analytics.html", url=url)
    else:
        return render_template("404.html"), 404

if __name__ == "__main__":
    app.run(debug=True)


