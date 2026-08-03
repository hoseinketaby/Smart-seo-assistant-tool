import os
from flask import Flask, redirect, url_for, render_template
from flask_login import current_user
from dotenv import load_dotenv
from sqlalchemy import text

from extensions import db, login_manager
from models import User

load_dotenv()


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-change-me-in-production")

    # اصلاح فرمت آدرس دیتابیس برای Render (سازگاری با PostgreSQL و SQLite)
    db_url = os.getenv("DATABASE_URL", "sqlite:///app.db")
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
        
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url
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
    app.register_blueprint(model_config_bp)

    with app.app_context():
        db.create_all()
        # مایگریشن خودکار فقط برای SQLite جهت جلوگیری از خطای 500
        if "sqlite" in app.config["SQLALCHEMY_DATABASE_URI"]:
            try:
                db.session.execute(text("ALTER TABLE model_entries ADD COLUMN is_active BOOLEAN DEFAULT 0;"))
                db.session.commit()
            except Exception:
                db.session.rollback()

    @app.route("/")
    def index():
        return render_template("index.html")

    return app


app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 7860))
    app.run(debug=True, host="0.0.0.0", port=port)
