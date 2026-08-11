from functools import wraps

from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user

from youtube_service import search_youtube_videos, summarize_youtube_video_text
from google_service import search_duckduckgo, search_google_html
from summarizer_service import summarize_article
from llm_config import get_active_user_llm_config
from keyword_service import get_related_keywords, ai_keyword_research
from keyword_mindmap_service import generate_keyword_mind_map
from subscription import is_trial_active, trial_days_left, has_used_trial

dashboard_bp = Blueprint("dashboard", __name__)

TRIAL_EXPIRED_MESSAGE = (
    "⏳ دوره‌ی ۷ روزه استفاده رایگان شما به پایان رسیده است. "
    "برای ادامه استفاده از ابزار سئو، لطفاً یکی از پلن‌ها را از صفحه‌ی «پلن‌ها» تهیه کنید."
)

TRIAL_NOT_STARTED_MESSAGE = (
    "🎁 برای استفاده از ابزار سئو، ابتدا پلن «دوره‌ی آزمایشی ۷ روزه» (۰ تومان) را "
    "از صفحه‌ی «پلن‌ها» به سبد خرید اضافه کنید و خرید را تکمیل کنید."
)


def trial_required(f):
    """Ø¬Ù„ÙˆÚ¯ÛŒØ±ÛŒ Ø§Ø² Ø§Ø¬Ø±Ø§ÛŒ Ø¯Ø±Ø®ÙˆØ§Ø³Øªâ€ŒÙ‡Ø§ÛŒ Ø§Ø¨Ø²Ø§Ø± Ø³Ø¦Ùˆ Ù¾ÛŒØ´ Ø§Ø² ÙØ¹Ø§Ù„â€ŒØ³Ø§Ø²ÛŒ ÛŒØ§ Ù¾Ø³ Ø§Ø² Ù¾Ø§ÛŒØ§Ù† Ø¯ÙˆØ±Ù‡â€ŒÛŒ Ø±Ø§ÛŒÚ¯Ø§Ù†."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not is_trial_active(current_user):
            message = TRIAL_EXPIRED_MESSAGE if has_used_trial(current_user) else TRIAL_NOT_STARTED_MESSAGE
            return jsonify({"error": message}), 403
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
    trial_not_started = not current_user.is_subscribed and not has_used_trial(current_user)

    # Ø§Ú¯Ø± Ø¯ÙˆØ±Ù‡â€ŒÛŒ Ø±Ø§ÛŒÚ¯Ø§Ù† Ú©Ø§Ø±Ø¨Ø± ÙØ¹Ø§Ù„ Ù†Ø´Ø¯Ù‡ ÛŒØ§ ØªÙ…Ø§Ù… Ø´Ø¯Ù‡ Ùˆ Ø§Ø´ØªØ±Ø§Ú©ÛŒ Ù‡Ù… Ù†Ø¯Ø§Ø±Ø¯ØŒ Ø¯ÛŒÚ¯Ø±
    # Ø¯Ø±Ø®ÙˆØ§Ø³Øªâ€ŒÙ‡Ø§ÛŒ Ù¾Ø±Ù‡Ø²ÛŒÙ†Ù‡ (Ø¬Ø³ØªØ¬ÙˆÛŒ ÛŒÙˆØªÛŒÙˆØ¨/Ú¯ÙˆÚ¯Ù„/Ú©Ù„Ù…Ø§Øª Ú©Ù„ÛŒØ¯ÛŒ) Ø§Ø¬Ø±Ø§ Ù†Ù…ÛŒâ€ŒØ´ÙˆØ¯Ø› Ù…Ø­ØªÙˆØ§ÛŒ
    # Ù¾Ù†Ù„ Ø¨Ù‡â€ŒØµÙˆØ±Øª Ù…Ø§Øªâ€ŒØ´Ø¯Ù‡ Ù†Ù…Ø§ÛŒØ´ Ø¯Ø§Ø¯Ù‡ Ù…ÛŒâ€ŒØ´ÙˆØ¯ Ùˆ Ú©Ø§Ø±Ø¨Ø± Ø¨Ù‡ ØµÙØ­Ù‡â€ŒÛŒ Ù¾Ù„Ù†â€ŒÙ‡Ø§ Ù‡Ø¯Ø§ÛŒØª Ù…ÛŒâ€ŒØ´ÙˆØ¯.
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
        trial_not_started=trial_not_started,
        trial_days_left=trial_days_left(current_user),
    )


@dashboard_bp.route("/dashboard/youtube/summarize", methods=["POST"])
@login_required
@trial_required
def summarize_youtube():
    data = request.get_json() or {}
    video_id = data.get("video_id")

    if not video_id:
        return jsonify({"error": "Ø´Ù†Ø§Ø³Ù‡ ÙˆÛŒØ¯ÛŒÙˆ Ø§Ø±Ø³Ø§Ù„ Ù†Ø´Ø¯Ù‡ Ø§Ø³Øª."}), 400

    summary = summarize_youtube_video_text(video_id, current_user)
    return jsonify({"summary": summary})


@dashboard_bp.route("/dashboard/article/summarize", methods=["POST"])
@login_required
@trial_required
def summarize_article_route():
    """
    Ø®Ù„Ø§ØµÙ‡â€ŒØ³Ø§Ø²ÛŒ Ù…Ù‚Ø§Ù„Ø§Øª ÙˆØ¨
    """
    data = request.get_json() or {}
    url = data.get("url")
    title = data.get("title", "Ù…Ù‚Ø§Ù„Ù‡")

    if not url:
        return jsonify({"error": "Ù„ÛŒÙ†Ú© Ù…Ù‚Ø§Ù„Ù‡ Ø§Ø±Ø³Ø§Ù„ Ù†Ø´Ø¯Ù‡ Ø§Ø³Øª."}), 400

    summary = summarize_article(url, title, current_user)
    return jsonify({"summary": summary})


@dashboard_bp.route("/dashboard/keyword/ai-search", methods=["POST"])
@login_required
@trial_required
def ai_keyword_search():
    """
    Ø¬Ø³ØªØ¬ÙˆÛŒ Ú©Ù„Ù…Ø§Øª Ú©Ù„ÛŒØ¯ÛŒ Ø¨Ø§ Ø§Ø³ØªÙØ§Ø¯Ù‡ Ø§Ø² Ù‡ÙˆØ´ Ù…ØµÙ†ÙˆØ¹ÛŒ (Ø¨Ø¯ÙˆÙ† Ù†ÛŒØ§Ø² Ø¨Ù‡ API Ø¬Ø³ØªØ¬ÙˆÛŒ Ú©Ù„Ù…Ø§Øª Ú©Ù„ÛŒØ¯ÛŒ)
    """
    data = request.get_json() or {}
    keyword = (data.get("keyword") or "").strip()

    if not keyword:
        return jsonify({"error": "Ú©Ù„Ù…Ù‡ Ú©Ù„ÛŒØ¯ÛŒ Ø§Ø±Ø³Ø§Ù„ Ù†Ø´Ø¯Ù‡ Ø§Ø³Øª."}), 400

    result = ai_keyword_research(keyword, current_user)
    return jsonify({"result": result})


@dashboard_bp.route("/dashboard/keyword/mindmap", methods=["POST"])
@login_required
@trial_required
def generate_keyword_mindmap():
    """
    Ø³Ø§Ø®Øª Mind Map Ù…Ø¨ØªÙ†ÛŒ Ø¨Ø± LLM Ø¨Ø±Ø§ÛŒ Ù„ÛŒØ³Øª Ú©Ù„Ù…Ø§Øª Ú©Ù„ÛŒØ¯ÛŒ Ø§Ø³ØªØ®Ø±Ø§Ø¬â€ŒØ´Ø¯Ù‡.
    """
    data = request.get_json() or {}
    keywords = data.get("keywords") or []

    if not isinstance(keywords, list) or not keywords:
        return jsonify({"error": "Ù„Ø·ÙØ§Ù‹ Ù„ÛŒØ³Øª Ú©Ù„Ù…Ø§Øª Ú©Ù„ÛŒØ¯ÛŒ Ù…Ø¹ØªØ¨Ø± Ø§Ø±Ø³Ø§Ù„ Ú©Ù†ÛŒØ¯."}), 400

    normalized = [str(k or "").strip() for k in keywords if str(k or "").strip()]
    if not normalized:
        return jsonify({"error": "Ù„ÛŒØ³Øª Ú©Ù„Ù…Ø§Øª Ú©Ù„ÛŒØ¯ÛŒ Ù…Ø¹ØªØ¨Ø± Ù†ÛŒØ³Øª."}), 400

    mind_map = generate_keyword_mind_map(normalized, current_user)
    return jsonify({"mind_map": mind_map})


@dashboard_bp.route("/dashboard/custom/summarize", methods=["POST"])
@login_required
@trial_required
def summarize_custom():
    """
    Ø®Ù„Ø§ØµÙ‡â€ŒØ³Ø§Ø²ÛŒ Ù…ØªÙ† Ø³ÙØ§Ø±Ø´ÛŒ Ú©Ø§Ø±Ø¨Ø±
    """
    data = request.get_json() or {}
    text = data.get("text", "").strip()
    prompt = data.get("prompt", "").strip()
    source_type = data.get("source_type", "text")
    url = data.get("url", "").strip()

    if source_type == "text" and not text:
        return jsonify({"error": "Ù…ØªÙ† Ø¨Ø±Ø§ÛŒ Ø®Ù„Ø§ØµÙ‡â€ŒØ³Ø§Ø²ÛŒ Ø§Ø±Ø³Ø§Ù„ Ù†Ø´Ø¯Ù‡ Ø§Ø³Øª."}), 400
    
    if source_type == "url" and not url:
        return jsonify({"error": "Ù„ÛŒÙ†Ú© Ø§Ø±Ø³Ø§Ù„ Ù†Ø´Ø¯Ù‡ Ø§Ø³Øª."}), 400

    if source_type == "url":
        from summarizer_service import extract_article_content
        content = extract_article_content(url)
        if not content:
            return jsonify({"error": "Ø§Ù…Ú©Ø§Ù† Ø§Ø³ØªØ®Ø±Ø§Ø¬ Ù…Ø­ØªÙˆØ§ÛŒ Ù…Ù‚Ø§Ù„Ù‡ ÙˆØ¬ÙˆØ¯ Ù†Ø¯Ø§Ø´Øª."}), 400
        text = content

    summary = summarize_custom_text(text, prompt, current_user)
    return jsonify({"summary": summary})



def summarize_custom_text(text: str, prompt: str, user) -> str:
    """
    Ø®Ù„Ø§ØµÙ‡â€ŒØ³Ø§Ø²ÛŒ Ù…ØªÙ† Ø³ÙØ§Ø±Ø´ÛŒ Ø¨Ø§ Ø§Ø³ØªÙØ§Ø¯Ù‡ Ø§Ø² LLM ØªÙ†Ø¸ÛŒÙ… Ø´Ø¯Ù‡ Ú©Ø§Ø±Ø¨Ø±
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
            prompt = "Ù„Ø·ÙØ§Ù‹ Ù…ØªÙ† Ø²ÛŒØ± Ø±Ø§ Ø®Ù„Ø§ØµÙ‡â€ŒØ³Ø§Ø²ÛŒ Ú©Ù†ÛŒØ¯. Ù†Ú©Ø§Øª Ú©Ù„ÛŒØ¯ÛŒ Ùˆ Ø§ØµÙ„ÛŒ Ø±Ø§ Ø§Ø³ØªØ®Ø±Ø§Ø¬ Ú©Ø±Ø¯Ù‡ Ùˆ Ø¨Ù‡ Ø²Ø¨Ø§Ù† ÙØ§Ø±Ø³ÛŒ Ø±ÙˆØ§Ù† Ùˆ Ø¬Ø°Ø§Ø¨ Ø§Ø±Ø§Ø¦Ù‡ Ø¯Ù‡ÛŒØ¯."

        messages = [
            SystemMessage(
                content="Ø´Ù…Ø§ ÛŒÚ© Ø¯Ø³ØªÛŒØ§Ø± Ø­Ø±ÙÙ‡â€ŒØ§ÛŒ Ø®Ù„Ø§ØµÙ‡â€ŒØ³Ø§Ø²ÛŒ Ù…ØªÙ† Ù‡Ø³ØªÛŒØ¯."
            ),
            HumanMessage(content=f"{prompt}\n\nÙ…ØªÙ†:\n{truncated_text}"),
        ]
        response = llm.invoke(messages)
        return response.content
    except Exception as e:
        return f"âŒ Ø®Ø·Ø§ Ø¯Ø± Ø¨Ø±Ù‚Ø±Ø§Ø±ÛŒ Ø§Ø±ØªØ¨Ø§Ø· Ø¨Ø§ Ù…Ø¯Ù„ Â«{model_id}Â»: {str(e)}"


# ==================== ØªØ­Ù„ÛŒÙ„ Ù…Ø­ØªÙˆØ§ (Content Analyzer) ====================

@dashboard_bp.route("/dashboard/content/analyze", methods=["POST"])
@login_required
@trial_required
def analyze_content():
    """
    ØªØ­Ù„ÛŒÙ„ Ù…Ø­ØªÙˆØ§ Ø§Ø² Ù†Ø¸Ø± SEO â€” ÙˆØ±ÙˆØ¯ÛŒ Ù…ØªÙ† Ø¯Ø³ØªÛŒ ÛŒØ§ Ù„ÛŒÙ†Ú© ÙˆØ¨
    """
    data = request.get_json() or {}
    text = data.get("text", "").strip()
    prompt = data.get("prompt", "").strip()
    source_type = data.get("source_type", "text")
    url = data.get("url", "").strip()

    if source_type == "text" and not text:
        return jsonify({"error": "Ù…ØªÙ† Ø¨Ø±Ø§ÛŒ ØªØ­Ù„ÛŒÙ„ Ø§Ø±Ø³Ø§Ù„ Ù†Ø´Ø¯Ù‡ Ø§Ø³Øª."}), 400

    if source_type == "url" and not url:
        return jsonify({"error": "Ù„ÛŒÙ†Ú© Ø§Ø±Ø³Ø§Ù„ Ù†Ø´Ø¯Ù‡ Ø§Ø³Øª."}), 400

    if source_type == "url":
        from summarizer_service import extract_article_content
        content = extract_article_content(url)
        if not content:
            return jsonify({"error": "Ø§Ù…Ú©Ø§Ù† Ø§Ø³ØªØ®Ø±Ø§Ø¬ Ù…Ø­ØªÙˆØ§ÛŒ ØµÙØ­Ù‡ ÙˆØ¬ÙˆØ¯ Ù†Ø¯Ø§Ø´Øª."}), 400
        text = content

    analysis = analyze_content_text(text, prompt, current_user)
    return jsonify({"analysis": analysis})


def analyze_content_text(text: str, prompt: str, user) -> str:
    """
    ØªØ­Ù„ÛŒÙ„ Ù…Ø­ØªÙˆØ§ Ø¨Ø§ Ø§Ø³ØªÙØ§Ø¯Ù‡ Ø§Ø² LLM ØªÙ†Ø¸ÛŒÙ…â€ŒØ´Ø¯Ù‡ Ú©Ø§Ø±Ø¨Ø±
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
                "Ù„Ø·ÙØ§Ù‹ Ù…Ø­ØªÙˆØ§ÛŒ Ø²ÛŒØ± Ø±Ø§ Ø§Ø² Ù†Ø¸Ø± SEO Ø¨Ù‡â€ŒØµÙˆØ±Øª Ø­Ø±ÙÙ‡â€ŒØ§ÛŒ ØªØ­Ù„ÛŒÙ„ Ú©Ù†ÛŒØ¯. "
                "Ù…ÙˆØ§Ø±Ø¯ Ø²ÛŒØ± Ø±Ø§ Ø¨Ø±Ø±Ø³ÛŒ Ú©Ù†ÛŒØ¯:\n"
                "â€¢ Ù†Ù‚Ø§Ø· Ù‚ÙˆØª Ù…Ø­ØªÙˆØ§\n"
                "â€¢ Ù†Ù‚Ø§Ø· Ø¶Ø¹Ù Ùˆ Ù†ÙˆØ§Ù‚Øµ\n"
                "â€¢ Ù¾ÛŒØ´Ù†Ù‡Ø§Ø¯Ø§Øª Ø¨Ù‡Ø¨ÙˆØ¯ (Actionable)\n"
                "â€¢ Ø³Ø§Ø®ØªØ§Ø± ØªÛŒØªØ±Ù‡Ø§ (Heading Structure)\n"
                "â€¢ Ú©Ù„Ù…Ø§Øª Ú©Ù„ÛŒØ¯ÛŒ Ùˆ Ú†Ú¯Ø§Ù„ÛŒ Ø¢Ù†â€ŒÙ‡Ø§\n"
                "â€¢ Ø®ÙˆØ§Ù†Ø§ÛŒÛŒ Ùˆ ØªØ¬Ø±Ø¨Ù‡ Ú©Ø§Ø±Ø¨Ø±ÛŒ\n"
                "â€¢ Ø³Ø¦Ùˆ Ø¯Ø§Ø®Ù„ÛŒ (Internal SEO)\n"
                "Ù†ØªÛŒØ¬Ù‡ Ø±Ø§ Ø¨Ù‡ Ø²Ø¨Ø§Ù† ÙØ§Ø±Ø³ÛŒ Ø±ÙˆØ§Ù† Ùˆ ØªÛŒØªØ±Ø¨Ù†Ø¯ÛŒâ€ŒØ´Ø¯Ù‡ Ø§Ø±Ø§Ø¦Ù‡ Ø¯Ù‡ÛŒØ¯."
            )

        messages = [
            SystemMessage(
                content="Ø´Ù…Ø§ ÛŒÚ© Ù…ØªØ®ØµØµ Ø­Ø±ÙÙ‡â€ŒØ§ÛŒ SEO Ùˆ ØªØ­Ù„ÛŒÙ„Ú¯Ø± Ù…Ø­ØªÙˆØ§ Ù‡Ø³ØªÛŒØ¯. ØªØ­Ù„ÛŒÙ„â€ŒÙ‡Ø§ÛŒ Ø´Ù…Ø§ Ø¨Ø§ÛŒØ¯ Ø¹Ù…ÛŒÙ‚ØŒ Ø¯Ù‚ÛŒÙ‚ØŒ Ú©Ø§Ø±Ø¨Ø±Ø¯ÛŒ Ùˆ Ø¨Ù‡ Ø²Ø¨Ø§Ù† ÙØ§Ø±Ø³ÛŒ Ø¨Ø§Ø´Ø¯."
            ),
            HumanMessage(content=f"{prompt}\n\nÙ…Ø­ØªÙˆØ§:\n{truncated_text}"),
        ]
        response = llm.invoke(messages)
        return response.content
    except Exception as e:
        return f"âŒ Ø®Ø·Ø§ Ø¯Ø± Ø¨Ø±Ù‚Ø±Ø§Ø±ÛŒ Ø§Ø±ØªØ¨Ø§Ø· Ø¨Ø§ Ù…Ø¯Ù„ Â«{model_id}Â»: {str(e)}"






