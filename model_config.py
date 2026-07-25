from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from extensions import db
from models import Provider, ModelEntry
from crypto_utils import encrypt_value

model_config_bp = Blueprint("model_config", __name__, url_prefix="/dashboard/models")

# Known providers. 'base_url' is None for providers not yet confirmed or
# not compatible with the simple api_key+base_url pattern - see 'supported'
# and 'warning' for those.
PROVIDER_PRESETS = {
    "gapgpt": {
        "label": "گپ‌جی‌پی‌تی (GapGPT)",
        "base_url": "https://api.gapgpt.app/v1",
        "custom_base_url": False,
        "supported": True,
        "model_hint": "شناسه مدل را طبق مستندات GapGPT وارد کنید، مثلاً claude-fable-5",
    },
    "avalai": {
        "label": "اول‌ای‌آی (AvalAI)",
        "base_url": "",  # intentionally empty per request - to be filled in later
        "custom_base_url": False,
        "supported": True,
        "model_hint": "base_url هنوز نهایی نشده؛ فعلاً خالی ذخیره می‌شود تا بعداً تکمیل شود.",
    },
    "openrouter": {
        "label": "اوپن‌روتر (OpenRouter)",
        "base_url": "https://openrouter.ai/api/v1",
        "custom_base_url": False,
        "supported": True,
        "model_hint": "شناسه مدل باید به فرمت provider/model باشد، مثلاً openai/gpt-4o یا anthropic/claude-sonnet-4",
    },
    "crewai": {
        "label": "CrewAI",
        "base_url": None,
        "custom_base_url": False,
        "supported": False,
        "warning": "CrewAI یک فریم‌ورک اجرای Agent است، نه یک ارائه‌دهنده API با base_url مستقل - "
                   "خودش از طریق ارائه‌دهنده‌های دیگر (OpenAI, Anthropic, ...) کار می‌کند. "
                   "افزودن آن با این فرم در حال حاضر پشتیبانی نمی‌شود.",
    },
    "aws": {
        "label": "AWS (Bedrock)",
        "base_url": None,
        "custom_base_url": False,
        "supported": False,
        "warning": "AWS Bedrock به‌جای یک API key ساده از access_key_id + secret_access_key + region "
                   "استفاده می‌کند و با این فرم سازگار نیست. نیاز به پیاده‌سازی جداگانه دارد.",
    },
}


def _sidebar_context(active_tab="api-keys"):
    """Shared context so this blueprint's pages render inside the same
    dashboard shell (sidebar/tabs) as dashboard.py's tabs."""
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

    if not preset.get("supported", True):
        flash(preset["warning"], "error")
        return redirect(url_for("model_config.index"))

    if not name or not api_key:
        flash("نام و API key الزامی است.", "error")
        return redirect(url_for("model_config.index"))

    if preset["custom_base_url"]:
        if not custom_base_url:
            flash("برای ارائه‌دهنده سفارشی، وارد کردن base URL الزامی است.", "error")
            return redirect(url_for("model_config.index"))
        base_url = custom_base_url
    else:
        base_url = preset["base_url"]

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

    entry = ModelEntry(provider_id=provider.id, model_id=model_id, display_name=display_name)
    db.session.add(entry)
    db.session.commit()
    flash(f"مدل «{display_name}» به «{provider.name}» اضافه شد.", "info")
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
