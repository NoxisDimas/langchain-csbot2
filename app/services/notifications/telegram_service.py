import requests
from app.config import get_settings


settings = get_settings()


def notify_support_telegram(text: str):
	if not (settings.TELEGRAM_BOT_TOKEN and settings.TELEGRAM_SUPPORT_CHAT_ID):
		return
	url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
	payload = {"chat_id": settings.TELEGRAM_SUPPORT_CHAT_ID, "text": text}
	requests.post(url, json=payload, timeout=15)