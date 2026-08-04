import os

from models import Provider, ModelEntry
from crypto_utils import decrypt_value

# ==================== تنظیمات پیش‌فرض DeepSeek ====================
# اگر کاربر هنوز هیچ ارائه‌دهنده/مدلی در بخش «مدیریت API Key» تنظیم
# نکرده باشد، به‌جای نمایش خطا، از کلید پیش‌فرض DeepSeek (که از طریق
# متغیر محیطی تنظیم می‌شود) استفاده می‌شود تا خلاصه‌ساز و تحلیل محتوا
# همیشه آماده‌ی استفاده باشند.
#
# در فایل .env یا در تنظیمات محیط سرور (مثلاً Render) این مقدار را ست کنید:
#   DEEPSEEK_API_KEY=sk-xxxxxxxx
#
# در صورت نیاز می‌توانید base_url و مدل پیش‌فرض را هم override کنید:
#   DEEPSEEK_BASE_URL=https://api.deepseek.com
#   DEEPSEEK_MODEL=deepseek-chat
DEFAULT_DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEFAULT_DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
DEFAULT_DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

NO_MODEL_ERROR = (
    "🔑 هیچ کلید API یا مدلی در بخش «مدیریت API Key» تنظیم نشده است. "
    "لطفاً ابتدا از منوی سمت راست وارد «مدیریت API Key» شوید و کلید و مدل خود را ثبت کنید."
)


def get_active_user_llm_config(user_id: int):
    """
    دریافت تنظیمات LLM فعال کاربر.

    اگر کاربر مدل فعالی تنظیم کرده باشد، همان استفاده می‌شود. در غیر
    این صورت و در صورتی که کلید پیش‌فرض DeepSeek در متغیرهای محیطی
    تنظیم شده باشد، به‌صورت خودکار از DeepSeek به‌عنوان مدل پیش‌فرض
    رایگان استفاده می‌شود تا کاربر نیازی به تنظیم اولیه نداشته باشد.
    """
    active_model = (
        ModelEntry.query.join(Provider)
        .filter(Provider.user_id == user_id, ModelEntry.is_active == True)
        .first()
    )

    if not active_model:
        active_model = (
            ModelEntry.query.join(Provider)
            .filter(Provider.user_id == user_id)
            .first()
        )

    if not active_model or not active_model.provider:
        if DEFAULT_DEEPSEEK_API_KEY:
            return DEFAULT_DEEPSEEK_API_KEY, DEFAULT_DEEPSEEK_BASE_URL, DEFAULT_DEEPSEEK_MODEL, None
        return None, None, None, NO_MODEL_ERROR

    provider = active_model.provider
    api_key = decrypt_value(provider.api_key_encrypted)
    base_url = provider.base_url
    model_id = active_model.model_id

    return api_key, base_url, model_id, None
