# -*- coding: utf-8 -*-
"""
موتور تحلیل و مدیریت سئوی داخلی سایت.

این ماژول همان منطقی را پیاده می‌کند که افزونه‌های سئوی وردپرس مثل Rank Math
برای هر پست انجام می‌دهند: بررسی طول عنوان و توضیحات متا، حضور کلمه کلیدی
هدف در بخش‌های مهم محتوا، تراکم کلمه کلیدی، طول محتوا و... و در نهایت یک
امتیاز ۰ تا ۱۰۰ و فهرستی از موارد قبول‌شده/رد‌شده تولید می‌کند.
"""

import re
from html import unescape

from extensions import db
from models import SeoSetting

TITLE_MIN = 30
TITLE_MAX = 60
DESCRIPTION_MIN = 70
DESCRIPTION_MAX = 160
CONTENT_MIN_WORDS = 300
KEYWORD_DENSITY_MIN = 0.5
KEYWORD_DENSITY_MAX = 2.5


def get_seo_settings():
    """تنظیمات عمومی سئو را برمی‌گرداند و در صورت نبود، یک رکورد پیش‌فرض می‌سازد."""
    settings = SeoSetting.query.first()
    if settings is None:
        settings = SeoSetting(
            title_separator="—",
            schema_type="Organization",
            sitemap_include_posts=True,
        )
        db.session.add(settings)
        db.session.commit()
    return settings


def update_seo_settings(data):
    settings = get_seo_settings()
    for field, value in data.items():
        setattr(settings, field, value)
    db.session.commit()
    return settings


def _strip_html(text):
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", " ", text)
    return unescape(text)


def _word_count(text):
    words = re.findall(r"[\w\u0600-\u06FF]+", text or "", flags=re.UNICODE)
    return len(words)


def _count_occurrences(haystack, needle):
    if not haystack or not needle:
        return 0
    return haystack.casefold().count(needle.casefold())


def effective_seo_title(post, settings=None):
    """عنوانی که واقعا در تگ <title> و پیش‌نمایش گوگل نمایش داده می‌شود."""
    settings = settings or get_seo_settings()
    base = (post.seo_title or post.title or "").strip()
    if not base:
        return settings.default_meta_title or ""
    site_name = settings.site_name
    if site_name and site_name not in base:
        separator = settings.title_separator or "—"
        return f"{base} {separator} {site_name}"
    return base


def effective_meta_description(post, settings=None):
    settings = settings or get_seo_settings()
    return (
        (post.meta_description or "").strip()
        or (post.excerpt or "").strip()
        or (settings.default_meta_description or "").strip()
    )


def effective_og_image(post, settings=None):
    settings = settings or get_seo_settings()
    return post.og_image_url or post.cover_image_url or settings.default_og_image_url


def analyze_post_seo(post, settings=None):
    """
    تحلیل کامل سئوی یک پست را انجام می‌دهد و دیکشنری زیر را برمی‌گرداند:
    {
        "score": 0-100,
        "status": "good" | "ok" | "bad",
        "checks": [{"key","label","passed","hint"}],
    }
    """
    settings = settings or get_seo_settings()

    keyword = (post.focus_keyword or "").strip()
    seo_title = (post.seo_title or post.title or "").strip()
    meta_description = (post.meta_description or post.excerpt or "").strip()
    plain_content = _strip_html(post.content or "")
    word_count = _word_count(plain_content)

    checks = []

    def add_check(key, label, passed, hint):
        checks.append({"key": key, "label": label, "passed": bool(passed), "hint": hint})

    # 1) وجود کلمه کلیدی هدف
    add_check(
        "keyword_set",
        "کلمه کلیدی هدف مشخص شده است",
        bool(keyword),
        "یک کلمه کلیدی هدف برای این پست انتخاب کنید تا بقیه بررسی‌ها انجام شود."
        if not keyword
        else "کلمه کلیدی هدف تعیین شده است.",
    )

    if keyword:
        # 2) کلمه کلیدی در عنوان سئو
        in_title = keyword.casefold() in seo_title.casefold()
        add_check(
            "keyword_in_title",
            "کلمه کلیدی در عنوان سئو آمده است",
            in_title,
            "کلمه کلیدی هدف را در عنوان سئو بگنجانید، ترجیحاً نزدیک ابتدای عنوان."
            if not in_title
            else "کلمه کلیدی در عنوان دیده می‌شود.",
        )

        # 3) کلمه کلیدی در توضیحات متا
        in_description = keyword.casefold() in meta_description.casefold()
        add_check(
            "keyword_in_description",
            "کلمه کلیدی در توضیحات متا آمده است",
            in_description,
            "کلمه کلیدی را حداقل یک‌بار در توضیحات متا بیاورید."
            if not in_description
            else "کلمه کلیدی در توضیحات متا وجود دارد.",
        )

        # 4) کلمه کلیدی در ۱۰٪ ابتدایی محتوا
        intro_slice = plain_content[: max(150, len(plain_content) // 10)]
        in_intro = keyword.casefold() in intro_slice.casefold()
        add_check(
            "keyword_in_intro",
            "کلمه کلیدی در پاراگراف ابتدایی متن آمده است",
            in_intro,
            "کلمه کلیدی را در همان چند خط اول محتوا نیز بیاورید."
            if not in_intro
            else "کلمه کلیدی در ابتدای محتوا دیده می‌شود.",
        )

        # 5) تراکم کلمه کلیدی
        occurrences = _count_occurrences(plain_content, keyword)
        density = (occurrences / word_count * 100) if word_count else 0
        density_ok = KEYWORD_DENSITY_MIN <= density <= KEYWORD_DENSITY_MAX
        add_check(
            "keyword_density",
            f"تراکم کلمه کلیدی مناسب است ({density:.1f}٪)",
            density_ok,
            "تراکم کلمه کلیدی را بین ۰.۵ تا ۲.۵ درصد نگه دارید (نه خیلی کم، نه تکرار بیش‌ازحد)."
            if not density_ok
            else "تراکم کلمه کلیدی در بازه مناسب است.",
        )

        # 6) کلمه کلیدی در نشانی/عنوان کوتاه (fallback به عنوان اصلی)
        in_excerpt = keyword.casefold() in (post.excerpt or "").casefold()
        add_check(
            "keyword_in_excerpt",
            "کلمه کلیدی در خلاصه پست آمده است",
            in_excerpt,
            "کلمه کلیدی را در خلاصه پست هم بیاورید تا در نتایج جستجو برجسته شود."
            if not in_excerpt
            else "کلمه کلیدی در خلاصه پست دیده می‌شود.",
        )

    # 7) طول عنوان سئو
    title_len = len(seo_title)
    title_ok = TITLE_MIN <= title_len <= TITLE_MAX
    add_check(
        "title_length",
        f"طول عنوان سئو مناسب است ({title_len} کاراکتر)",
        title_ok,
        f"طول عنوان را بین {TITLE_MIN} تا {TITLE_MAX} کاراکتر نگه دارید تا در گوگل کامل نمایش داده شود."
        if not title_ok
        else "طول عنوان مناسب است.",
    )

    # 8) طول توضیحات متا
    desc_len = len(meta_description)
    desc_ok = DESCRIPTION_MIN <= desc_len <= DESCRIPTION_MAX
    add_check(
        "description_length",
        f"طول توضیحات متا مناسب است ({desc_len} کاراکتر)",
        desc_ok,
        f"طول توضیحات متا را بین {DESCRIPTION_MIN} تا {DESCRIPTION_MAX} کاراکتر تنظیم کنید."
        if not desc_ok
        else "طول توضیحات متا مناسب است.",
    )

    # 9) طول محتوا
    content_ok = word_count >= CONTENT_MIN_WORDS
    add_check(
        "content_length",
        f"محتوا طول کافی دارد ({word_count} کلمه)",
        content_ok,
        f"محتوای پست حداقل {CONTENT_MIN_WORDS} کلمه باشد تا شانس رتبه گرفتن بیشتر شود."
        if not content_ok
        else "طول محتوا مناسب است.",
    )

    # 10) وجود تصویر شاخص / OG
    has_image = bool(post.cover_image_url or post.og_image_url)
    add_check(
        "has_image",
        "پست دارای تصویر شاخص است",
        has_image,
        "یک تصویر شاخص برای پست تنظیم کنید تا در شبکه‌های اجتماعی بهتر نمایش داده شود."
        if not has_image
        else "تصویر شاخص تنظیم شده است.",
    )

    # 11) noindex فعال نباشد (اگر قرار است ایندکس شود)
    add_check(
        "indexable",
        "پست برای ایندکس شدن مسدود نشده است",
        not post.meta_robots_noindex,
        "این پست با noindex علامت خورده و در نتایج جستجو ظاهر نمی‌شود."
        if post.meta_robots_noindex
        else "پست قابل ایندکس شدن توسط گوگل است.",
    )

    passed_count = sum(1 for c in checks if c["passed"])
    score = round((passed_count / len(checks)) * 100) if checks else 0

    if score >= 80:
        status = "good"
    elif score >= 50:
        status = "ok"
    else:
        status = "bad"

    return {"score": score, "status": status, "checks": checks, "word_count": word_count}


def sync_post_seo_score(post):
    """امتیاز سئوی پست را محاسبه و روی رکورد ذخیره می‌کند (برای نمایش سریع در لیست‌ها)."""
    result = analyze_post_seo(post)
    post.seo_score = result["score"]
    return result


def site_seo_overview(posts):
    """خلاصه وضعیت سئوی کل سایت برای داشبورد."""
    settings = get_seo_settings()
    analyzed = []
    for post in posts:
        result = analyze_post_seo(post, settings)
        analyzed.append((post, result))

    total = len(analyzed)
    avg_score = round(sum(r["score"] for _, r in analyzed) / total) if total else 0
    good = sum(1 for _, r in analyzed if r["status"] == "good")
    ok = sum(1 for _, r in analyzed if r["status"] == "ok")
    bad = sum(1 for _, r in analyzed if r["status"] == "bad")
    missing_keyword = sum(1 for post, _ in analyzed if not (post.focus_keyword or "").strip())

    return {
        "analyzed": analyzed,
        "avg_score": avg_score,
        "good": good,
        "ok": ok,
        "bad": bad,
        "missing_keyword": missing_keyword,
        "total": total,
    }
