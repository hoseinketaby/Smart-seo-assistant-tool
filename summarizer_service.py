import http.client
import ipaddress
import socket
import ssl
from urllib.parse import urljoin, urlsplit
from bs4 import BeautifulSoup
from extensions import db
from models import Provider, ModelEntry
from crypto_utils import decrypt_value
from llm_config import get_active_user_llm_config


MAX_ARTICLE_BYTES = 1024 * 1024


def _public_address(hostname, port):
    if not hostname or "." not in hostname:
        raise ValueError("Invalid article host")
    addresses = socket.getaddrinfo(hostname, port, type=socket.SOCK_STREAM)
    if not addresses or any(not ipaddress.ip_address(info[4][0]).is_global for info in addresses):
        raise ValueError("Article host must resolve only to public addresses")
    return addresses[0][4][0]


def _fetch_public_html(url):
    for _ in range(4):
        target = urlsplit(url)
        if target.scheme not in {"http", "https"} or not target.hostname or target.username or target.password:
            raise ValueError("Invalid article URL")
        port = target.port or (443 if target.scheme == "https" else 80)
        if port not in {80, 443}:
            raise ValueError("Article URL has an unsupported port")
        address = _public_address(target.hostname, port)
        hostname = target.hostname

        if target.scheme == "https":
            class PinnedHTTPSConnection(http.client.HTTPSConnection):
                def connect(self):
                    raw_socket = socket.create_connection((address, port), timeout=10)
                    try:
                        self.sock = self._context.wrap_socket(raw_socket, server_hostname=hostname)
                    except Exception:
                        raw_socket.close()
                        raise

            connection = PinnedHTTPSConnection(hostname, port, timeout=10, context=ssl.create_default_context())
        else:
            class PinnedHTTPConnection(http.client.HTTPConnection):
                def connect(self):
                    self.sock = socket.create_connection((address, port), timeout=10)

            connection = PinnedHTTPConnection(hostname, port, timeout=10)

        try:
            path = (target.path or "/") + ("?" + target.query if target.query else "")
            connection.request("GET", path, headers={
                "Host": target.netloc,
                "User-Agent": "Mozilla/5.0 (compatible; ArticleReader/1.0)",
                "Accept": "text/html",
                "Accept-Encoding": "identity",
            })
            response = connection.getresponse()
            if response.status in {301, 302, 303, 307, 308}:
                location = response.getheader("Location")
                if not location:
                    return None
                url = urljoin(url, location)
                continue
            if response.status != 200 or "html" not in response.getheader("Content-Type", "text/html").lower():
                return None
            html = response.read(MAX_ARTICLE_BYTES + 1)
            if len(html) > MAX_ARTICLE_BYTES:
                return None
            return html.decode("utf-8", errors="replace")
        finally:
            connection.close()
    return None


def extract_article_content(url: str) -> str:
    """
    استخراج محتوای مقاله از لینک
    """
    try:
        html = _fetch_public_html(url)
        if not html:
            return None
        
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
    except Exception:
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
        return f"❌ خطا در برقراری ارتباط با مدل «{model_id}»: خطا ثبت شد؛ لطفاً دوباره تلاش کنید"
