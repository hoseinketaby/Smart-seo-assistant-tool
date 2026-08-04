from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from extensions import db
from models import User

auth_bp = Blueprint("auth", __name__)


def _safe_next(value):
    """فقط مسیرهای داخلی سایت را به‌عنوان next می‌پذیرد (جلوگیری از Open Redirect)."""
    if value and value.startswith("/") and not value.startswith("//"):
        return value
    return None


@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.overview"))

    next_page = _safe_next(request.args.get("next") or request.form.get("next"))

    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""
        confirm_password = request.form.get("confirm_password") or ""

        if not email or not password:
            flash("ایمیل و رمز عبور الزامی است.", "error")
            return render_template("signup.html", email=email, next=next_page)

        if password != confirm_password:
            flash("رمز عبور و تکرار آن یکسان نیستند.", "error")
            return render_template("signup.html", email=email, next=next_page)

        if len(password) < 8:
            flash("رمز عبور باید حداقل ۸ کاراکتر باشد.", "error")
            return render_template("signup.html", email=email, next=next_page)

        if User.query.filter_by(email=email).first():
            flash("این ایمیل قبلاً ثبت شده است.", "error")
            return render_template("signup.html", email=email, next=next_page)

        user = User(email=email, password_hash=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()

        login_user(user)
        flash(
            "🎉 خوش آمدید! از همین حالا به مدت ۷ روز به‌صورت کاملاً رایگان به ابزار سئو دسترسی دارید.",
            "trial",
        )
        return redirect(next_page or url_for("dashboard.overview"))

    return render_template("signup.html", email="", next=next_page)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.overview"))

    next_page = _safe_next(request.args.get("next") or request.form.get("next"))

    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(next_page or url_for("dashboard.overview"))

        flash("ایمیل یا رمز عبور اشتباه است.", "error")
        return render_template("login.html", email=email, next=next_page)

    return render_template("login.html", email="", next=next_page)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
