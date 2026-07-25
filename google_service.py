import urllib.parse
import urllib.request
import re
import random
import time
from bs4 import BeautifulSoup


# ==================== روش اول: DuckDuckGo (پایدارتر) ====================

def search_duckduckgo(query: str, max_results: int = 10):
    """
    جستجوی مقالات در DuckDuckGo بدون نیاز به API
    DuckDuckGo محدودیت IP ندارد و برای scraping راحت‌تر است
    """
    if not query:
        return get_trending_duckduckgo_articles(max_results)
    
    encoded_query = urllib.parse.quote(query)
    url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "fa-IR,fa;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Connection": "keep-alive",
    }
    
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode("utf-8")
        
        soup = BeautifulSoup(html, 'html.parser')
        results = []
        
        # پیدا کردن نتایج جستجو
        for result in soup.find_all('div', class_='result'):
            title_elem = result.find('a', class_='result__a')
            if not title_elem:
                continue
            
            title = title_elem.get_text(strip=True)
            link = title_elem.get('href', '')
            
            # استخراج لینک واقعی
            if link.startswith('/'):
                link = f"https://duckduckgo.com{link}"
            
            # استخراج توضیحات
            snippet_elem = result.find('a', class_='result__snippet')
            if snippet_elem:
                snippet = snippet_elem.get_text(strip=True)
            else:
                snippet_elem = result.find('div', class_='result__snippet')
                snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""
            
            # استخراج دامنه
            domain_elem = result.find('span', class_='result__domain')
            domain = domain_elem.get_text(strip=True) if domain_elem else ""
            
            if title and link:
                results.append({
                    'title': title,
                    'link': link,
                    'snippet': snippet,
                    'domain': domain,
                    'source': 'DuckDuckGo'
                })
            
            if len(results) >= max_results:
                break
        
        return results
    except Exception as e:
        print(f"Error fetching DuckDuckGo results: {e}")
        return []


def get_trending_duckduckgo_articles(max_results: int = 10):
    """
    دریافت مقالات پرطرفدار از DuckDuckGo
    """
    # لیست کلمات کلیدی پربازدید
    trending_queries = [
        "آخرین اخبار ایران",
        "آموزش برنامه نویسی",
        "سلامت و تغذیه",
        "فناوری اطلاعات",
        "بورس و اقتصاد",
        "فیلم و سریال جدید",
        "ورزش و فوتبال",
        "گردشگری و سفر",
        "مد و فشن",
        "کتاب و مطالعه",
        "هوش مصنوعی",
        "بیت کوین",
        "تست شخصیت",
        "آموزش زبان انگلیسی",
        "دیجیتال مارکتینگ"
    ]
    
    query = random.choice(trending_queries)
    return search_duckduckgo(query, max_results)


# ==================== روش دوم: Google Search (ممکن است محدود شود) ====================

def search_google_html(query: str, max_results: int = 10):
    """
    جستجوی گوگل با استفاده از HTML (روش قدیمی - ممکن است محدود شود)
    """
    if not query:
        return get_google_trending_html(max_results)
    
    encoded_query = urllib.parse.quote(query)
    url = f"https://www.google.com/search?q={encoded_query}&hl=fa"
    
    headers = {
        "User-Agent": random.choice([
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15",
        ]),
        "Accept-Language": "fa-IR,fa;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0",
    }
    
    req = urllib.request.Request(url, headers=headers)
    try:
        # تاخیر برای جلوگیری از تشخیص ربات
        time.sleep(random.uniform(1, 3))
        
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode("utf-8")
        
        soup = BeautifulSoup(html, 'html.parser')
        results = []
        
        # پیدا کردن نتایج جستجو
        for result in soup.find_all('div', class_='g'):
            # استخراج عنوان
            title_elem = result.find('h3')
            if not title_elem:
                continue
            
            # استخراج لینک
            link_elem = result.find('a')
            if not link_elem:
                continue
            
            title = title_elem.get_text(strip=True)
            link = link_elem.get('href', '')
            
            # استخراج لینک واقعی
            if link.startswith('/url?q='):
                link = urllib.parse.unquote(link.split('/url?q=')[1].split('&')[0])
            elif link.startswith('http'):
                pass
            else:
                continue
            
            # استخراج توضیحات
            snippet = ""
            snippet_elem = result.find('div', class_='IsZvec')
            if snippet_elem:
                snippet = snippet_elem.get_text(strip=True)
            else:
                snippet_elem = result.find('div', class_='VwiC3b')
                if snippet_elem:
                    snippet = snippet_elem.get_text(strip=True)
                else:
                    # روش دیگر برای استخراج توضیحات
                    snippet_elem = result.find('div', class_='BNeawe')
                    if snippet_elem:
                        snippet = snippet_elem.get_text(strip=True)
            
            if title and link and link.startswith('http'):
                results.append({
                    'title': title,
                    'link': link,
                    'snippet': snippet,
                    'domain': '',
                    'source': 'Google'
                })
            
            if len(results) >= max_results:
                break
        
        return results
    except Exception as e:
        print(f"Error fetching Google results: {e}")
        return []


def get_google_trending_html(max_results: int = 10):
    """
    دریافت مقالات پرطرفدار از گوگل
    """
    # لیست کلمات کلیدی پربازدید
    trending_topics = [
        "آموزش هوش مصنوعی",
        "برنامه نویسی پایتون",
        "آخرین اخبار سیاسی",
        "سلامت روان",
        "تکنولوژی جدید",
        "بورس و سرمایه‌گذاری",
        "فیلم های جدید",
        "ورزش و تناسب اندام",
        "طراحی وب",
        "یادگیری زبان انگلیسی",
        "آموزش سئو",
        "بازاریابی محتوا",
        "توسعه فردی",
        "کار از راه دور",
        "کسب درآمد اینترنتی"
    ]
    
    query = random.choice(trending_topics)
    return search_google_html(query, max_results)