from functools import wraps

from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user

from youtube_service import search_youtube_videos, summarize_youtube_video_text
from google_service import search_duckduckgo, search_google_html
from summarizer_service import summarize_article
from llm_config import get_active_user_llm_config
from keyword_service import get_related_keywords, ai_keyword_research
from subscription import is_trial_active, trial_days_left

dashboard_bp = Blueprint("dashboard", __name__)

TRIAL_EXPIRED_MESSAGE = (
    "⏳ دوره‌ی ۷ روزه استفاده رایگان شما به پایان رسیده است. "
    "برای ادامه استفاده از ابزار سئو، لطفاً یکی از پلن‌ها را از صفحه‌ی «پلن‌ها» تهیه کنید."
)


def trial_required(f):
    """جلوگیری از اجرای درخواست‌های ابزار سئو پس از پایان دوره‌ی رایگان."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not is_trial_active(current_user):
            return jsonify({"error": TRIAL_EXPIRED_MESSAGE}), 403
        return f(*args, **kwargs)
    return wrapper

TABS = [
    {"key": "content-analyzer", "label": "تحلیل محتوا", "icon": "📊",
     "endpoint": "dashboard.overview", "params": {"tab": "content-analyzer"},
     "placeholder": "محتوای متنی یا صفحات وب را از نظر SEO تحلیل کنید."},
    {"key": "youtube-research", "label": "پژوهش یوتیوب", "icon": "🎥",
     "endpoint": "dashboard.overview", "params": {"tab": "youtube-research"},
     "placeholder": ""},
    {"key": "google-research", "label": "مقالات گوگل", "icon": "🔍",
     "endpoint": "dashboard.overview", "params": {"tab": "google-research"},
     "placeholder": ""},
    {"key": "duckduckgo-research", "label": "جستجو با DuckDuckGo", "icon": "🦆",
     "endpoint": "dashboard.overview", "params": {"tab": "duckduckgo-research"},
     "placeholder": ""},
    {"key": "keyword-research", "label": "جستجوی کلمات کلیدی", "icon": "📈",
     "endpoint": "dashboard.overview", "params": {"tab": "keyword-research"},
     "placeholder": ""},
    {"key": "ai-keyword-research", "label": "جستجوی کلمات کلیدی با هوش مصنوعی", "icon": "✨",
     "endpoint": "dashboard.overview", "params": {"tab": "ai-keyword-research"},
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
    keyword_query = request.args.get("kwq", "").strip()
    keyword_results = []
    keyword_error = None

    trial_active = is_trial_active(current_user)
    trial_locked = not trial_active

    # اگر دوره‌ی رایگان کاربر تمام شده و اشتراکی هم ندارد، دیگر درخواست‌های
    # پرهزینه (جستجوی یوتیوب/گوگل/کلمات کلیدی) اجرا نمی‌شود؛ محتوای پنل به‌صورت
    # مات‌شده نمایش داده می‌شود و کاربر به صفحه‌ی پلن‌ها هدایت می‌شود.
    if trial_active:
        if tab == "youtube-research":
            yt_videos = search_youtube_videos(yt_query, max_results=10)

        elif tab == "google-research":
            google_results = search_google_html(google_query, max_results=10)

        elif tab == "duckduckgo-research":
            duckduckgo_results = search_duckduckgo(duckduckgo_query, max_results=10)

        elif tab == "keyword-research":
            keyword_results, keyword_error = get_related_keywords(current_user.id, keyword_query, max_results=30)

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
        keyword_results=keyword_results,
        keyword_query=keyword_query,
        keyword_error=keyword_error,
        trial_locked=trial_locked,
        trial_days_left=trial_days_left(current_user),
    )


@dashboard_bp.route("/dashboard/youtube/summarize", methods=["POST"])
@login_required
@trial_required
def summarize_youtube():
    data = request.get_json() or {}
    video_id = data.get("video_id")

    if not video_id:
        return jsonify({"error": "شناسه ویدیو ارسال نشده است."}), 400

    summary = summarize_youtube_video_text(video_id, current_user)
    return jsonify({"summary": summary})


@dashboard_bp.route("/dashboard/article/summarize", methods=["POST"])
@login_required
@trial_required
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


@dashboard_bp.route("/dashboard/keyword/ai-search", methods=["POST"])
@login_required
@trial_required
def ai_keyword_search():
    """
    جستجوی کلمات کلیدی با استفاده از هوش مصنوعی (بدون نیاز به API جستجوی کلمات کلیدی)
    """
    data = request.get_json() or {}
    keyword = (data.get("keyword") or "").strip()

    if not keyword:
        return jsonify({"error": "کلمه کلیدی ارسال نشده است."}), 400

    result = ai_keyword_research(keyword, current_user)
    return jsonify({"result": result})


@dashboard_bp.route("/dashboard/custom/summarize", methods=["POST"])
@login_required
@trial_required
def summarize_custom():
    """
    خلاصه‌سازی متن سفارشی کاربر
    """
    data = request.get_json() or {}
    text = data.get("text", "").strip()
    prompt = data.get("prompt", "").strip()
    source_type = data.get("source_type", "text")
    url = data.get("url", "").strip()

    if source_type == "text" and not text:
        return jsonify({"error": "متن برای خلاصه‌سازی ارسال نشده است."}), 400
    
    if source_type == "url" and not url:
        return jsonify({"error": "لینک ارسال نشده است."}), 400

    if source_type == "url":
        from summarizer_service import extract_article_content
        content = extract_article_content(url)
        if not content:
            return jsonify({"error": "امکان استخراج محتوای مقاله وجود نداشت."}), 400
        text = content

    summary = summarize_custom_text(text, prompt, current_user)
    return jsonify({"summary": summary})


def summarize_custom_text(text: str, prompt: str, user) -> str:
    """
    خلاصه‌سازی متن سفارشی با استفاده از LLM تنظیم شده کاربر
    """
    api_key, base_url, model_id, error_msg = get_active_user_llm_config(user.id)

    if error_msg:
        return error_msg

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


# ==================== تحلیل محتوا (Content Analyzer) ====================

@dashboard_bp.route("/dashboard/content/analyze", methods=["POST"])
@login_required
@trial_required
def analyze_content():
    """
    تحلیل محتوا از نظر SEO — ورودی متن دستی یا لینک وب
    """
    data = request.get_json() or {}
    text = data.get("text", "").strip()
    prompt = data.get("prompt", "").strip()
    source_type = data.get("source_type", "text")
    url = data.get("url", "").strip()

    if source_type == "text" and not text:
        return jsonify({"error": "متن برای تحلیل ارسال نشده است."}), 400

    if source_type == "url" and not url:
        return jsonify({"error": "لینک ارسال نشده است."}), 400

    if source_type == "url":
        from summarizer_service import extract_article_content
        content = extract_article_content(url)
        if not content:
            return jsonify({"error": "امکان استخراج محتوای صفحه وجود نداشت."}), 400
        text = content

    analysis = analyze_content_text(text, prompt, current_user)
    return jsonify({"analysis": analysis})


def analyze_content_text(text: str, prompt: str, user) -> str:
    """
    تحلیل محتوا با استفاده از LLM تنظیم‌شده کاربر
    """
    api_key, base_url, model_id, error_msg = get_active_user_llm_config(user.id)

    if error_msg:
        return error_msg

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

        if not prompt:
            prompt = (
                "لطفاً محتوای زیر را از نظر SEO به‌صورت حرفه‌ای تحلیل کنید. "
                "موارد زیر را بررسی کنید:\n"
                "• نقاط قوت محتوا\n"
                "• نقاط ضعف و نواقص\n"
                "• پیشنهادات بهبود (Actionable)\n"
                "• ساختار تیترها (Heading Structure)\n"
                "• کلمات کلیدی و چگالی آن‌ها\n"
                "• خوانایی و تجربه کاربری\n"
                "• سئو داخلی (Internal SEO)\n"
                "نتیجه را به زبان فارسی روان و تیتربندی‌شده ارائه دهید."
            )

        messages = [
            SystemMessage(
                content="شما یک متخصص حرفه‌ای SEO و تحلیلگر محتوا هستید. تحلیل‌های شما باید عمیق، دقیق، کاربردی و به زبان فارسی باشد."
            ),
            HumanMessage(content=f"{prompt}\n\nمحتوا:\n{truncated_text}"),
        ]
        response = llm.invoke(messages)
        return response.content
    except Exception as e:
        return f"❌ خطا در برقراری ارتباط با مدل «{model_id}»: {str(e)}"
