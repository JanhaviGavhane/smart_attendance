from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import select
from database import db
from models import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/")
def home():
    if current_user.is_authenticated:
        return redirect(url_for("auth.dashboard"))

    return redirect(url_for("auth.login"))


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("auth.dashboard"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not name or not email or not password or not confirm_password:
            flash("Please fill in all fields.", "error")
            return render_template("register.html")

        if len(name) > 100 or len(email) > 150:
            flash("Name or email is too long.", "error")
            return render_template("register.html")

        if len(password) < 8:
            flash("Password must contain at least 8 characters.", "error")
            return render_template("register.html")

        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return render_template("register.html")

        existing_user = db.session.execute(
            select(User).where(User.email == email)
        ).scalar_one_or_none()

        if existing_user:
            flash("An account with this email already exists.", "error")
            return render_template("register.html")

        user = User(
            name=name,
            email=email,
            password_hash=generate_password_hash(password)
        )

        db.session.add(user)
        db.session.commit()

        login_user(user)
        flash("Registration successful.", "success")
        return redirect(url_for("auth.dashboard"))

    return render_template("register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("auth.dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not email or not password:
            flash("Enter your email and password.", "error")
            return render_template("login.html")

        user = db.session.execute(
            select(User).where(User.email == email)
        ).scalar_one_or_none()

        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash("Welcome back.", "success")
            return redirect(url_for("auth.dashboard"))

        flash("Invalid email or password.", "error")

    return render_template("login.html")


@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("auth.login"))


@auth_bp.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")