from datetime import datetime, timezone
from flask_login import UserMixin
from extensions import db


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # وضعیت اشتراک کاربر
    is_subscribed = db.Column(db.Boolean, default=False, nullable=False)
    
    # تاریخ شروع دوره رایگان (فقط زمانی که کاربر دکمه استفاده را بزند)
    trial_started_at = db.Column(db.DateTime, nullable=True)
    
    # وضعیت فعال بودن دوره رایگان
    is_trial_active = db.Column(db.Boolean, default=False, nullable=False)

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
    is_active = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


class KeywordProvider(db.Model):
    __tablename__ = "keyword_providers"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    preset_key = db.Column(db.String(50), nullable=False)
    api_key_encrypted = db.Column(db.Text, nullable=False)
    is_active = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


class CartItem(db.Model):
    """آیتم‌های سبد خرید کاربر"""
    __tablename__ = "cart_items"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    plan_type = db.Column(db.String(50), nullable=False)  # 'trial', 'monthly', 'quarterly', 'yearly'
    plan_name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer, nullable=False)  # قیمت به ریال
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    user = db.relationship("User", backref="cart_items")


class Order(db.Model):
    """سفارش‌های ثبت شده کاربر"""
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    plan_type = db.Column(db.String(50), nullable=False)
    plan_name = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Integer, nullable=False)  # مبلغ به ریال
    status = db.Column(db.String(50), default="pending")  # pending, paid, failed
    transaction_id = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    paid_at = db.Column(db.DateTime, nullable=True)
    
    user = db.relationship("User", backref="orders")
