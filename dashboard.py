from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user

from youtube_service import search_youtube_videos, summarize_youtube_video_text, get_trending_youtube_videos

dashboard_bp = Blueprint("dashboard", __name__)

TABS = [
    {"key": "content-analyzer", "label": "تحلیل محتوا", "icon": "📊",
     "endpoint": "dashboard.overview", "params": {"tab": "content-analyzer"},
     "placeholder": "این بخش محتوای یک یا چند URL را واکشی و از نظر SEO تحلیل می‌کند - به‌زودی."},
    {"key": "youtube-research", "label": "پژوهش یوتیوب", "icon": "🎥",
     "endpoint": "dashboard.overview", "params": {"tab": "youtube-research"},
     "placeholder": ""},
    {"key": "google-research", "label": "مقالات گوگل", "icon": "🔍",
     "endpoint": "dashboard.overview", "params": {"tab": "google-research"},
     "placeholder": "این بخش برترین مقالات گوگل را بر اساس کلمه کلیدی پیدا می‌کند - به‌زودی."},
    {"key": "summarizer", "label": "خلاصه‌ساز", "icon": "📝",
     "endpoint": "dashboard.overview", "params": {"tab": "summarizer"},
     "placeholder": "این بخش همان خلاصه‌ساز محتوای وب/یوتیوب موجود است - در مرحله بعد منتقل می‌شود."},
    {"key": "api-keys", "label": "مدیریت API Key", "icon": "🔑",
     "endpoint": "model_config.index", "params": {},
     "placeholder": ""},
    {"key": "history", "label": "تاریخچه", "icon": "🕒",
     "endpoint": "dashboard.overview", "params": {"tab": "history"},
     "placeholder": "این بخش تحلیل‌ها و جستجوهای قبلی شما را نمایش می‌دهد - به‌زودی."},
]

TABS_BY_KEY = {t["key"]: t for t in TABS}


@dashboard_bp.route("/dashboard")
@dashboard_bp.route("/dashboard/<tab>")
@login_required
def overview(tab="content-analyzer"):
    if tab not in TABS_BY_KEY or tab == "api-keys":
        tab = "content-analyzer"

    yt_query = request.args.get("q", "").strip()
    yt_videos = []
    google_results = []
    google_query = request.args.get("gq", "").strip()

    if tab == "youtube-research":
        # اگر query خالی بود، ویدیوهای پرطرفدار نمایش داده می‌شوند
        yt_videos = search_youtube_videos(yt_query, max_results=10)
    
    elif tab == "google-research":
        # برای گوگل هم اگر query خالی بود، نتایج پرطرفدار نمایش داده می‌شوند
        google_results = search_google_articles(google_query, max_results=10)

    return render_template(
        "dashboard/base.html",
        tabs=TABS,
        active_tab=tab,
        active_tab_info=TABS_BY_KEY[tab],
        user=current_user,
        yt_videos=yt_videos,
        yt_query=yt_query,
        google_results=google_results,
        google_query=google_query,
    )


@dashboard_bp.route("/dashboard/youtube/summarize", methods=["POST"])
@login_required
def summarize_youtube():
    data = request.get_json() or {}
    video_id = data.get("video_id")

    if not video_id:
        return jsonify({"error": "شناسه ویدیو ارسال نشده است."}), 400

    summary = summarize_youtube_video_text(video_id, current_user)
    return jsonify({"summary": summary})


def search_google_articles(query: str, max_results: int = 10):
    """
    جستجوی مقالات در گوگل بدون نیاز به API key
    این تابع باید با استفاده از روش‌های scraping یا سرویس‌های جایگزین پیاده‌سازی شود
    """
    # TODO: پیاده‌سازی جستجوی گوگل بدون API key
    # می‌توان از کتابخانه‌هایی مانند requests-html یا selenium استفاده کرد
    # یا از سرویس‌های جایگزین مانند DuckDuckGo استفاده کرد
    
    if not query:
        # TODO: دریافت مقالات پرطرفدار یا پربازدید گوگل
        return []
    
    # TODO: پیاده‌سازی جستجو با query
    return []


def get_trending_google_articles(max_results: int = 10):
    """
    دریافت مقالات پرطرفدار گوگل بدون نیاز به API key
    """
    # TODO: پیاده‌سازی دریافت مقالات پرطرفدار گوگل
    return []
