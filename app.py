import os
from flask import Flask, redirect, url_for
from flask_login import current_user
from dotenv import load_dotenv
from sqlalchemy import text

from extensions import db, login_manager
from models import User

load_dotenv()


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-change-me-in-production")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///app.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    from auth import auth_bp
    from dashboard import dashboard_bp
    from model_config import model_config_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(model_config_bp)  # ثبت بلوپرینت مدیریت API Keyها

    with app.app_context():
        db.create_all()
        # مایگریشن خودکار: اضافه کردن ستون is_active اگر در دیتابیس موجود نباشد (جلوگیری از خطای ۵۰۰)
        try:
            db.session.execute(text("ALTER TABLE model_entries ADD COLUMN is_active BOOLEAN DEFAULT 0;"))
            db.session.commit()
        except Exception:
            db.session.rollback()  # اگر ستون قبلاً وجود داشت، خطایی رخ ندهد

    @app.route("/")
    def index():
        if current_user.is_authenticated:
            return redirect(url_for("dashboard.overview"))
        return redirect(url_for("auth.login"))

    return app


app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 7860))
    app.run(debug=True, host="0.0.0.0", port=port)
