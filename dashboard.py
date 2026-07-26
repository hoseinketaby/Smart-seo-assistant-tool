from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user

from youtube_service import search_youtube_videos, summarize_youtube_video_text
from google_service import search_duckduckgo, search_google_html
from summarizer_service import summarize_article

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
     "placeholder": ""},
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
        google_results = search_google_html(google_query, max_results=10)
    
    elif tab == "duckduckgo-research":
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


@dashboard_bp.route("/dashboard/article/summarize", methods=["POST"])
@login_required
def summarize_article_route():
    """
    خلاصه‌سازی مقالات وب
    """
    data = request.get_json() or {}
    url = data.get("url")
    title = data.get("title", "مقاله")

    if not url:
        return jsonify({"error": "لینک مقاله ارسال نشده است."}), 400

    summary = summarize_article(url, title, current_user)
    return jsonify({"summary": summary})


@dashboard_bp.route("/dashboard/custom/summarize", methods=["POST"])
@login_required
def summarize_custom():
    """
    خلاصه‌سازی متن سفارشی کاربر
    """
    data = request.get_json() or {}
    text = data.get("text", "").strip()
    prompt = data.get("prompt", "").strip()
    source_type = data.get("source_type", "text")  # text, url
    url = data.get("url", "").strip()

    if source_type == "text" and not text:
        return jsonify({"error": "متن برای خلاصه‌سازی ارسال نشده است."}), 400
    
    if source_type == "url" and not url:
        return jsonify({"error": "لینک ارسال نشده است."}), 400

    # اگر منبع URL باشد
    if source_type == "url":
        from summarizer_service import extract_article_content
        content = extract_article_content(url)
        if not content:
            return jsonify({"error": "امکان استخراج محتوای مقاله وجود نداشت."}), 400
        text = content

    # خلاصه‌سازی با LLM
    summary = summarize_custom_text(text, prompt, current_user)
    return jsonify({"summary": summary})


def summarize_custom_text(text: str, prompt: str, user) -> str:
    """
    خلاصه‌سازی متن سفارشی با استفاده از LLM تنظیم شده کاربر
    """
    from extensions import db
    from models import Provider, ModelEntry
    from crypto_utils import decrypt_value
    
    # دریافت تنظیمات LLM کاربر
    active_model = (
        ModelEntry.query.join(Provider)
        .filter(Provider.user_id == user.id, ModelEntry.is_active == True)
        .first()
    )

    if not active_model:
        active_model = (
            ModelEntry.query.join(Provider)
            .filter(Provider.user_id == user.id)
            .first()
        )

    if not active_model or not active_model.provider:
        return "🔑 هیچ کلید API یا مدلی در بخش «مدیریت API Key» تنظیم نشده است. لطفاً ابتدا از منوی سمت راست وارد «مدیریت API Key» شوید و کلید و مدل خود را ثبت کنید."

    provider = active_model.provider
    api_key = decrypt_value(provider.api_key_encrypted)
    base_url = provider.base_url
    model_id = active_model.model_id

    # محدود کردن طول متن
    max_chars = 12000
    truncated_text = text[:max_chars]

    try:
        from langchain_openai import ChatOpenAI
        from langchain_core.messages import SystemMessage, HumanMessage

        kwargs = {
            "api_key": api_key,
            "model": model_id,
            "temperature": 0.5
        }
        if base_url:
            kwargs["base_url"] = base_url

        llm = ChatOpenAI(**kwargs)
        
        # اگر پرامپت کاربر خالی بود، از پرامپت پیش‌فرض استفاده کن
        if not prompt:
            prompt = "لطفاً متن زیر را خلاصه‌سازی کنید. نکات کلیدی و اصلی را استخراج کرده و به زبان فارسی روان و جذاب ارائه دهید."

        messages = [
            SystemMessage(
                content="شما یک دستیار حرفه‌ای خلاصه‌سازی متن هستید."
            ),
            HumanMessage(content=f"{prompt}\n\nمتن:\n{truncated_text}"),
        ]
        response = llm.invoke(messages)
        return response.content
    except Exception as e:
        return f"❌ خطا در برقراری ارتباط با مدل «{model_id}»: {str(e)}"
