from datetime import datetime, timezone
from flask_login import UserMixin
from extensions import db


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    providers = db.relationship("Provider", backref="user", lazy=True, cascade="all, delete-orphan")
    keyword_providers = db.relationship("KeywordProvider", backref="user", lazy=True, cascade="all, delete-orphan")


class Provider(db.Model):
    __tablename__ = "providers"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    name = db.Column(db.String(255), nullable=False)
    preset_key = db.Column(db.String(50), nullable=False)
    base_url = db.Column(db.String(512), nullable=True)
    api_key_encrypted = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    models = db.relationship("ModelEntry", backref="provider", lazy=True, cascade="all, delete-orphan")


class ModelEntry(db.Model):
    __tablename__ = "model_entries"

    id = db.Column(db.Integer, primary_key=True)
    provider_id = db.Column(db.Integer, db.ForeignKey("providers.id"), nullable=False, index=True)
    model_id = db.Column(db.String(255), nullable=False)
    display_name = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=False)  # مشخص‌کننده مدل فعال کاربر
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


class KeywordProvider(db.Model):
    """ابزار جستجوی کلمات کلیدی (مثل Mangools یا Keywords Everywhere) که کاربر کلید API خودش را برای آن ثبت کرده است."""
    __tablename__ = "keyword_providers"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    preset_key = db.Column(db.String(50), nullable=False)
    api_key_encrypted = db.Column(db.Text, nullable=False)
    is_active = db.Column(db.Boolean, default=False)  # مشخص‌کننده ابزار فعال کلمات کلیدی کاربر
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
