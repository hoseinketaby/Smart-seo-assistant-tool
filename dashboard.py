from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user

from youtube_service import search_youtube_videos, summarize_youtube_video_text
from google_service import search_duckduckgo, search_google_html

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
     "placeholder": ""},
    {"key": "duckduckgo-research", "label": "جستجو با DuckDuckGo", "icon": "🦆",
     "endpoint": "dashboard.overview", "params": {"tab": "duckduckgo-research"},
     "placeholder": ""},
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
    duckduckgo_results = []
    duckduckgo_query = request.args.get("dq", "").strip()

    if tab == "youtube-research":
        yt_videos = search_youtube_videos(yt_query, max_results=10)
    
    elif tab == "google-research":
        # روش دوم: جستجوی مستقیم گوگل (ممکن است محدود شود)
        google_results = search_google_html(google_query, max_results=10)
    
    elif tab == "duckduckgo-research":
        # روش اول: جستجوی DuckDuckGo (پایدارتر)
        duckduckgo_results = search_duckduckgo(duckduckgo_query, max_results=10)

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
        duckduckgo_results=duckduckgo_results,
        duckduckgo_query=duckduckgo_query,
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
