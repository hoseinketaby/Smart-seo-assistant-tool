from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user

import validators
import requests
from bs4 import BeautifulSoup

from extensions import db
from models import Analysis, APIKey

dashboard_bp = Blueprint("dashboard", __name__)

# ... (TABS and overview route as before) ...

@dashboard_bp.route('/dashboard/fetch', methods=['POST'])
@login_required
def fetch_url():
    data = request.get_json() or {}
    url = (data.get('url') or '').strip()
    if not url or not validators.url(url):
        return jsonify({'error': 'Invalid URL'}), 400

    try:
        headers = {'User-Agent': 'SEO-Assistant/1.0 (+https://example.com)'}
        resp = requests.get(url, headers=headers, timeout=8)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, 'html.parser')
        article = soup.find('article')
        if article:
            texts = [p.get_text(separator=' ', strip=True) for p in article.find_all('p')]
            text = '\n\n'.join([t for t in texts if t])
        else:
            ps = soup.find_all('p')
            texts = [p.get_text(separator=' ', strip=True) for p in ps]
            text = '\n\n'.join([t for t in texts if t])

        max_chars = 20000
        if len(text) > max_chars:
            text = text[:max_chars]

        return jsonify({'text': text})
    except requests.RequestException as e:
        return jsonify({'error': 'Failed to fetch URL', 'details': str(e)}), 500

def send_to_llm(api_key_obj, prompt):
    provider = (api_key_obj.provider or '').lower()
    key = api_key_obj.api_key
    base_url = api_key_obj.base_url or ''

    if provider == 'openai' or not provider:
        url = base_url or 'https://api.openai.com/v1/chat/completions'
        payload = {
            'model': 'gpt-3.5-turbo',
            'messages': [{'role': 'user', 'content': prompt}],
            'max_tokens': 512,
            'temperature': 0.2,
        }
        headers = {'Authorization': f'Bearer {key}', 'Content-Type': 'application/json'}
        try:
            r = requests.post(url, json=payload, headers=headers, timeout=30)
            r.raise_for_status()
            data = r.json()
            text = None
            if 'choices' in data and len(data['choices']) > 0:
                ch = data['choices'][0]
                if 'message' in ch and 'content' in ch['message']:
                    text = ch['message']['content']
                elif 'text' in ch:
                    text = ch['text']
            if text is None:
                return False, 'No text in LLM response'
            return True, text
        except requests.RequestException as e:
            return False, f'LLM request failed: {e}'
    else:
        if not base_url:
            return False, 'No base_url configured for provider'
        headers = {'Authorization': f'Bearer {key}', 'Content-Type': 'application/json'}
        try:
            r = requests.post(base_url, json={'prompt': prompt}, headers=headers, timeout=30)
            r.raise_for_status()
            data = r.json()
            if isinstance(data, dict):
                for k in ('text', 'result', 'output'):
                    if k in data:
                        return True, data[k]
                return True, str(data)
            return True, str(data)
        except requests.RequestException as e:
            return False, f'LLM request failed: {e}'

@dashboard_bp.route('/dashboard/analyze', methods=['POST'])
@login_required
def analyze():
    payload = request.get_json() or {}
    mode = payload.get('mode')
    text = (payload.get('text') or '').strip()
    url = (payload.get('url') or '').strip()

    if mode == 'write' and not text:
        return jsonify({'error': 'No text provided for analysis'}), 400
    if mode == 'url' and not url and not text:
        return jsonify({'error': 'No URL or text provided for analysis'}), 400

    content_text = text
    if not content_text and url:
        try:
            headers = {'User-Agent': 'SEO-Assistant/1.0 (+https://example.com)'}
            resp = requests.get(url, headers=headers, timeout=8)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, 'html.parser')
            article = soup.find('article')
            if article:
                texts = [p.get_text(separator=' ', strip=True) for p in article.find_all('p')]
                content_text = '\n\n'.join([t for t in texts if t])
            else:
                ps = soup.find_all('p')
                texts = [p.get_text(separator=' ', strip=True) for p in ps]
                content_text = '\n\n'.join([t for t in texts if t])
            if len(content_text) > 20000:
                content_text = content_text[:20000]
        except Exception as e:
            return jsonify({'error': 'Failed to fetch URL for analysis', 'details': str(e)}), 400

    api_key_obj = APIKey.query.filter_by(user_id=current_user.id, selected=True).first()
    if not api_key_obj:
        api_key_obj = APIKey.query.filter_by(user_id=current_user.id).first()
    if not api_key_obj:
        return jsonify({'error': 'No API key configured. Please add an API key in API Keys tab.'}), 400

    prompt = (
        "You are an SEO assistant. Analyze the following article content and return a concise JSON with keys: "
        "'score' (0-100 integer), 'summary' (1-3 sentences), 'issues' (array of short strings describing SEO problems), "
        "and 'suggestions' (array of short actionable suggestions).\n\n"
        f"CONTENT:\n{content_text}\n\nRespond only with a JSON object."
    )

    success, llm_result = send_to_llm(api_key_obj, prompt)
    if not success:
        return jsonify({'error': 'LLM request failed', 'details': llm_result}), 500

    analysis = Analysis(user_id=current_user.id, url=url or None, extracted_data={'llm': llm_result})
    db.session.add(analysis)
    db.session.commit()

    return jsonify({'result': llm_result, 'analysis_id': analysis.id})
