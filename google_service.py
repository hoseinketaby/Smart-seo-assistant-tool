import urllib.parse
import urllib.request
import gzip
import zlib
import re
import random
import time
from bs4 import BeautifulSoup


USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
]


def _fetch_html(url, headers=None, timeout=15):
    """
    درخواست HTTP و رمزگشایی صحیح پاسخ.
    نکته‌ی مهم: قبلاً هدر Accept-Encoding شامل gzip/br ارسال می‌شد ولی
    urllib خودش این فشرده‌سازی را باز نمی‌کند، در نتیجه محتوای فشرده
    مستقیم decode('utf-8') می‌شد و خطا می‌داد (و به همین دلیل جستجوی
    گوگل همیشه خروجی خالی برمی‌گرداند). این تابع آن مشکل را برطرف می‌کند.
    """
    req = urllib.request.Request(url, headers=headers or {})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        raw = response.read()
        content_encoding = response.info().get("Content-Encoding", "")

    if content_encoding == "gzip":
        raw = gzip.decompress(raw)
    elif content_encoding == "deflate":
        raw = zlib.decompress(raw)

    return raw.decode("utf-8", errors="ignore")


def _base_headers(extra=None):
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept-Language": "fa-IR,fa;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Connection": "keep-alive",
    }
    if extra:
        headers.update(extra)
    return headers


# ==================== DuckDuckGo ====================

def _parse_duckduckgo_html(html, max_results):
    soup = BeautifulSoup(html, "html.parser")
    results = []

    for result in soup.find_all("div", class_="result"):
        title_elem = result.find("a", class_="result__a")
        if not title_elem:
            continue

        title = title_elem.get_text(strip=True)
        link = title_elem.get("href", "")
        if link.startswith("/"):
            link = f"https://duckduckgo.com{link}"

        snippet_elem = result.find("a", class_="result__snippet") or result.find("div", class_="result__snippet")
        snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""

        domain_elem = result.find("span", class_="result__domain")
        domain = domain_elem.get_text(strip=True) if domain_elem else ""

        if title and link:
            results.append({
                "title": title,
                "link": link,
                "snippet": snippet,
                "domain": domain,
                "source": "DuckDuckGo",
            })

        if len(results) >= max_results:
            break

    return results


def search_duckduckgo(query: str, max_results: int = 10):
    """
    جستجوی مقالات در DuckDuckGo. دو Endpoint امتحان می‌شود تا احتمال
    خروجی خالی به حداقل برسد.
    """
    if not query:
        return get_trending_duckduckgo_articles(max_results)

    encoded_query = urllib.parse.quote(query)
    endpoints = [
        f"https://html.duckduckgo.com/html/?q={encoded_query}",
        f"https://lite.duckduckgo.com/lite/?q={encoded_query}",
    ]

    for url in endpoints:
        try:
            html = _fetch_html(url, headers=_base_headers())
            results = _parse_duckduckgo_html(html, max_results)
            if results:
                return results
        except Exception as e:
            print(f"Error fetching DuckDuckGo results from {url}: {e}")

    return []


def get_trending_duckduckgo_articles(max_results: int = 10):
    return search_duckduckgo(DEFAULT_TRENDING_KEYWORD, max_results)


# ==================== Bing (لایه‌ی جایگزین برای گوگل) ====================

def search_bing_html(query: str, max_results: int = 10):
    encoded_query = urllib.parse.quote(query)
    url = f"https://www.bing.com/search?q={encoded_query}&mkt=fa-IR&setlang=fa"

    try:
        html = _fetch_html(url, headers=_base_headers())
        soup = BeautifulSoup(html, "html.parser")
        results = []

        for li in soup.find_all("li", class_="b_algo"):
            h2 = li.find("h2")
            if not h2 or not h2.find("a"):
                continue

            a_tag = h2.find("a")
            title = a_tag.get_text(strip=True)
            link = a_tag.get("href", "")

            caption = li.find("div", class_="b_caption")
            snippet = ""
            if caption:
                p = caption.find("p")
                snippet = p.get_text(strip=True) if p else caption.get_text(strip=True)

            if title and link.startswith("http"):
                results.append({
                    "title": title,
                    "link": link,
                    "snippet": snippet,
                    "domain": "",
                    "source": "Bing",
                })

            if len(results) >= max_results:
                break

        return results
    except Exception as e:
        print(f"Error fetching Bing results: {e}")
        return []


# ==================== Google ====================

def _parse_google_html(html, max_results):
    soup = BeautifulSoup(html, "html.parser")
    results = []

    for result in soup.find_all("div", class_="g"):
        title_elem = result.find("h3")
        link_elem = result.find("a")
        if not title_elem or not link_elem:
            continue

        title = title_elem.get_text(strip=True)
        link = link_elem.get("href", "")

        if link.startswith("/url?q="):
            link = urllib.parse.unquote(link.split("/url?q=")[1].split("&")[0])
        elif not link.startswith("http"):
            continue

        snippet = ""
        for cls in ("IsZvec", "VwiC3b", "BNeawe"):
            snippet_elem = result.find("div", class_=cls)
            if snippet_elem:
                snippet = snippet_elem.get_text(strip=True)
                break

        if title and link.startswith("http"):
            results.append({
                "title": title,
                "link": link,
                "snippet": snippet,
                "domain": "",
                "source": "Google",
            })

        if len(results) >= max_results:
            break

    return results


def search_google_html(query: str, max_results: int = 10):
    """
    جستجوی گوگل. گوگل معمولاً روی IP سرورهای ابری/میزبانی، اسکرپینگ مستقیم
    را با کپچا یا صفحه‌ی رضایت (consent) مسدود می‌کند و هیچ راهی برای
    تضمین ۱۰۰٪ کارکرد بدون API رسمی گوگل وجود ندارد. برای اینکه تب هرگز
    خالی نماند، این تابع به‌ترتیب گوگل → بینگ → داک‌داک‌گو را امتحان
    می‌کند و اولین نتیجه‌ی غیرخالی را برمی‌گرداند.
    """
    if not query:
        return get_google_trending_html(max_results)

    encoded_query = urllib.parse.quote(query)
    url = f"https://www.google.com/search?q={encoded_query}&hl=fa&num={max_results}"

    headers = _base_headers({
        # این کوکی از ریدایرکت شدن به صفحه‌ی «رضایت با کوکی‌ها»ی گوگل
        # (که پارس نتایج را کامل خراب می‌کرد) جلوگیری می‌کند
        "Cookie": "CONSENT=YES+cb.20210328-17-p0.en+FX+410",
        "Upgrade-Insecure-Requests": "1",
    })

    try:
        time.sleep(random.uniform(0.5, 1.5))
        html = _fetch_html(url, headers=headers)
        results = _parse_google_html(html, max_results)
        if results:
            return results
    except Exception as e:
        print(f"Error fetching Google results: {e}")

    # لایه‌ی جایگزین اول: بینگ
    try:
        results = search_bing_html(query, max_results)
        if results:
            return results
    except Exception as e:
        print(f"Error in Bing fallback: {e}")

    # لایه‌ی جایگزین دوم: داک‌داک‌گو (تا در نهایت چیزی به کاربر نمایش داده شود)
    try:
        results = search_duckduckgo(query, max_results)
        for r in results:
            r["source"] = f"{r.get('source', 'DuckDuckGo')} (جایگزین گوگل)"
        return results
    except Exception as e:
        print(f"Error in DuckDuckGo fallback: {e}")
        return []


# کلمه‌ی کلیدی پیش‌فرضی که قبل از اولین جستجوی کاربر، پشت‌صحنه
# جستجو می‌شود تا تب هیچ‌وقت خالی نباشد. این مقدار هرگز داخل
# فیلد input نمایش داده نمی‌شود چون dashboard.py فقط پارامتر
# واقعی URL (که خالی است) را به تمپلیت پاس می‌دهد، نه این مقدار را.
DEFAULT_TRENDING_KEYWORD = "آموزش سئو"


def get_google_trending_html(max_results: int = 10):
    return search_google_html(DEFAULT_TRENDING_KEYWORD, max_results)
