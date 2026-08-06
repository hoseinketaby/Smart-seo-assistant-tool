"""
مدیریت دوره‌ی استفاده‌ی رایگان (Trial) کاربران ابزار سئو.
اکنون از trial.py برای مدیریت فعال‌سازی و وضعیت استفاده می‌کند.
"""

from datetime import datetime, timezone, timedelta
from trial import is_trial_valid, get_trial_days_left as get_trial_days_left_from_trial


TRIAL_DAYS = 7


def _aware(dt):
    if dt is None:
        return datetime.now(timezone.utc)
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def trial_end_date(user):
    """تاریخ پایان دوره‌ی رایگان ۷ روزه‌ی کاربر."""
    if not user.is_trial_active or not user.trial_started_at:
        return None
    return _aware(user.trial_started_at) + timedelta(days=TRIAL_DAYS)


def is_trial_active(user):
    """
    آیا کاربر هنوز مجاز به استفاده از ابزار سئو است؟
    (یعنی یا در بازه‌ی ۷ روز رایگان است، یا اشتراک خریداری‌شده‌ی فعال دارد)
    """
    if not user or not getattr(user, "is_authenticated", False):
        return False
    if getattr(user, "is_subscribed", False):
        return True
    return is_trial_valid(user)


def trial_days_left(user):
    """تعداد روزهای باقی‌مانده از دوره‌ی رایگان (برای نمایش به کاربر)."""
    if getattr(user, "is_subscribed", False):
        return None
    return get_trial_days_left_from_trial(user)
