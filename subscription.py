"""
مدیریت دوره‌ی استفاده‌ی رایگان (Trial) کاربران ابزار سئو.

هر کاربر از لحظه‌ی ثبت‌نام (created_at) به مدت ۷ روز به‌صورت رایگان و
کامل به ابزار سئو دسترسی دارد. پس از پایان این بازه، در صورتی که کاربر
اشتراک فعالی نداشته باشد (is_subscribed = True)، دسترسی او به ابزار قفل
می‌شود و باید یکی از پلن‌های موجود در صفحه‌ی «پلن‌ها» را تهیه کند.
"""

import math
from datetime import datetime, timezone, timedelta

TRIAL_DAYS = 7


def _aware(dt):
    """اطمینان از timezone-aware بودن تاریخ برای مقایسه‌ی درست."""
    if dt is None:
        return datetime.now(timezone.utc)
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def trial_end_date(user):
    """تاریخ پایان دوره‌ی رایگان ۷ روزه‌ی کاربر."""
    return _aware(user.created_at) + timedelta(days=TRIAL_DAYS)


def is_trial_active(user):
    """
    آیا کاربر هنوز مجاز به استفاده از ابزار سئو است؟
    (یعنی یا در بازه‌ی ۷ روز رایگان است، یا اشتراک خریداری‌شده‌ی فعال دارد)
    """
    if not user or not getattr(user, "is_authenticated", False):
        return False
    if getattr(user, "is_subscribed", False):
        return True
    return datetime.now(timezone.utc) < trial_end_date(user)


def trial_days_left(user):
    """تعداد روزهای باقی‌مانده از دوره‌ی رایگان (برای نمایش به کاربر)."""
    if getattr(user, "is_subscribed", False):
        return None
    remaining_seconds = (trial_end_date(user) - datetime.now(timezone.utc)).total_seconds()
    if remaining_seconds <= 0:
        return 0
    return max(1, math.ceil(remaining_seconds / 86400))
