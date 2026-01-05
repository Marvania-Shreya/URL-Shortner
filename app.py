from flask import Flask, request, redirect, render_template
import random
import string

from models import (
    init_db,
    insert_url,
    get_url,
    get_all_urls,
    increment_visit_count,
    delete_url_by_code,
    get_url_by_original
)

app = Flask(__name__)
init_db()  # Sets up database table if not exists

def generate_short_code(length=6):
    """Generate a random short code"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# MAIN ROUTE
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        original_url = request.form["url"].strip()  # Remove extra spaces

        # DUPLICATE URL CHECK
        existing_url = get_url_by_original(original_url)
        if existing_url:
            # redirect to homepage OR show existing short code
            return redirect("/")

        # SAFE SHORT CODE GENERATION
        short_code = generate_short_code()
        insert_url(original_url, short_code)

        # Redirect prevents form resubmission
        return redirect("/")

    # GET request → show all URLs
    all_urls = get_all_urls()
    return render_template("index.html", all_urls=all_urls)

# REDIRECT ROUTE
@app.route("/<short_code>")
def redirect_short_url(short_code):
    url_data = get_url(short_code)
    if url_data:
        increment_visit_count(short_code)  # Count clicks
        return redirect(url_data[1])  # url_data[1] = original URL
    else:
        return render_template("404.html"), 404

# DELETE ROUTE
@app.route("/delete/<short_code>", methods=["POST"])
def delete_url(short_code):
    delete_url_by_code(short_code)
    return redirect("/")

# RUN THE APP
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)
