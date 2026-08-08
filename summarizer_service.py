import urllib.request
from bs4 import BeautifulSoup
from extensions import db
from models import Provider, ModelEntry
from crypto_utils import decrypt_value
from llm_config import get_active_user_llm_config


def extract_article_content(url: str) -> str:
    """
    استخراج محتوای مقاله از لینک
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept-Language": "fa-IR,fa;q=0.9,en-US;q=0.8,en;q=0.7",
        }
        
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode("utf-8")
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # حذف تگ‌های غیرضروری
        for tag in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
            tag.decompose()
        
        # استخراج متن اصلی
        paragraphs = soup.find_all('p')
        content = " ".join([p.get_text(strip=True) for p in paragraphs])
        
        # اگر پاراگراف‌ها کم بود، از کل متن استفاده کن
        if len(content) < 100:
            content = soup.get_text(strip=True)
        
        return content
    except Exception as e:
        print(f"Error extracting article content: {e}")
        return None


def summarize_article(url: str, title: str, user) -> str:
    """
    خلاصه‌سازی مقاله با استفاده از LLM تنظیم شده کاربر
    """
    # استخراج محتوای مقاله
    content = extract_article_content(url)
    
    if not content:
        return "❌ متأسفانه امکان استخراج محتوای مقاله وجود نداشت. لطفاً لینک را بررسی کنید."
    
    # دریافت تنظیمات LLM کاربر
    api_key, base_url, model_id, error_msg = get_active_user_llm_config(user.id)
    
    if error_msg:
        return error_msg
    
    # محدود کردن طول متن
    max_chars = 12000
    truncated_text = content[:max_chars]
    
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
        messages = [
            SystemMessage(
                content="شما یک دستیار حرفه‌ای خلاصه‌سازی مقاله هستید. متن مقاله را خوانده و یک خلاصه روان، جذاب، تیتربندی شده و دقیق به زبان فارسی ارائه دهید. نکات کلیدی و اصلی مقاله را استخراج کنید."
            ),
            HumanMessage(content=f"لطفاً مقاله زیر را خلاصه‌سازی کنید:\n\nعنوان: {title}\n\nمتن:\n{truncated_text}"),
        ]
        response = llm.invoke(messages)
        return response.content
    except Exception as e:
        return f"❌ خطا در برقراری ارتباط با مدل «{model_id}»: {str(e)}"
