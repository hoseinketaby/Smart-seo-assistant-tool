from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from extensions import db
from models import Order, CartItem
from cart import add_to_cart, get_cart_items, get_cart_total, clear_cart, checkout, PLANS
from payment import simulate_payment

cart_bp = Blueprint("cart", __name__, url_prefix="/cart")


@cart_bp.route("/")
@login_required
def index():
    """نمایش سبد خرید"""
    cart_items = get_cart_items(current_user.id)
    cart_total = get_cart_total(current_user.id)
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    
    # برای نمایش در سایدبار
    from subscription import trial_days_left, is_trial_active
    
    return render_template(
        "dashboard/cart.html",
        cart_items=cart_items,
        cart_total=cart_total,
        orders=orders,
        active_tab="cart",
        tabs=[],
        active_tab_info={"icon": "🛒", "label": "سبد خرید"},
        user=current_user,
        trial_locked=not is_trial_active(current_user),
        trial_days_left=trial_days_left(current_user),
    )


@cart_bp.route("/add/<plan_type>", methods=["POST"])
@login_required
def add(plan_type):
    """اضافه کردن پلن به سبد خرید"""
    success, message = add_to_cart(plan_type)
    
    if success:
        flash(message, "success")
    else:
        flash(message, "error")
    
    return redirect(url_for("cart.index"))


@cart_bp.route("/remove/<int:item_id>", methods=["POST"])
@login_required
def remove_from_cart(item_id):
    """حذف آیتم از سبد خرید"""
    item = CartItem.query.filter_by(id=item_id, user_id=current_user.id).first()
    if item:
        db.session.delete(item)
        db.session.commit()
        flash("آیتم از سبد خرید حذف شد.", "info")
    else:
        flash("آیتم یافت نشد.", "error")
    
    return redirect(url_for("cart.index"))


@cart_bp.route("/clear", methods=["POST"])
@login_required
def clear():
    """خالی کردن سبد خرید"""
    clear_cart(current_user.id)
    flash("سبد خرید خالی شد.", "info")
    return redirect(url_for("cart.index"))


@cart_bp.route("/checkout", methods=["POST"])
@login_required
def checkout_route():
    """ثبت سفارش و پرداخت"""
    success, result = checkout(current_user.id)
    
    if not success:
        flash(result, "error")
        return redirect(url_for("cart.index"))
    
    # پرداخت مبلغ صفر (دوره رایگان) یا هدایت به درگاه
    if result == 0:
        # برای مبلغ صفر، مستقیم پرداخت را شبیه‌سازی کن
        orders = Order.query.filter_by(user_id=current_user.id, status="pending").all()
        for order in orders:
            success, message = simulate_payment(order.id)
            if not success:
                flash(message, "error")
                return redirect(url_for("cart.index"))
        
        flash("🎉 دوره رایگان با موفقیت فعال شد!", "success")
        return redirect(url_for("dashboard.overview"))
    
    # برای مبالغ مثبت، هدایت به درگاه پرداخت (شبیه‌سازی شده)
    orders = Order.query.filter_by(user_id=current_user.id, status="pending").all()
    if not orders:
        flash("هیچ سفارش در انتظار پرداختی یافت نشد.", "error")
        return redirect(url_for("cart.index"))
    
    # در حالت واقعی، اینجا کاربر را به درگاه پرداخت هدایت کنید
    # و بعد از بازگشت، وضعیت پرداخت را بررسی کنید
    
    # شبیه‌سازی پرداخت
    for order in orders:
        success, message = simulate_payment(order.id)
        if not success:
            flash(message, "error")
            return redirect(url_for("cart.index"))
    
    flash("✅ پرداخت با موفقیت انجام شد. اشتراک شما فعال شد.", "success")
    return redirect(url_for("dashboard.overview"))


@cart_bp.route("/payment/verify", methods=["GET"])
@login_required
def payment_verify():
    """تایید پرداخت از درگاه (شبیه‌سازی شده)"""
    # در حالت واقعی، اینجا پارامترهای درگاه را دریافت کنید
    
    order_id = request.args.get("order_id")
    if order_id:
        success, message = simulate_payment(int(order_id))
        if success:
            flash("✅ پرداخت با موفقیت انجام شد.", "success")
        else:
            flash(message, "error")
    else:
        flash("اطلاعات پرداخت یافت نشد.", "error")
    
    return redirect(url_for("cart.index"))
