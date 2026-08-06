"""
مدیریت فعال‌سازی و استفاده از دوره رایگان ۷ روزه
"""

from datetime import datetime, timezone, timedelta
from flask import flash, redirect, url_for
from flask_login import current_user
from extensions import db

TRIAL_DAYS = 7
TRIAL_PRICE = 0  # قیمت دوره رایگان به ریال


def activate_trial(user):
    """فعال‌سازی دوره رایگان برای کاربر"""
    if user.is_trial_active:
        return False, "دوره رایگان شما قبلاً فعال شده است."
    
    if user.is_subscribed:
        return False, "شما قبلاً اشتراک فعال دارید."
    
    user.is_trial_active = True
    user.trial_started_at = datetime.now(timezone.utc)
    db.session.commit()
    return True, "دوره ۷ روزه رایگان با موفقیت فعال شد."


def is_trial_available(user):
    """بررسی اینکه آیا کاربر می‌تواند دوره رایگان را فعال کند"""
    if user.is_trial_active:
        return False, "دوره رایگان قبلاً فعال شده است."
    
    if user.is_subscribed:
        return False, "شما قبلاً اشتراک فعال دارید."
    
    return True, ""


def get_trial_end_date(user):
    """تاریخ پایان دوره رایگان"""
    if not user.is_trial_active or not user.trial_started_at:
        return None
    return user.trial_started_at + timedelta(days=TRIAL_DAYS)


def is_trial_valid(user):
    """بررسی اینکه آیا دوره رایگان هنوز معتبر است"""
    if not user.is_trial_active:
        return False
    
    if user.is_subscribed:
        return True
    
    end_date = get_trial_end_date(user)
    if not end_date:
        return False
    
    return datetime.now(timezone.utc) < end_date


def get_trial_days_left(user):
    """تعداد روزهای باقی‌مانده از دوره رایگان"""
    if not user.is_trial_active:
        return 0
    
    if user.is_subscribed:
        return None  # نامحدود
    
    end_date = get_trial_end_date(user)
    if not end_date:
        return 0
    
    remaining = (end_date - datetime.now(timezone.utc)).days
    return max(0, remaining)


def get_trial_price():
    """قیمت دوره رایگان (صفر ریال)"""
    return TRIAL_PRICE
