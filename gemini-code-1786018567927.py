from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime, timezone
from extensions import db

checkout_bp = Blueprint("checkout", __name__, url_prefix="/checkout")

# تعریف پلن‌ها و قیمت‌های آن‌ها (قیمت‌ها به ریال است)
PLANS = {
    "trial": {"name": "۷ روز رایگان", "price": 0, "days": 7},
    "monthly": {"name": "پلن ماهانه", "price": 1500000, "days": 30},
    "quarterly": {"name": "پلن سه‌ماهه", "price": 4000000, "days": 90},
    "yearly": {"name": "پلن سالانه", "price": 15000000, "days": 365}
}

@checkout_bp.route("/cart/<plan_id>")
@login_required
def cart(plan_id):
    if plan_id not in PLANS:
        flash("پلن انتخابی معتبر نیست.", "error")
        return redirect(url_for("plans"))
        
    plan = PLANS[plan_id]
    
    # بررسی اینکه آیا کاربر قبلاً از پلن رایگان استفاده کرده است یا خیر
    if plan_id == "trial" and current_user.trial_started_at is not None:
        flash("شما قبلاً از دوره ۷ روز رایگان استفاده کرده‌اید.", "error")
        return redirect(url_for("plans"))

    return render_template("cart.html", plan_id=plan_id, plan=plan)

@checkout_bp.route("/process/<plan_id>", methods=["POST"])
@login_required
def process_payment(plan_id):
    if plan_id not in PLANS:
        flash("پلن انتخابی معتبر نیست.", "error")
        return redirect(url_for("plans"))
        
    plan = PLANS[plan_id]
    
    # در صورتی که مبلغ 0 ریال باشد (پلن رایگان)
    if plan["price"] == 0:
        if plan_id == "trial":
            if current_user.trial_started_at is not None:
                flash("شما قبلاً از دوره رایگان استفاده کرده‌اید.", "error")
                return redirect(url_for("plans"))
            
            # فعال‌سازی زمان شروع دوره رایگان
            current_user.trial_started_at = datetime.now(timezone.utc)
            db.session.commit()
            flash("پلن ۷ روز رایگان شما با موفقیت فعال شد!", "success")
            return redirect(url_for("dashboard.overview"))
    else:
        # TODO: کدهای اتصال به درگاه پرداخت بانکی باید اینجا قرار بگیرند.
        # در حال حاضر برای شبیه‌سازی، اشتراک مستقیماً فعال می‌شود:
        flash("پرداخت شبیه‌سازی شد و اشتراک شما فعال گردید.", "success")
        current_user.is_subscribed = True
        db.session.commit()
        return redirect(url_for("dashboard.overview"))