import os
from datetime import timedelta

from flask import Flask, abort, redirect, url_for, render_template
from flask_login import current_user
from dotenv import load_dotenv
from sqlalchemy import text

from extensions import db, login_manager
from models import SitePost, User

load_dotenv()


def create_app():
    app = Flask(__name__)
    app.config["JSON_AS_ASCII"] = False
    app.json.ensure_ascii = False
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-change-me-in-production")
    app.config["ADMIN_SETUP_KEY"] = os.getenv("ADMIN_SETUP_KEY", "")
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(hours=12)
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

    # اصلاح فرمت آدرس دیتابیس برای Render (سازگاری با PostgreSQL و SQLite)
    db_url = os.getenv("DATABASE_URL", "sqlite:///app.db")
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
        
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    login_manager.init_app(app)

    @app.after_request
    def set_utf8_response_charset(response):
        if response.mimetype in {"text/html", "application/json"}:
            response.charset = "utf-8"
        return response

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    from auth import auth_bp
    from dashboard import dashboard_bp
    from model_config import model_config_bp
    from cart import cart_bp
    from admin import POST_CATEGORIES, admin_bp, get_current_admin

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(model_config_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(admin_bp)

    with app.app_context():
        db.create_all()
        # مایگریشن خودکار فقط برای SQLite جهت جلوگیری از خطای 500
        if "sqlite" in app.config["SQLALCHEMY_DATABASE_URI"]:
            try:
                db.session.execute(text("ALTER TABLE model_entries ADD COLUMN is_active BOOLEAN DEFAULT 0;"))
                db.session.commit()
            except Exception:
                db.session.rollback()

            try:
                db.session.execute(text("ALTER TABLE users ADD COLUMN is_subscribed BOOLEAN DEFAULT 0;"))
                db.session.commit()
            except Exception:
                db.session.rollback()

            try:
                db.session.execute(text("ALTER TABLE users ADD COLUMN trial_started_at DATETIME;"))
                db.session.commit()
            except Exception:
                db.session.rollback()

    @app.context_processor
    def inject_global_template_values():
        return {"current_admin": get_current_admin()}

    @app.route("/")
    def index():
        published_posts = (
            SitePost.query.filter_by(is_published=True)
            .order_by(SitePost.published_at.desc(), SitePost.created_at.desc())
            .limit(24)
            .all()
        )
        post_sections = []
        for category_key, category_info in POST_CATEGORIES.items():
            post_sections.append(
                {
                    "key": category_key,
                    **category_info,
                    "posts": [
                        post
                        for post in published_posts
                        if post.category == category_key
                    ][:3],
                }
            )

        return render_template("index.html", post_sections=post_sections)

    @app.route("/posts/<int:post_id>")
    def post_detail(post_id):
        post = SitePost.query.get_or_404(post_id)
        if not post.is_published and get_current_admin() is None:
            abort(404)

        return render_template(
            "post_detail.html",
            post=post,
            category=POST_CATEGORIES.get(
                post.category,
                {"label": "مطالب سایت", "icon": "fa-file-lines"},
            ),
        )

    @app.route("/services")
    def services():
        return render_template("services.html")

    @app.route("/plans")
    def plans():
        from subscription import has_used_trial, is_trial_active, trial_days_left

        trial_used = current_user.is_authenticated and has_used_trial(current_user)
        trial_active = is_trial_active(current_user)
        days_left = trial_days_left(current_user) if current_user.is_authenticated else None
        return render_template(
            "plans.html",
            trial_used=trial_used,
            trial_active=trial_active,
            trial_days_left=days_left,
        )

    return app


app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 7860))
    app.run(debug=True, host="0.0.0.0", port=port)
