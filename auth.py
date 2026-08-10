from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from admin import authenticate_admin, login_admin, logout_admin
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

        logout_admin()
        login_user(user)
        flash(
            "🎉 خوش آمدید! برای شروع، پلن «دوره‌ی آزمایشی ۷ روزه» (۰ تومان) را به سبد خرید اضافه کنید و خرید را تکمیل کنید.",
            "success",
        )
        return redirect(next_page or url_for("plans"))

    return render_template("signup.html", email="", next=next_page)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated and request.method == "GET":
        return redirect(url_for("dashboard.overview"))

    next_page = _safe_next(request.args.get("next") or request.form.get("next"))

    if request.method == "POST":
        identifier = (
            request.form.get("identifier")
            or request.form.get("email")
            or ""
        ).strip()
        password = request.form.get("password") or ""

        admin = authenticate_admin(identifier, password)
        if admin:
            if current_user.is_authenticated:
                logout_user()
            login_admin(admin)
            return redirect(url_for("admin.index"))

        email = identifier.lower()
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            logout_admin()
            login_user(user, remember=request.form.get("remember") == "on")
            return redirect(next_page or url_for("dashboard.overview"))

        flash("ایمیل، نام کاربری یا رمز عبور اشتباه است.", "error")
        return render_template("login.html", identifier=identifier, next=next_page)

    return render_template("login.html", identifier="", next=next_page)


@auth_bp.route("/logout")
def logout():
    if current_user.is_authenticated:
        logout_user()
    logout_admin()
    return redirect(url_for("auth.login"))
