import os
import requests
from fastapi import APIRouter, HTTPException, Request
from typing import Any, Dict

from app.config import get_settings
from app.services.conversation import run_conversation


router = APIRouter()
settings = get_settings()


def _send_telegram_message(chat_id: str, text: str):
	if not settings.TELEGRAM_BOT_TOKEN:
		raise RuntimeError("TELEGRAM_BOT_TOKEN not configured")
	url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
	payload = {"chat_id": chat_id, "text": text}
	requests.post(url, json=payload, timeout=15)


@router.post("/webhook")
async def telegram_webhook(request: Request):
	try:
		update: Dict[str, Any] = await request.json()
		message = update.get("message") or update.get("edited_message")
		if not message:
			return {"ok": True}

		chat_id = str(message.get("chat", {}).get("id"))
		text = message.get("text", "")
		if not text:
			return {"ok": True}

		# Use telegram:CHATID as session_id
		session_id = f"telegram:{chat_id}"
		result = run_conversation(
			session_id=session_id,
			message=text,
			channel="telegram",
			user_meta={"telegram_chat_id": chat_id},
		)
		answer = result.get("assistant_response", "")
		_send_telegram_message(chat_id, answer)
		return {"ok": True}
	except Exception as e:
		raise HTTPException(status_code=500, detail=str(e))