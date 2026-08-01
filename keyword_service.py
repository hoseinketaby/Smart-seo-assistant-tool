import os
import json
import urllib.request
import urllib.parse
import urllib.error

from llm_config import get_active_user_llm_config

# ==================== Mangools (KWFinder) — داده‌های واقعی کلمات کلیدی ====================
# ثبت‌نام رایگان و بدون نیاز به کارت بانکی در mangools.com و دریافت کلید
# API از mangools.com/api-token. سپس مقدار زیر را در متغیرهای محیطی ست کنید:
#   MANGOOLS_API_KEY=xxxxxxxx
MANGOOLS_API_KEY = os.getenv("MANGOOLS_API_KEY", "")
MANGOOLS_BASE_URL = "https://api.mangools.com/v3"

NO_KEYWORD_API_KEY_ERROR = (
    "🔑 کلید API ابزار جستجوی کلمات کلیدی تنظیم نشده است. یک حساب رایگان "
    "(بدون نیاز به کارت بانکی) در mangools.com بسازید، کلید API خود را از "
    "صفحه mangools.com/api-token بردارید و آن را در متغیر محیطی "
    "MANGOOLS_API_KEY قرار دهید."
)


def _mangools_get(path: str, params: dict):
    query = urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})
    url = f"{MANGOOLS_BASE_URL}{path}?{query}"
    req = urllib.request.Request(url, headers={"x-access-token": MANGOOLS_API_KEY})
    with urllib.request.urlopen(req, timeout=15) as response:
        return json.loads(response.read().decode("utf-8"))


def get_related_keywords(keyword: str, location_id: int = 0, language_id: int = 0, max_results: int = 30):
    """
    دریافت کلمات کلیدی مرتبط به‌همراه میزان جستجوی ماهانه، CPC، رقابت
    تبلیغاتی (PPC) و میزان سختی کلمه کلیدی (در صورت کش شدن) از Mangools.

    خروجی: (لیست کلمات کلیدی یا None, پیام خطا یا None)
    """
    keyword = (keyword or "").strip()
    if not keyword:
        return [], None

    if not MANGOOLS_API_KEY:
        return None, NO_KEYWORD_API_KEY_ERROR

    try:
        data = _mangools_get("/kwfinder/related-keywords", {
            "kw": keyword,
            "location_id": location_id,
            "language_id": language_id,
        })
    except urllib.error.HTTPError as e:
        if e.code == 401:
            return None, "🔑 کلید API کلمات کلیدی نامعتبر است. لطفاً مقدار MANGOOLS_API_KEY را بررسی کنید."
        if e.code == 429:
            return None, "⏳ سقف رایگان جستجوی کلمات کلیدی برای امروز به پایان رسیده است. فردا دوباره امتحان کنید."
        return None, f"❌ خطا در دریافت اطلاعات از سرویس کلمات کلیدی (کد {e.code})."
    except Exception as e:
        return None, f"❌ خطا در ارتباط با سرویس کلمات کلیدی: {str(e)}"

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
