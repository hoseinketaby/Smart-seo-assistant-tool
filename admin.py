import re
import secrets
from datetime import datetime, timezone
from functools import wraps
from urllib.parse import urlparse

from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash

from extensions import db
from models import AdminAccount, SitePost

admin_bp = Blueprint("admin", __name__)

POST_CATEGORIES = {
    "news": {
        "label": "اخبار سایت",
        "description": "خبرها، اطلاعیه‌ها و اتفاق‌های مهم سایت",
        "icon": "fa-bullhorn",
    },
    "education": {
        "label": "آموزش سئو",
        "description": "آموزش‌های کاربردی برای رشد ورودی و محتوا",
        "icon": "fa-graduation-cap",
    },
    "updates": {
        "label": "به‌روزرسانی ابزار",
        "description": "قابلیت‌های تازه و تغییرات دستیار SEO",
        "icon": "fa-wand-magic-sparkles",
    },
    "guides": {
        "label": "نکات و راهنماها",
        "description": "راهنماهای کوتاه برای استفاده بهتر از سایت",
        "icon": "fa-compass",
    },
}


def normalize_admin_username(value):
    return (value or "").strip().casefold()


def get_current_admin():
    admin_id = session.get("admin_id")
    if not admin_id:
        return None

    try:
        admin_id = int(admin_id)
    except (TypeError, ValueError):
        session.pop("admin_id", None)
        return None

    admin = db.session.get(AdminAccount, admin_id)
    if admin is None:
        session.pop("admin_id", None)
    return admin


def authenticate_admin(identifier, password):
    username = normalize_admin_username(identifier)
    if not username or not password:
        return None

    admin = AdminAccount.query.filter_by(username=username).first()
    if admin and check_password_hash(admin.password_hash, password):
        return admin
    return None


def login_admin(admin):
    session["admin_id"] = admin.id
    session.permanent = True
    session.pop("_admin_csrf_token", None)


def logout_admin():
    session.pop("admin_id", None)
    session.pop("_admin_csrf_token", None)


def admin_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if get_current_admin() is None:
            flash("برای دسترسی به پنل مدیریت ابتدا وارد شوید.", "error")
            return redirect(url_for("admin.index"))
        return view(*args, **kwargs)

    return wrapped_view


def _csrf_token():
    token = session.get("_admin_csrf_token")
    if not token:
        token = secrets.token_urlsafe(32)
        session["_admin_csrf_token"] = token
    return token


def _require_valid_csrf():
    expected = session.get("_admin_csrf_token")
    submitted = request.form.get("csrf_token", "")
    if not expected or not secrets.compare_digest(expected, submitted):
        abort(400, description="درخواست نامعتبر است. صفحه را تازه‌سازی و دوباره تلاش کنید.")


def _validate_admin_fields(username, password, confirm_password):
    errors = []

    if len(username) < 3 or len(username) > 80:
        errors.append("نام کاربری مدیر باید بین ۳ تا ۸۰ کاراکتر باشد.")
    elif not re.fullmatch(r"[\w.@+-]+", username, flags=re.UNICODE):
        errors.append("نام کاربری فقط می‌تواند شامل حروف، عدد و نشانه‌های . @ + - _ باشد.")

    if len(password) < 8:
        errors.append("رمز عبور مدیر باید حداقل ۸ کاراکتر باشد.")

    if password != confirm_password:
        errors.append("رمز عبور و تکرار آن یکسان نیستند.")

    return errors


def _make_excerpt(content, limit=240):
    compact_content = " ".join(content.split())
    if len(compact_content) <= limit:
        return compact_content

    shortened = compact_content[: limit - 1].rsplit(" ", 1)[0]
    return f"{shortened or compact_content[: limit - 1]}…"


def _post_form_data():
    title = (request.form.get("title") or "").strip()
    excerpt = (request.form.get("excerpt") or "").strip()
    content = (request.form.get("content") or "").strip()
    category = (request.form.get("category") or "news").strip()
    cover_image_url = (request.form.get("cover_image_url") or "").strip()
    is_published = request.form.get("is_published") == "on"
    errors = []

    if not title:
        errors.append("عنوان پست الزامی است.")
    elif len(title) > 180:
        errors.append("عنوان پست نباید بیشتر از ۱۸۰ کاراکتر باشد.")

    if not content:
        errors.append("متن پست الزامی است.")

    if excerpt and len(excerpt) > 360:
        errors.append("خلاصه پست نباید بیشتر از ۳۶۰ کاراکتر باشد.")

    if category not in POST_CATEGORIES:
        errors.append("دسته‌بندی انتخاب‌شده معتبر نیست.")

    if cover_image_url:
        parsed_url = urlparse(cover_image_url)
        if parsed_url.scheme not in {"http", "https"} or not parsed_url.netloc:
            errors.append("نشانی تصویر باید با http یا https شروع شود.")

    return {
        "title": title,
        "excerpt": excerpt or _make_excerpt(content),
        "content": content,
        "category": category,
        "cover_image_url": cover_image_url or None,
        "is_published": is_published,
    }, errors


def _render_dashboard(admin):
    posts = SitePost.query.order_by(SitePost.created_at.desc()).all()
    return render_template(
        "admin/dashboard.html",
        admin=admin,
        posts=posts,
        categories=POST_CATEGORIES,
        published_count=sum(post.is_published for post in posts),
        draft_count=sum(not post.is_published for post in posts),
        admins_count=AdminAccount.query.count(),
    )


@admin_bp.context_processor
def inject_admin_template_values():
    return {
        "admin_csrf_token": _csrf_token,
        "post_categories": POST_CATEGORIES,
    }


@admin_bp.route("/admin", methods=["GET", "POST"])
def index():
    current_admin = get_current_admin()
    if current_admin:
        return _render_dashboard(current_admin)

    setup_mode = AdminAccount.query.first() is None
    username = ""

    if request.method == "POST":
        _require_valid_csrf()
        username = normalize_admin_username(request.form.get("username"))
        password = request.form.get("password") or ""

        if setup_mode:
            confirm_password = request.form.get("confirm_password") or ""
            errors = _validate_admin_fields(username, password, confirm_password)
            required_setup_key = current_app.config.get("ADMIN_SETUP_KEY", "")

            if required_setup_key and not secrets.compare_digest(
                required_setup_key,
                request.form.get("setup_key") or "",
            ):
                errors.append("کلید راه‌اندازی مدیریت صحیح نیست.")

            if AdminAccount.query.filter_by(username=username).first():
                errors.append("این نام کاربری مدیر قبلاً ثبت شده است.")

            if errors:
                for error in errors:
                    flash(error, "error")
            else:
                admin = AdminAccount(
                    username=username,
                    password_hash=generate_password_hash(password),
                )
                db.session.add(admin)
                db.session.commit()
                login_admin(admin)
                flash("حساب مدیر ساخته شد و اکنون می‌توانید پست منتشر کنید.", "success")
                return redirect(url_for("admin.index"))
        else:
            admin = authenticate_admin(username, password)
            if admin:
                login_admin(admin)
                flash("با موفقیت وارد پنل مدیریت شدید.", "success")
                return redirect(url_for("admin.index"))
            flash("نام کاربری یا رمز عبور مدیر اشتباه است.", "error")

    return render_template(
        "admin/login.html",
        setup_mode=setup_mode,
        setup_key_required=bool(current_app.config.get("ADMIN_SETUP_KEY")),
        username=username,
    )


@admin_bp.route("/admin/logout", methods=["POST"])
@admin_required
def logout():
    _require_valid_csrf()
    logout_admin()
    flash("از پنل مدیریت خارج شدید.", "success")
    return redirect(url_for("admin.index"))


@admin_bp.route("/admin/posts", methods=["POST"])
@admin_required
def create_post():
    _require_valid_csrf()
    admin = get_current_admin()
    post_data, errors = _post_form_data()

    if errors:
        for error in errors:
            flash(error, "error")
        return redirect(url_for("admin.index"))

    now = datetime.now(timezone.utc)
    post = SitePost(
        admin_id=admin.id,
        published_at=now if post_data["is_published"] else None,
        **post_data,
    )
    db.session.add(post)
    db.session.commit()
    flash(
        "پست با موفقیت منتشر شد." if post.is_published else "پیش‌نویس پست ذخیره شد.",
        "success",
    )
    return redirect(url_for("admin.index"))


@admin_bp.route("/admin/posts/<int:post_id>/edit", methods=["GET", "POST"])
@admin_required
def edit_post(post_id):
    post = SitePost.query.get_or_404(post_id)

    if request.method == "POST":
        _require_valid_csrf()
        post_data, errors = _post_form_data()

        if errors:
            for error in errors:
                flash(error, "error")
            return redirect(url_for("admin.edit_post", post_id=post.id))

        was_published = post.is_published
        for field, value in post_data.items():
            setattr(post, field, value)

        if post.is_published and not was_published:
            post.published_at = datetime.now(timezone.utc)

        db.session.commit()
        flash("تغییرات پست ذخیره شد.", "success")
        return redirect(url_for("admin.index"))

    return render_template(
        "admin/edit_post.html",
        admin=get_current_admin(),
        post=post,
        categories=POST_CATEGORIES,
    )


@admin_bp.route("/admin/posts/<int:post_id>/toggle", methods=["POST"])
@admin_required
def toggle_post(post_id):
    _require_valid_csrf()
    post = SitePost.query.get_or_404(post_id)
    post.is_published = not post.is_published
    if post.is_published:
        post.published_at = datetime.now(timezone.utc)
    db.session.commit()
    flash("وضعیت انتشار پست تغییر کرد.", "success")
    return redirect(url_for("admin.index"))


@admin_bp.route("/admin/posts/<int:post_id>/delete", methods=["POST"])
@admin_required
def delete_post(post_id):
    _require_valid_csrf()
    post = SitePost.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    flash("پست حذف شد.", "success")
    return redirect(url_for("admin.index"))


@admin_bp.route("/admin/accounts", methods=["POST"])
@admin_required
def create_admin_account():
    _require_valid_csrf()
    username = normalize_admin_username(request.form.get("username"))
    password = request.form.get("password") or ""
    confirm_password = request.form.get("confirm_password") or ""
    errors = _validate_admin_fields(username, password, confirm_password)

    if AdminAccount.query.filter_by(username=username).first():
        errors.append("این نام کاربری مدیر قبلاً ثبت شده است.")

    if errors:
        for error in errors:
            flash(error, "error")
        return redirect(url_for("admin.index"))

    admin = AdminAccount(
        username=username,
        password_hash=generate_password_hash(password),
    )
    db.session.add(admin)
    db.session.commit()
    flash("مدیر جدید با موفقیت اضافه شد.", "success")
    return redirect(url_for("admin.index"))
