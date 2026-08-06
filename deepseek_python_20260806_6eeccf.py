"""
مدیریت پرداخت (شبیه‌سازی شده برای نمایش)
"""

from datetime import datetime, timezone
from flask import flash, redirect, url_for
from flask_login import current_user
from extensions import db
from models import Order, User


def process_payment(order_id, payment_data=None):
    """
    پردازش پرداخت (شبیه‌سازی شده)
    
    در حالت واقعی، اینجا باید به درگاه پرداخت متصل شود.
    """
    order = Order.query.filter_by(id=order_id, user_id=current_user.id).first()
    if not order:
        return False, "سفارش یافت نشد."
    
    if order.status == "paid":
        return False, "این سفارش قبلاً پرداخت شده است."
    
    # شبیه‌سازی پرداخت موفق
    # در حالت واقعی، اینجا باید از درگاه پرداخت تایید بگیرید
    
    # برای پلن‌های با مبلغ صفر (مثل دوره رایگان) نیازی به پرداخت نیست
    if order.amount == 0:
        order.status = "paid"
        order.paid_at = datetime.now(timezone.utc)
        order.transaction_id = f"FREE_{order.id}_{int(datetime.now().timestamp())}"
        db.session.commit()
        
        # فعال‌سازی اشتراک کاربر
        current_user.is_subscribed = True
        db.session.commit()
        
        return True, "پرداخت با موفقیت انجام شد."
    
    # شبیه‌سازی پرداخت با مبلغ مثبت
    # در حالت واقعی، اینجا باید منتظر پاسخ از درگاه باشید
    order.status = "paid"
    order.paid_at = datetime.now(timezone.utc)
    order.transaction_id = f"PAY_{order.id}_{int(datetime.now().timestamp())}"
    db.session.commit()
    
    # فعال‌سازی اشتراک کاربر
    current_user.is_subscribed = True
    db.session.commit()
    
    return True, "پرداخت با موفقیت انجام شد."


def simulate_payment(order_id):
    """شبیه‌سازی پرداخت (برای تست)"""
    order = Order.query.filter_by(id=order_id, user_id=current_user.id).first()
    if not order:
        return False, "سفارش یافت نشد."
    
    if order.status == "paid":
        return False, "این سفارش قبلاً پرداخت شده است."
    
    order.status = "paid"
    order.paid_at = datetime.now(timezone.utc)
    order.transaction_id = f"SIM_{order.id}_{int(datetime.now().timestamp())}"
    db.session.commit()
    
    # فعال‌سازی اشتراک کاربر
    current_user.is_subscribed = True
    db.session.commit()
    
    return True, "پرداخت با موفقیت انجام شد."