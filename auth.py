import re

from flask import (
    Blueprint,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError

from models import User, db

bp = Blueprint("auth", __name__)

USERNAME_RE = re.compile(r"^[A-Za-z0-9_.-]{3,50}$")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
MIN_PASSWORD_LEN = 8

def _is_safe_next(target):
    return bool(target) and target.startswith("/") and not target.startswith("//")

@bp.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for("page_index"))

    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        email = (request.form.get("email") or "").strip()
        password = request.form.get("password") or ""
        confirm = request.form.get("confirm") or ""

        form = {"username": username, "email": email}

        error = None
        if not USERNAME_RE.match(username):
            error = ("Username must be 3–50 characters: letters, numbers, "
                     "and . _ - only.")
        elif not EMAIL_RE.match(email):
            error = "Please enter a valid email address."
        elif len(password) < MIN_PASSWORD_LEN:
            error = f"Password must be at least {MIN_PASSWORD_LEN} characters."
        elif password != confirm:
            error = "Passwords do not match."
        else:
            existing = (
                db.session.query(User)
                .filter(or_(User.username == username, User.email == email))
                .first()
            )
            if existing is not None:
                error = "That username or email is already taken."

        if error:
            return render_template("signup.html", error=error, form=form), 400

        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return (
                render_template(
                    "signup.html",
                    error="That username or email is already taken.",
                    form=form,
                ),
                409,
            )

        login_user(user)
        session.permanent = True
        return redirect(url_for("page_index"))

    return render_template("signup.html", form={})

@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("page_index"))

    if request.method == "POST":
        identifier = (request.form.get("identifier") or "").strip()
        password = request.form.get("password") or ""

        if not identifier or not password:
            return (
                render_template(
                    "login.html", error="Please enter your credentials."
                ),
                400,
            )

        user = (
            db.session.query(User)
            .filter(or_(User.username == identifier, User.email == identifier))
            .first()
        )

        if user is None or not user.check_password(password):
            return (
                render_template(
                    "login.html", error="Invalid credentials. Please try again."
                ),
                401,
            )

        login_user(user)
        session.permanent = True

        nxt = request.args.get("next")
        return redirect(nxt if _is_safe_next(nxt) else url_for("page_index"))

    return render_template("login.html")

@bp.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for("auth.login"))
