import json
import os
import re
import urllib.parse
import urllib.request
from youtube_transcript_api import YouTubeTranscriptApi

from extensions import db
from models import Provider, ModelEntry
from crypto_utils import decrypt_value


def search_youtube_videos(query: str, max_results: int = 10):
    if not query:
        query = "آموزش سئو"

    encoded_query = urllib.parse.quote(query)
    url = f"https://www.youtube.com/results?search_query={encoded_query}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept-Language": "fa-IR,fa;q=0.9,en-US;q=0.8,en;q=0.7",
    }

    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode("utf-8")

        match = re.search(r"var ytInitialData = ({.*?});</script>", html)
        if not match:
            match = re.search(r"window\[\"ytInitialData\"\] = ({.*?});", html)

        if not match:
            return []

        data = json.loads(match.group(1))
        videos = []

        contents = (
            data.get("contents", {})
            .get("twoColumnSearchResultsRenderer", {})
            .get("primaryContents", {})
            .get("sectionListRenderer", {})
            .get("contents", [])
        )

        for item in contents:
            item_section = item.get("itemSectionRenderer", {})
            for video in item_section.get("contents", []):
                video_data = video.get("videoRenderer")
                if not video_data:
                    continue

                video_id = video_data.get("videoId")
                title_runs = video_data.get("title", {}).get("runs", [])
                title = title_runs[0].get("text", "") if title_runs else ""

                owner_runs = video_data.get("ownerText", {}).get("runs", [])
                channel_name = owner_runs[0].get("text", "") if owner_runs else "یوتیوب"

                length_text = video_data.get("lengthText", {}).get("simpleText", "نامشخص")
                thumbnails = video_data.get("thumbnail", {}).get("thumbnails", [])
                thumbnail_url = thumbnails[-1]["url"] if thumbnails else f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg"

                if video_id and title:
                    videos.append({
                        "video_id": video_id,
                        "title": title,
                        "channel": channel_name,
                        "duration": length_text,
                        "thumbnail": thumbnail_url,
                        "url": f"https://www.youtube.com/watch?v={video_id}",
                    })

                if len(videos) >= max_results:
                    break

            if len(videos) >= max_results:
                break

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
    """استخراج کلید API، Base URL و مدل فعال شده توسط کاربر"""
    # جستجوی مدلی که is_active == True است
    active_model = (
        ModelEntry.query.join(Provider)
        .filter(Provider.user_id == user_id, ModelEntry.is_active == True)
        .first()
    )

    # اگر مدل فعال مشخصی نداشت، اولین مدل موجود کاربر را بردارد
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

    # استخراج کلید و مدل فعال کاربر از بخش مدیریت API Key
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