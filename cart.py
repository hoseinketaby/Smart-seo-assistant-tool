"""
سبد خرید پلن‌های ابزار سئو.

در حال حاضر تنها پلن قابل خرید مستقیم، «دوره‌ی آزمایشی ۷ روزه» با قیمت
۰ تومان است که پس از تکمیل خرید، بلافاصله برای کاربر فعال می‌شود. پلن‌های
ماهانه/سه‌ماهه/سالانه همچنان از طریق تماس فعال می‌شوند.
"""

from flask import Blueprint, render_template, redirect, url_for, session, flash
from flask_login import login_required, current_user

from extensions import db
from subscription import activate_trial, has_used_trial

cart_bp = Blueprint("cart", __name__)

PLANS = {
    "trial_7day": {
        "key": "trial_7day",
        "name": "دوره‌ی آزمایشی ۷ روزه",
        "description": "دسترسی کامل و رایگان به همه‌ی ابزارهای سئو به مدت ۷ روز",
        "price": 0,  # تومان
    },
}


def _get_cart():
    """سبد خرید کاربر از روی سشن (لیست کلیدهای پلن)."""
    return session.setdefault("cart", [])


def _format_toman(amount):
    """نمایش قیمت به تومان با ارقام فارسی."""
    digits = "۰۱۲۳۴۵۶۷۸۹"
    return "".join(digits[int(d)] if d.isdigit() else d for d in f"{amount:,}")


@cart_bp.app_template_filter("toman")
def toman_filter(amount):
    return _format_toman(amount)


@cart_bp.route("/cart/add/<plan_key>", methods=["POST"])
@login_required
def add(plan_key):
    plan = PLANS.get(plan_key)
    if not plan:
        flash("پلن انتخاب‌شده معتبر نیست.", "error")
        return redirect(url_for("plans"))

    if plan_key == "trial_7day":
        if getattr(current_user, "is_subscribed", False):
            flash("اشتراک فعال دارید و نیازی به دوره‌ی آزمایشی ندارید.", "error")
            return redirect(url_for("plans"))
        if has_used_trial(current_user):
            flash("دوره‌ی آزمایشی ۷ روزه قبلاً برای حساب شما فعال شده است.", "error")
            return redirect(url_for("plans"))

    cart = _get_cart()
    if plan_key in cart:
        flash("این پلن از قبل در سبد خرید شما وجود است.", "info")
    else:
        cart.append(plan_key)
        session.modified = True
        flash(f"«{plan['name']}» به سبد خرید شما اضافه شد.", "success")
    return redirect(url_for("cart.view_cart"))


@cart_bp.route("/cart")
@login_required
def view_cart():
    items = [PLANS[key] for key in _get_cart() if key in PLANS]
    total = sum(item["price"] for item in items)
    return render_template("cart.html", items=items, total=total)


@cart_bp.route("/cart/remove/<plan_key>", methods=["POST"])
@login_required
def remove(plan_key):
    cart = _get_cart()
    if plan_key in cart:
        cart.remove(plan_key)
        session.modified = True
        flash("پلن از سبد خرید شما حذف شد.", "info")
    return redirect(url_for("cart.view_cart"))


@cart_bp.route("/cart/checkout", methods=["POST"])
@login_required
def checkout():
    cart = _get_cart()
    items = [PLANS[key] for key in cart if key in PLANS]

    if not items:
        flash("سبد خرید شما خالی است.", "error")
        return redirect(url_for("plans"))

    # فعال‌سازی دوره‌ی آزمایشی ۷ روزه (خرید با قیمت ۰ تومان)
    if "trial_7day" in cart:
        if getattr(current_user, "is_subscribed", False):
            session.pop("cart", None)
            flash("اشتراک فعال دارید و نیازی به دوره‌ی آزمایشی ندارید.", "info")
            return redirect(url_for("dashboard.overview"))
        if not activate_trial(current_user):
            session.pop("cart", None)
            flash("دوره‌ی آزمایشی ۷ روزه قبلاً برای حساب شما فعال شده است.", "error")
            return redirect(url_for("plans"))
        db.session.commit()
        session.pop("cart", None)
        flash(
            "🎉 دوره‌ی آزمایشی ۷ روزه با موفقیت فعال شد! از همین حالا به همه‌ی ابزارهای سئو دسترسی دارید.",
            "trial",
        )
        return redirect(url_for("dashboard.overview"))

    # پلن‌های پولی فعلاً از طریق تماس فعال می‌شوند.
    flash("برای تکمیل خرید این پلن لطفاً با ما تماس بگیرید: ۰۹۳۵۵۶۵۰۹۹۵", "info")
    return redirect(url_for("plans"))
