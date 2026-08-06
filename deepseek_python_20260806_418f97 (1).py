"""
مدیریت سبد خرید
"""

from flask import session, flash, redirect, url_for, request
from flask_login import current_user
from extensions import db
from models import CartItem, Order
from trial import TRIAL_DAYS, TRIAL_PRICE, activate_trial

# تعریف پلن‌ها
PLANS = {
    "trial": {
        "name": "دوره ۷ روزه رایگان",
        "price": TRIAL_PRICE,
        "description": "۷ روز استفاده کامل از ابزار سئو",
    },
    "monthly": {
        "name": "پلن ماهانه",
        "price": 500000,  # ۵۰۰ هزار ریال
        "description": "یک ماه استفاده کامل از ابزار سئو",
    },
    "quarterly": {
        "name": "پلن سه‌ماهه",
        "price": 1200000,  # ۱ میلیون و ۲۰۰ هزار ریال
        "description": "سه ماه استفاده کامل از ابزار سئو با ۲۰٪ تخفیف",
    },
    "yearly": {
        "name": "پلن سالانه",
        "price": 4000000,  # ۴ میلیون ریال
        "description": "یک سال استفاده کامل از ابزار سئو با ۳۳٪ تخفیف",
    },
}


def add_to_cart(plan_type):
    """اضافه کردن پلن به سبد خرید"""
    if plan_type not in PLANS:
        return False, "پلن نامعتبر است."
    
    plan = PLANS[plan_type]
    
    # اگر پلن دوره رایگان است، مستقیم فعالش کن
    if plan_type == "trial":
        success, message = activate_trial(current_user)
        if success:
            flash("🎉 دوره ۷ روزه رایگان با موفقیت فعال شد! از ابزار سئو استفاده کنید.", "success")
        else:
            flash(message, "error")
        return success, message
    
    # بررسی اینکه کاربر قبلاً این پلن را در سبد خرید ندارد
    existing = CartItem.query.filter_by(user_id=current_user.id, plan_type=plan_type).first()
    if existing:
        return False, "این پلن قبلاً به سبد خرید اضافه شده است."
    
    cart_item = CartItem(
        user_id=current_user.id,
        plan_type=plan_type,
        plan_name=plan["name"],
        price=plan["price"],
    )
    db.session.add(cart_item)
    db.session.commit()
    
    return True, f"پلن «{plan['name']}» به سبد خرید اضافه شد."


def get_cart_items(user_id):
    """دریافت آیتم‌های سبد خرید کاربر"""
    return CartItem.query.filter_by(user_id=user_id).all()


def get_cart_total(user_id):
    """محاسبه مجموع مبلغ سبد خرید"""
    items = get_cart_items(user_id)
    return sum(item.price for item in items)


def clear_cart(user_id):
    """پاک کردن سبد خرید کاربر"""
    CartItem.query.filter_by(user_id=user_id).delete()
    db.session.commit()


def checkout(user_id):
    """ثبت نهایی سفارش و هدایت به درگاه پرداخت"""
    items = get_cart_items(user_id)
    if not items:
        return False, "سبد خرید شما خالی است."
    
    total = get_cart_total(user_id)
    
    # برای هر آیتم یک سفارش ایجاد کن
    for item in items:
        order = Order(
            user_id=user_id,
            plan_type=item.plan_type,
            plan_name=item.plan_name,
            amount=item.price,
            status="pending",
        )
        db.session.add(order)
    
    # پاک کردن سبد خرید
    clear_cart(user_id)
    db.session.commit()
    
    return True, total


def get_plan_info(plan_type):
    """دریافت اطلاعات یک پلن"""
    return PLANS.get(plan_type)