from datetime import datetime, timezone
from flask_login import UserMixin
from extensions import db


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    # تاریخ شروع دوره‌ی آزمایشی ۷ روزه. تا زمانی که کاربر پلن آزمایشی را از
    # صفحه‌ی «پلن‌ها» به سبد خرید اضافه نکرده و تکمیل خرید نکرده باشد، این
    # مقدار None است و دوره‌ی رایگان به‌صورت خودکار فعال نمی‌شود.
    trial_started_at = db.Column(db.DateTime, nullable=True)
    # اگر کاربر یکی از پلن‌های ابزار سئو را خریداری کرده باشد، این مقدار True
    # می‌شود و دیگر محدودیت ۷ روز رایگان برای او اعمال نمی‌شود. در حال حاضر
    # فعال‌سازی این فیلد به‌صورت دستی (مثلاً از دیتابیس) انجام می‌شود.
    is_subscribed = db.Column(db.Boolean, default=False, nullable=False)

    providers = db.relationship("Provider", backref="user", lazy=True, cascade="all, delete-orphan")
    keyword_providers = db.relationship("KeywordProvider", backref="user", lazy=True, cascade="all, delete-orphan")


class AdminAccount(db.Model):
    __tablename__ = "admin_accounts"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    posts = db.relationship(
        "SitePost",
        back_populates="author",
        lazy=True,
        cascade="all, delete-orphan",
    )


class SitePost(db.Model):
    __tablename__ = "site_posts"

    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey("admin_accounts.id"), nullable=False, index=True)
    title = db.Column(db.String(180), nullable=False)
    excerpt = db.Column(db.String(360), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(40), nullable=False, default="news", index=True)
    cover_image_url = db.Column(db.String(1024), nullable=True)
    is_published = db.Column(db.Boolean, nullable=False, default=True, index=True)
    published_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    author = db.relationship("AdminAccount", back_populates="posts")


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
