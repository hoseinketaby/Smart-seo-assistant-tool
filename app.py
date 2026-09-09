import os
from datetime import timedelta

from flask import Flask, Response, abort, redirect, url_for, render_template
from flask_login import current_user
from dotenv import load_dotenv
from sqlalchemy import text

from extensions import db, login_manager
from models import SitePost, User
from services_catalog import SERVICES, get_service

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

            # ستون‌های جدید تب سئو
            seo_columns = [
                ("site_posts", "focus_keyword", "VARCHAR(160)"),
                ("site_posts", "seo_title", "VARCHAR(70)"),
                ("site_posts", "meta_description", "VARCHAR(320)"),
                ("site_posts", "canonical_url", "VARCHAR(1024)"),
                ("site_posts", "og_image_url", "VARCHAR(1024)"),
                ("site_posts", "meta_robots_noindex", "BOOLEAN DEFAULT 0"),
                ("site_posts", "meta_robots_nofollow", "BOOLEAN DEFAULT 0"),
                ("site_posts", "seo_score", "INTEGER DEFAULT 0"),
            ]
            for table, column, col_type in seo_columns:
                try:
                    db.session.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {col_type};"))
                    db.session.commit()
                except Exception:
                    db.session.rollback()

    @app.context_processor
    def inject_global_template_values():
        from seo_service import get_seo_settings

        return {
            "current_admin": get_current_admin(),
            "services_catalog": SERVICES,
            "seo_settings": get_seo_settings(),
        }

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
        from seo_service import (
            effective_meta_description,
            effective_og_image,
            effective_seo_title,
            get_seo_settings,
        )

        post = SitePost.query.get_or_404(post_id)
        if not post.is_published and get_current_admin() is None:
            abort(404)

        seo_settings = get_seo_settings()
        robots_directives = []
        robots_directives.append("noindex" if post.meta_robots_noindex else "index")
        robots_directives.append("nofollow" if post.meta_robots_nofollow else "follow")

        return render_template(
            "post_detail.html",
            post=post,
            category=POST_CATEGORIES.get(
                post.category,
                {"label": "مطالب سایت", "icon": "fa-file-lines"},
            ),
            seo_title=effective_seo_title(post, seo_settings),
            seo_description=effective_meta_description(post, seo_settings),
            seo_image=effective_og_image(post, seo_settings),
            seo_canonical=post.canonical_url or url_for("post_detail", post_id=post.id, _external=True),
            seo_robots=", ".join(robots_directives),
        )

    @app.route("/sitemap.xml")
    def sitemap_xml():
        from seo_service import get_seo_settings

        seo_settings = get_seo_settings()
        urls = [
            {"loc": url_for("index", _external=True), "changefreq": "daily", "priority": "1.0"},
            {"loc": url_for("services", _external=True), "changefreq": "weekly", "priority": "0.6"},
            {"loc": url_for("plans", _external=True), "changefreq": "weekly", "priority": "0.6"},
        ]

        if seo_settings.sitemap_include_posts:
            published_posts = (
                SitePost.query.filter_by(is_published=True)
                .filter_by(meta_robots_noindex=False)
                .order_by(SitePost.updated_at.desc())
                .all()
            )
            for post in published_posts:
                urls.append(
                    {
                        "loc": url_for("post_detail", post_id=post.id, _external=True),
                        "lastmod": (post.updated_at or post.created_at).strftime("%Y-%m-%d"),
                        "changefreq": "weekly",
                        "priority": "0.8",
                    }
                )

        xml_parts = ['<?xml version="1.0" encoding="UTF-8"?>']
        xml_parts.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
        for item in urls:
            xml_parts.append("<url>")
            xml_parts.append(f"<loc>{item['loc']}</loc>")
            if item.get("lastmod"):
                xml_parts.append(f"<lastmod>{item['lastmod']}</lastmod>")
            xml_parts.append(f"<changefreq>{item['changefreq']}</changefreq>")
            xml_parts.append(f"<priority>{item['priority']}</priority>")
            xml_parts.append("</url>")
        xml_parts.append("</urlset>")

        return Response("".join(xml_parts), mimetype="application/xml")

    @app.route("/robots.txt")
    def robots_txt():
        from seo_service import get_seo_settings

        seo_settings = get_seo_settings()
        lines = ["User-agent: *", "Allow: /"]
        lines.append("Disallow: /admin")
        lines.append("Disallow: /dashboard")

        if seo_settings.robots_extra_rules:
            lines.append("")
            lines.extend(seo_settings.robots_extra_rules.splitlines())

        lines.append("")
        lines.append(f"Sitemap: {url_for('sitemap_xml', _external=True)}")

        return Response("\n".join(lines), mimetype="text/plain")

    @app.route("/services")
    def services():
        return render_template("services.html")

    @app.route("/services/<service_key>")
    def service_detail(service_key):
        service = get_service(service_key)
        if service is None:
            abort(404)

        other_services = [item for item in SERVICES if item["key"] != service_key]
        return render_template(
            "service_detail.html", service=service, other_services=other_services
        )

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
