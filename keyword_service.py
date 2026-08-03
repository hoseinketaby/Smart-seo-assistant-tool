import os
import json
import urllib.request
import urllib.parse
import urllib.error

from models import KeywordProvider
from crypto_utils import decrypt_value
from llm_config import get_active_user_llm_config

# ==================== ابزارهای جستجوی کلمات کلیدی پشتیبانی‌شده ====================
# هر کاربر می‌تواند از بخش «مدیریت API Key» یکی از این ابزارها را انتخاب کرده و
# کلید API خودش را ثبت کند. اطلاعات ثبت‌نام و مستندات هرکدام:
KEYWORD_PROVIDER_PRESETS = {
    "mangools": {
        "label": "Mangools (KWFinder)",
        "free": True,
        "signup_url": "https://mangools.com/users/sign_up",
        "key_url": "https://mangools.com/api-token",
        "docs_url": "https://apidocs.mangools.com/",
        "hint": "ثبت‌نام رایگان و بدون نیاز به کارت بانکی. بعد از ثبت‌نام، کلید API را از صفحه‌ی api-token بردارید.",
    },
    "keywordseverywhere": {
        "label": "Keywords Everywhere",
        "free": True,
        "signup_url": "https://keywordseverywhere.com/first-install-addon.html",
        "key_url": "https://keywordseverywhere.com/first-install-addon.html",
        "docs_url": "https://api.keywordseverywhere.com/docs/#/",
        "hint": "گرفتن کلید API رایگان است؛ برای دریافت داده به اعتبار (credit) نیاز دارید. کلمات مرتبط نیازمند پلن Gold/Platinum است.",
    },
}

# متغیر محیطی پیش‌فرض (سازگاری با نسخه‌ی قبلی) — اگر کاربر خودش ابزاری تنظیم
# نکرده باشد و این مقدار ست شده باشد، از آن به‌عنوان پیش‌فرض Mangools استفاده می‌شود.
DEFAULT_MANGOOLS_API_KEY = os.getenv("MANGOOLS_API_KEY", "")

MANGOOLS_BASE_URL = "https://api.mangools.com/v3"
KEYWORDSEVERYWHERE_BASE_URL = "https://api.keywordseverywhere.com/v1"

NO_KEYWORD_API_KEY_ERROR = (
    "🔑 هیچ ابزار جستجوی کلمات کلیدی تنظیم نشده است. لطفاً از بخش «مدیریت API Key» "
    "یکی از ابزارهای پشتیبانی‌شده (مثل Mangools) را انتخاب کرده و کلید API رایگان "
    "خود را ثبت کنید."
)


def get_active_keyword_provider(user_id: int):
    provider = (
        KeywordProvider.query
        .filter_by(user_id=user_id, is_active=True)
        .first()
    )
    if not provider:
        provider = KeywordProvider.query.filter_by(user_id=user_id).first()
    return provider


def get_related_keywords(user_id: int, keyword: str, location_id: int = 0, language_id: int = 0, max_results: int = 30):
    """
    دریافت کلمات کلیدی مرتبط از ابزار فعال کاربر (یا کلید پیش‌فرض Mangools در
    صورت وجود). خروجی: (لیست کلمات کلیدی یا None, پیام خطا یا None)
    """
    keyword = (keyword or "").strip()
    if not keyword:
        return [], None

    provider = get_active_keyword_provider(user_id)

    if provider:
        preset_key = provider.preset_key
        api_key = decrypt_value(provider.api_key_encrypted)
    elif DEFAULT_MANGOOLS_API_KEY:
        preset_key = "mangools"
        api_key = DEFAULT_MANGOOLS_API_KEY
    else:
        return None, NO_KEYWORD_API_KEY_ERROR

    if preset_key == "mangools":
        return _mangools_related_keywords(api_key, keyword, location_id, language_id, max_results)
    elif preset_key == "keywordseverywhere":
        return _keywordseverywhere_related_keywords(api_key, keyword, max_results)

    return None, "ابزار کلمات کلیدی انتخاب‌شده پشتیبانی نمی‌شود."


# ==================== Mangools (KWFinder) ====================

def _mangools_related_keywords(api_key: str, keyword: str, location_id: int, language_id: int, max_results: int):
    query = urllib.parse.urlencode({
        "kw": keyword,
        "location_id": location_id,
        "language_id": language_id,
    })
    url = f"{MANGOOLS_BASE_URL}/kwfinder/related-keywords?{query}"
    req = urllib.request.Request(url, headers={"x-access-token": api_key})

    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        if e.code == 401:
            return None, "🔑 کلید API Mangools نامعتبر است. آن را از بخش «مدیریت API Key» بررسی کنید."
        if e.code == 429:
            return None, "⏳ سقف رایگان جستجوی کلمات کلیدی Mangools برای امروز به پایان رسیده است."
        return None, f"❌ خطا در دریافت اطلاعات از Mangools (کد {e.code})."
    except Exception as e:
        return None, f"❌ خطا در ارتباط با Mangools: {str(e)}"

    raw_keywords = (data or {}).get("keywords", [])[:max_results]

    results = []
    for kw in raw_keywords:
        results.append({
            "keyword": kw.get("kw", ""),
            "search_volume": kw.get("sv"),
            "cpc": kw.get("cpc"),
            "ppc": kw.get("ppc"),
            "difficulty": kw.get("seo"),
        })

    return results, None


# ==================== Keywords Everywhere ====================

def _keywordseverywhere_related_keywords(api_key: str, keyword: str, max_results: int):
    url = f"{KEYWORDSEVERYWHERE_BASE_URL}/get_related_keywords"
    body = urllib.parse.urlencode({
        "country": "us",
        "currency": "USD",
        "dataSource": "gkp",
        "kw[]": keyword,
    }).encode()
    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            result = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        error_body = ""
        try:
            error_body = e.read().decode("utf-8", errors="ignore")
        except Exception:
            pass
        if e.code == 401:
            return None, "🔑 کلید API Keywords Everywhere نامعتبر است. آن را از بخش «مدیریت API Key» بررسی کنید."
        if e.code in (402, 403) or "credit" in error_body.lower() or "plan" in error_body.lower():
            return None, "⏳ اعتبار (credit) حساب Keywords Everywhere کافی نیست یا این قابلیت نیازمند پلن بالاتری است."
        return None, f"❌ خطا در دریافت اطلاعات از Keywords Everywhere (کد {e.code})."
    except Exception as e:
        return None, f"❌ خطا در ارتباط با Keywords Everywhere: {str(e)}"

    raw_keywords = (result or {}).get("data", [])[:max_results]

    results = []
    for kw in raw_keywords:
        cpc = kw.get("cpc") or {}
        results.append({
            "keyword": kw.get("keyword", ""),
            "search_volume": kw.get("vol"),
            "cpc": cpc.get("value"),
            "ppc": kw.get("competition"),
            "difficulty": None,  # Keywords Everywhere امتیاز KD کش‌شده ارائه نمی‌دهد
        })

    return results, None


# ==================== جستجوی کلمات کلیدی با هوش مصنوعی ====================

def ai_keyword_research(keyword: str, user) -> str:
    """
    تحلیل و برآورد کلمه کلیدی با استفاده از مدل هوش مصنوعی تنظیم‌شده کاربر
    (یا DeepSeek پیش‌فرض). چون این روش به دیتابیس واقعی گوگل متصل نیست،
    خروجی شامل برآوردهای هوشمند به‌جای اعداد دقیق است.
    """
    keyword = (keyword or "").strip()
    if not keyword:
        return "❌ لطفاً یک کلمه کلیدی وارد کنید."

    api_key, base_url, model_id, error_msg = get_active_user_llm_config(user.id)
    if error_msg:
        return error_msg

    try:
        from langchain_openai import ChatOpenAI
        from langchain_core.messages import SystemMessage, HumanMessage

        kwargs = {
            "api_key": api_key,
            "model": model_id,
            "temperature": 0.4,
        }
        if base_url:
            kwargs["base_url"] = base_url

        llm = ChatOpenAI(**kwargs)
        messages = [
            SystemMessage(
                content=(
                    "شما یک متخصص حرفه‌ای تحقیق کلمات کلیدی (Keyword Research) و سئو هستید. "
                    "شما به دیتابیس زنده گوگل یا ابزارهای سئو دسترسی ندارید، بنابراین باید بر "
                    "اساس دانش و تجربه‌ی خود برآوردهای منطقی و کاربردی ارائه دهید، و همیشه به "
                    "کاربر یادآوری کنید که این مقادیر تخمینی هستند نه داده‌ی دقیق گوگل."
                )
            ),
            HumanMessage(
                content=(
                    f"کلمه کلیدی: «{keyword}»\n\n"
                    "لطفاً تحلیل زیر را دقیقاً با همین ساختار تیتربندی و به زبان فارسی ارائه بده:\n\n"
                    "# کلمات کلیدی مرتبط\n"
                    "حداقل ۱۰ کلمه کلیدی مرتبط و long-tail را به‌صورت لیست بنویس.\n\n"
                    "# برآورد حجم جستجو\n"
                    "سطح تخمینی (خیلی کم / کم / متوسط / زیاد / خیلی زیاد) به‌همراه یک توضیح کوتاه.\n\n"
                    "# برآورد سختی رقابت (Keyword Difficulty)\n"
                    "یک عدد تخمینی از ۱ تا ۱۰۰ به‌همراه یک توضیح کوتاه از میزان رقابت.\n\n"
                    "# نیت جستجو (Search Intent)\n"
                    "مشخص کن که این کلمه کلیدی بیشتر اطلاعاتی، تجاری، تراکنشی یا ناوبری است.\n\n"
                    "# پیشنهاد نوع محتوا\n"
                    "چه نوع محتوایی (مقاله، ویدیو، صفحه محصول و ...) برای رتبه گرفتن مناسب است.\n\n"
                    "# سوالات پرتکرار مرتبط\n"
                    "۵ سوالی که کاربران معمولاً درباره‌ی این موضوع جستجو می‌کنند."
                )
            ),
        ]
        response = llm.invoke(messages)
        return response.content
    except Exception as e:
        return f"❌ خطا در برقراری ارتباط با مدل «{model_id}»: {str(e)}"
