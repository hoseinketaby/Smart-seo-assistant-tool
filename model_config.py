from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from extensions import db
from models import Provider, ModelEntry
from crypto_utils import encrypt_value

model_config_bp = Blueprint("model_config", __name__, url_prefix="/dashboard/models")

PROVIDER_PRESETS = {
    "deepseek": {
        "label": "دیپ‌سیک (DeepSeek)",
        "base_url": "https://api.deepseek.com",
        "custom_base_url": False,
        "supported": True,
        "model_hint": "شناسه مدل را طبق مستندات DeepSeek وارد کنید، مثلاً deepseek-chat یا deepseek-reasoner",
    },
    "gapgpt": {
        "label": "گپ‌جی‌پی‌تی (GapGPT)",
        "base_url": "https://api.gapgpt.app/v1",
        "custom_base_url": False,
        "supported": True,
        "model_hint": "شناسه مدل را طبق مستندات GapGPT وارد کنید، مثلاً claude-fable-5 یا gpt-4o-mini",
    },
    "avalai": {
        "label": "اول‌ای‌آی (AvalAI)",
        "base_url": "https://api.avalai.ir/v1",
        "custom_base_url": False,
        "supported": True,
        "model_hint": "شناسه مدل‌های پشتیبانی شده AvalAI را وارد کنید.",
    },
    "openrouter": {
        "label": "اوپن‌روتر (OpenRouter)",
        "base_url": "https://openrouter.ai/api/v1",
        "custom_base_url": False,
        "supported": True,
        "model_hint": "شناسه مدل به فرمت provider/model باشد، مثلاً openai/gpt-4o-mini",
    },
}


def _sidebar_context(active_tab="api-keys"):
    from dashboard import TABS, TABS_BY_KEY
    return {
        "tabs": TABS,
        "active_tab": active_tab,
        "active_tab_info": TABS_BY_KEY[active_tab],
        "user": current_user,
    }


@model_config_bp.route("/")
@login_required
def index():
    providers = (
        Provider.query.filter_by(user_id=current_user.id)
        .order_by(Provider.created_at.asc())
        .all()
    )
    return render_template(
        "dashboard/models.html",
        providers=providers,
        presets=PROVIDER_PRESETS,
        **_sidebar_context(),
    )


@model_config_bp.route("/providers/add", methods=["POST"])
@login_required
def add_provider():
    preset_key = (request.form.get("preset_key") or "").strip()
    name = (request.form.get("name") or "").strip()
    api_key = (request.form.get("api_key") or "").strip()
    custom_base_url = (request.form.get("base_url") or "").strip()

    if preset_key not in PROVIDER_PRESETS:
        flash("ارائه‌دهنده نامعتبر است.", "error")
        return redirect(url_for("model_config.index"))

    preset = PROVIDER_PRESETS[preset_key]

    if not name or not api_key:
        flash("نام و API key الزامی است.", "error")
        return redirect(url_for("model_config.index"))

    base_url = custom_base_url if preset.get("custom_base_url") else preset.get("base_url")

    provider = Provider(
        user_id=current_user.id,
        name=name,
        preset_key=preset_key,
        base_url=base_url,
        api_key_encrypted=encrypt_value(api_key),
    )
    db.session.add(provider)
    db.session.commit()
    flash(f"ارائه‌دهنده «{name}» اضافه شد.", "info")
    return redirect(url_for("model_config.index"))


@model_config_bp.route("/providers/<int:provider_id>/delete", methods=["POST"])
@login_required
def delete_provider(provider_id):
    provider = Provider.query.filter_by(id=provider_id, user_id=current_user.id).first()
    if not provider:
        flash("ارائه‌دهنده پیدا نشد.", "error")
        return redirect(url_for("model_config.index"))

    db.session.delete(provider)
    db.session.commit()
    flash("ارائه‌دهنده حذف شد.", "info")
    return redirect(url_for("model_config.index"))


@model_config_bp.route("/providers/<int:provider_id>/models/add", methods=["POST"])
@login_required
def add_model(provider_id):
    provider = Provider.query.filter_by(id=provider_id, user_id=current_user.id).first()
    if not provider:
        flash("ارائه‌دهنده پیدا نشد.", "error")
        return redirect(url_for("model_config.index"))

    model_id = (request.form.get("model_id") or "").strip()
    display_name = (request.form.get("display_name") or "").strip() or model_id

    if not model_id:
        flash("شناسه مدل الزامی است.", "error")
        return redirect(url_for("model_config.index"))

    # اگر این اولین مدل کاربر است، به‌صورت خودکار فعال شود
    user_models_count = ModelEntry.query.join(Provider).filter(Provider.user_id == current_user.id).count()
    is_active = (user_models_count == 0)

    entry = ModelEntry(provider_id=provider.id, model_id=model_id, display_name=display_name, is_active=is_active)
    db.session.add(entry)
    db.session.commit()
    flash(f"مدل «{display_name}» اضافه شد.", "info")
    return redirect(url_for("model_config.index"))


@model_config_bp.route("/models/<int:model_id>/activate", methods=["POST"])
@login_required
def activate_model(model_id):
    """تنظیم یک مدل به عنوان مدل فعال هوش مصنوعی کاربر"""
    user_models = ModelEntry.query.join(Provider).filter(Provider.user_id == current_user.id).all()
    activated_name = None

    for model in user_models:
        if model.id == model_id:
            model.is_active = True
            activated_name = model.display_name
        else:
            model.is_active = False

    if not activated_name:
        flash("مدل پیدا نشد.", "error")
        return redirect(url_for("model_config.index"))

    db.session.commit()
    flash(f"مدل «{activated_name}» به‌عنوان مدل فعال خلاصه‌ساز تنظیم شد.", "info")
    return redirect(url_for("model_config.index"))


@model_config_bp.route("/models/<int:model_id>/delete", methods=["POST"])
@login_required
def delete_model(model_id):
    entry = (
        ModelEntry.query.join(Provider)
        .filter(ModelEntry.id == model_id, Provider.user_id == current_user.id)
        .first()
    )
    if not entry:
        flash("مدل پیدا نشد.", "error")
        return redirect(url_for("model_config.index"))

    db.session.delete(entry)
    db.session.commit()
    flash("مدل حذف شد.", "info")
    return redirect(url_for("model_config.index"))
