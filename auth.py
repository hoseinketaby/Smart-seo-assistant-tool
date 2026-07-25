from flask import Blueprint, render_template
from flask_login import login_required, current_user

dashboard_bp = Blueprint("dashboard", __name__)

# Order here defines the order of tabs in the sidebar.
TABS = [
    {"key": "content-analyzer", "label": "تحلیل محتوا", "icon": "📊",
     "placeholder": "این بخش محتوای یک یا چند URL را واکشی و از نظر SEO تحلیل می‌کند - به‌زودی."},
    {"key": "youtube-research", "label": "پژوهش یوتیوب", "icon": "🎥",
     "placeholder": "این بخش پربازدیدترین ویدیوهای یوتیوب را بر اساس کلمه کلیدی پیدا می‌کند - به‌زودی."},
    {"key": "google-research", "label": "مقالات گوگل", "icon": "🔍",
     "placeholder": "این بخش برترین مقالات گوگل را بر اساس کلمه کلیدی پیدا می‌کند - به‌زودی."},
    {"key": "summarizer", "label": "خلاصه‌ساز", "icon": "📝",
     "placeholder": "این بخش همان خلاصه‌ساز محتوای وب/یوتیوب موجود است - در مرحله بعد منتقل می‌شود."},
    {"key": "history", "label": "تاریخچه", "icon": "🕒",
     "placeholder": "این بخش تحلیل‌ها و جستجوهای قبلی شما را نمایش می‌دهد - به‌زودی."},
]

TABS_BY_KEY = {t["key"]: t for t in TABS}


@dashboard_bp.route("/dashboard")
@dashboard_bp.route("/dashboard/<tab>")
@login_required
def overview(tab="content-analyzer"):
    if tab not in TABS_BY_KEY:
        tab = "content-analyzer"

    return render_template(
        "dashboard/base.html",
        tabs=TABS,
        active_tab=tab,
        active_tab_info=TABS_BY_KEY[tab],
        user=current_user,
    )
