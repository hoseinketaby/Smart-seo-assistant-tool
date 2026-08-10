"""
مدیریت دوره‌ی استفاده‌ی رایگان (Trial) کاربران ابزار سئو.

دوره‌ی رایگان ۷ روزه به‌صورت خودکار پس از ثبت‌نام فعال نمی‌شود؛ کاربر باید
از صفحه‌ی «پلن‌ها» پلن «دوره‌ی آزمایشی ۷ روزه» (به قیمت ۰ تومان) را به سبد
خرید خود اضافه کند و خرید را تکمیل کند. در آن لحظه فیلد trial_started_at
ثبت می‌شود و شمارش ۷ روز آغاز می‌گردد. پس از پایان این بازه، در صورتی که
کاربر اشتراک فعالی نداشته باشد (is_subscribed = True)، دسترسی او به ابزار
قفل می‌شود و باید یکی از پلن‌های موجود در صفحه‌ی «پلن‌ها» را تهیه کند.
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


def has_used_trial(user):
    """آیا دوره‌ی آزمایشی کاربر قبلاً فعال شده است؟ (فعال یا منقضی‌شده)"""
    return getattr(user, "trial_started_at", None) is not None


def activate_trial(user):
    """شروع دوره‌ی آزمایشی ۷ روزه از لحظه‌ی فعلی (فقط یک‌بار قابل فراخوانی است)."""
    if has_used_trial(user):
        return False
    user.trial_started_at = datetime.now(timezone.utc)
    return True


def trial_end_date(user):
    """تاریخ پایان دوره‌ی رایگان ۷ روزه‌ی کاربر (اگر هنوز فعال نشده باشد None)."""
    start = getattr(user, "trial_started_at", None)
    if start is None:
        return None
    return _aware(start) + timedelta(days=TRIAL_DAYS)


def is_trial_active(user):
    """
    آیا کاربر هنوز مجاز به استفاده از ابزار سئو است؟
    (یعنی یا در بازه‌ی ۷ روز رایگان است، یا اشتراک خریداری‌شده‌ی فعال دارد)
    """
    if not user or not getattr(user, "is_authenticated", False):
        return False
    if getattr(user, "is_subscribed", False):
        return True
    end = trial_end_date(user)
    if end is None:
        return False
    return datetime.now(timezone.utc) < end


def trial_days_left(user):
    """تعداد روزهای باقی‌مانده از دوره‌ی رایگان (برای نمایش به کاربر)."""
    if getattr(user, "is_subscribed", False):
        return None
    end = trial_end_date(user)
    if end is None:
        return None
    remaining_seconds = (end - datetime.now(timezone.utc)).total_seconds()
    if remaining_seconds <= 0:
        return 0
    return max(1, math.ceil(remaining_seconds / 86400))
