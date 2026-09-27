"""
Queen's Lards — a small family memory-sharing site.

This is a starter backend: it validates the sign-up and login forms and
keeps you logged in with a session cookie, but it stores accounts in memory
only (they reset every time the server restarts). Swap the `users` dict for
a real database before sharing this outside your immediate family.

Run it with:
    pip install flask
    python app.py
Then open http://127.0.0.1:5000 in your browser.
"""

import os
import re
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Change this before putting the site anywhere public.
app.secret_key = "please-change-this-secret-key"

# Where uploaded profile pictures are saved.
UPLOAD_FOLDER = os.path.join(app.static_folder, "uploads")
ALLOWED_PICTURE_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# In-memory "database" — good enough for a family project you're testing,
# not for something you leave running long-term. Keyed by lowercase email.
users = {}

# In-memory feed. Also resets on restart — swap for a real database (with
# an actual timestamp column) once you're ready to keep this permanently.
posts = []

AVATAR_CLASSES = ["", "rose", "gold"]

# In-memory list of family members added from the People page.
people = [
    {"name": "", "": ""},
    {"name": "", "": ""},
]

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def is_valid_email(email):
    return bool(EMAIL_PATTERN.match(email))


def logged_in():
    return "user_email" in session


def allowed_picture(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_PICTURE_EXTENSIONS


def current_user():
    """The signed-in user's record from `users`, or None."""
    email = session.get("user_email")
    return users.get(email) if email else None


# ---------- public pages ----------

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm", "")

        error = None
        if not name or not email or not password or not confirm:
            error = "Please fill in every field."
        elif not is_valid_email(email):
            error = "Please enter a valid email address."
        elif len(password) < 6:
            error = "Your password should be at least 6 characters."
        elif password != confirm:
            error = "Those passwords don't match."
        elif email in users:
            error = "An account with that email already exists."

        if error:
            return render_template("signup.html", error=error, name=name, email=email)

        users[email] = {"name": name, "password": password}
        session["user_email"] = email
        session["user_name"] = name
        return redirect(url_for("home"))

    return render_template("signup.html", error=None, name="", email="")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        error = None
        if not email or not password:
            error = "Please enter both your email and password."
        elif not is_valid_email(email):
            error = "Please enter a valid email address."
        elif email not in users or users[email]["password"] != password:
            error = "That email and password don't match our records."

        if error:
            return render_template("login.html", error=error, email=email)

        session["user_email"] = email
        session["user_name"] = users[email]["name"]
        return redirect(url_for("home"))

    return render_template("login.html", error=None, email="")


@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    return render_template("forgot_password.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


# ---------- pages you need to be logged in to see ----------

@app.route("/home")
def home():
    if not logged_in():
        return redirect(url_for("login"))
    user = current_user()
    # Newest first.
    return render_template(
        "home.html",
        user_name=session.get("user_name"),
        user_picture=user.get("picture") if user else None,
        posts=list(reversed(posts)),
    )


@app.route("/post", methods=["POST"])
def add_post():
    if not logged_in():
        return redirect(url_for("login"))

    content = request.form.get("content", "").strip()
    if content:
        name = session.get("user_name") or "Someone"
        posts.append({
            "who": name,
            "when": "Just now",
            "text": content,
            "photo": False,
            "avatar_class": AVATAR_CLASSES[len(posts) % len(AVATAR_CLASSES)],
            "initial": name[0].upper(),
        })

    return redirect(url_for("home"))


@app.route("/about")
def about():
    if not logged_in():
        return redirect(url_for("login"))
    return render_template("about.html", user_name=session.get("user_name"))


@app.route("/contact")
def contact():
    if not logged_in():
        return redirect(url_for("login"))
    return render_template("contact.html", user_name=session.get("user_name"))


@app.route("/people")
def people_page():
    if not logged_in():
        return redirect(url_for("login"))
    return render_template("people.html", people=people, error=None, name="", number="")


@app.route("/people/add", methods=["POST"])
def add_person():
    if not logged_in():
        return redirect(url_for("login"))

    name = request.form.get("name", "").strip()
    number = request.form.get("number", "").strip()

    error = None
    if not name or not number:
        error = "Please enter both a name and a number."

    if error:
        return render_template("people.html", people=people, error=error, name=name, number=number)

    people.append({"name": name, "number": number})
    return redirect(url_for("people_page"))


@app.route("/settings", methods=["GET", "POST"])
def settings():
    if not logged_in():
        return redirect(url_for("login"))

    user = current_user()
    error = None

    if request.method == "POST":
        picture = request.files.get("picture")
        if not picture or picture.filename == "":
            error = "Please choose a picture first."
        elif not allowed_picture(picture.filename):
            error = "Please upload a PNG, JPG, GIF, or WEBP image."
        else:
            email = session["user_email"]
            ext = picture.filename.rsplit(".", 1)[1].lower()
            filename = secure_filename(f"{email}.{ext}")
            picture.save(os.path.join(UPLOAD_FOLDER, filename))
            user["picture"] = filename

    return render_template(
        "settings.html",
        user_name=session.get("user_name"),
        user_picture=user.get("picture") if user else None,
        error=error,
    )


if __name__ == "__main__":
    app.run(debug=True)
