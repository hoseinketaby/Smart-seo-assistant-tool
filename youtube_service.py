import json
import gzip
import zlib
import re
import urllib.parse
import urllib.request
from youtube_transcript_api import YouTubeTranscriptApi

from extensions import db
from models import Provider, ModelEntry
from crypto_utils import decrypt_value


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "fa-IR,fa;q=0.9,en-US;q=0.8,en;q=0.7",
}


def _fetch_html(url, headers=None, timeout=15):
    req = urllib.request.Request(url, headers=headers or HEADERS)
    with urllib.request.urlopen(req, timeout=timeout) as response:
        raw = response.read()
        content_encoding = response.info().get("Content-Encoding", "")

    if content_encoding == "gzip":
        raw = gzip.decompress(raw)
    elif content_encoding == "deflate":
        raw = zlib.decompress(raw)

    return raw.decode("utf-8", errors="ignore")


def _extract_json_after_marker(html, marker):
    """
    به‌جای regex حریصانه‌ی قبلی (که با JSON تودرتو غلط پارس می‌شد و
    خاموشانه لیست خالی برمی‌گرداند)، از JSONDecoder.raw_decode استفاده
    می‌کند که مرزهای { } را واقعاً دنبال می‌کند.
    """
    idx = html.find(marker)
    if idx == -1:
        return None

    start = idx + len(marker)
    decoder = json.JSONDecoder()
    try:
        obj, _ = decoder.raw_decode(html, start)
        return obj
    except Exception:
        return None


def _get_yt_initial_data(html):
    for marker in ('var ytInitialData = ', 'window["ytInitialData"] = ', "ytInitialData = "):
        data = _extract_json_after_marker(html, marker)
        if data:
            return data
    return None


def _video_from_renderer(video):
    video_id = video.get("videoId")
    title_runs = video.get("title", {}).get("runs", [])
    title = title_runs[0].get("text", "") if title_runs else video.get("title", {}).get("simpleText", "")

    owner_runs = video.get("ownerText", {}).get("runs", [])
    channel_name = owner_runs[0].get("text", "") if owner_runs else "یوتیوب"

    length_text = video.get("lengthText", {}).get("simpleText", "نامشخص")
    thumbnails = video.get("thumbnail", {}).get("thumbnails", [])
    thumbnail_url = thumbnails[-1]["url"] if thumbnails else (
        f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg" if video_id else ""
    )
    views_text = video.get("viewCountText", {}).get("simpleText", "")

    if not (video_id and title):
        return None

    return {
        "video_id": video_id,
        "title": title,
        "channel": channel_name,
        "duration": length_text,
        "thumbnail": thumbnail_url,
        "url": f"https://www.youtube.com/watch?v={video_id}",
        "views": views_text,
    }


def _walk_video_renderers(node, out, max_results):
    """
    عبور بازگشتی از کل درخت JSON و جمع‌آوری هر videoRenderer که پیدا
    می‌شود؛ این کار مستقل از تغییر مسیر دقیق کلیدهای تودرتوی یوتیوب
    (که مدام تغییر می‌کند) است، برخلاف مسیر ثابت قبلی.
    """
    if len(out) >= max_results:
        return
    if isinstance(node, dict):
        if "videoRenderer" in node:
            parsed = _video_from_renderer(node["videoRenderer"])
            if parsed and not any(v["video_id"] == parsed["video_id"] for v in out):
                out.append(parsed)
        for value in node.values():
            if len(out) >= max_results:
                return
            _walk_video_renderers(value, out, max_results)
    elif isinstance(node, list):
        for item in node:
            if len(out) >= max_results:
                return
            _walk_video_renderers(item, out, max_results)


def _fallback_regex_extract(html, max_results):
    """آخرین لایه‌ی جایگزین وقتی حتی پارس JSON هم شکست بخورد."""
    video_ids = re.findall(r'"videoId":"([a-zA-Z0-9_-]{11})"', html)
    seen = set()
    videos = []
    for vid in video_ids:
        if vid in seen:
            continue
        seen.add(vid)
        videos.append({
            "video_id": vid,
            "title": "",
            "channel": "یوتیوب",
            "duration": "نامشخص",
            "thumbnail": f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg",
            "url": f"https://www.youtube.com/watch?v={vid}",
            "views": "",
        })
        if len(videos) >= max_results:
            break
    return videos


def get_trending_youtube_videos(max_results: int = 10):
    """دریافت ویدیوهای پرطرفدار یوتیوب بدون نیاز به API key"""
    url = "https://www.youtube.com/feed/trending?gl=IR&hl=fa"
    try:
        html = _fetch_html(url)
        data = _get_yt_initial_data(html)

        videos = []
        if data:
            _walk_video_renderers(data, videos, max_results)

        if not videos:
            videos = _fallback_regex_extract(html, max_results)

        return videos
    except Exception as e:
        print(f"Error fetching trending videos: {e}")
        return []


def search_youtube_videos(query: str, max_results: int = 10):
    if not query:
        return get_trending_youtube_videos(max_results)

    encoded_query = urllib.parse.quote(query)
    url = f"https://www.youtube.com/results?search_query={encoded_query}&hl=fa"

    try:
        html = _fetch_html(url)
        data = _get_yt_initial_data(html)

        videos = []
        if data:
            _walk_video_renderers(data, videos, max_results)

        if not videos:
            videos = _fallback_regex_extract(html, max_results)

        return videos
    except Exception as e:
        print(f"Error fetching Youtube videos: {e}")
        return []


def get_youtube_transcript(video_id: str) -> str:
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=["fa", "en"])
        return " ".join([item["text"] for item in transcript_list])
    except Exception:
        try:
            transcripts = YouTubeTranscriptApi.list_transcripts(video_id)
            for t in transcripts:
                transcript_data = t.fetch()
                return " ".join([item["text"] for item in transcript_data])
        except Exception:
            return None


def get_active_user_llm_config(user_id: int):
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
        return None, None, None, "🔑 هیچ کلید API یا مدلی در بخش «مدیریت API Key» تنظیم نشده است. لطفاً ابتدا از منوی سمت راست وارد «مدیریت API Key» شوید و کلید و مدل خود را ثبت کنید."

    provider = active_model.provider
    api_key = decrypt_value(provider.api_key_encrypted)
    base_url = provider.base_url
    model_id = active_model.model_id

    return api_key, base_url, model_id, None


def summarize_youtube_video_text(video_id: str, user) -> str:
    transcript_text = get_youtube_transcript(video_id)

    if not transcript_text:
        return "❌ متأسفانه زیرنویس یا متن پیاده‌شده‌ای برای این ویدیو پیدا نشد یا توسط سازنده غیرفعال شده است."

    api_key, base_url, model_id, error_msg = get_active_user_llm_config(user.id)

    if error_msg:
        return error_msg

    max_chars = 12000
    truncated_text = transcript_text[:max_chars]

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
                content="شما یک دستیار حرفه‌ای خلاصه‌سازی ویدیو هستید. متن زیرنویس ویدیو را خوانده و یک خلاصه روان، جذاب، تیتربندی شده و دقیق به زبان فارسی ارائه دهید."
            ),
            HumanMessage(content=f"لطفاً ویدیو زیر را خلاصه‌سازی کنید:\n\n{truncated_text}"),
        ]
        response = llm.invoke(messages)
        return response.content
    except Exception as e:
        return f"❌ خطا در برقراری ارتباط با مدل «{model_id}»: {str(e)}"
