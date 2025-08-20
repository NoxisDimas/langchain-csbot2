from fastapi import APIRouter, HTTPException, Request
from typing import Any, Dict
import requests
from app.config import get_settings
from app.services.conversation import run_conversation


router = APIRouter()
settings = get_settings()


def _wa_send(to: str, text: str):
	if not (settings.WA_TOKEN and settings.WA_PHONE_ID):
		raise RuntimeError("WhatsApp not configured")
	url = f"https://graph.facebook.com/v19.0/{settings.WA_PHONE_ID}/messages"
	headers = {"Authorization": f"Bearer {settings.WA_TOKEN}", "Content-Type": "application/json"}
	payload = {"messaging_product": "whatsapp", "to": to, "type": "text", "text": {"body": text}}
	requests.post(url, headers=headers, json=payload, timeout=20)


@router.post("/webhook")
async def webhook(request: Request):
	if not (settings.WA_TOKEN and settings.WA_PHONE_ID):
		return {"ok": True, "message": "whatsapp not configured"}
	try:
		update: Dict[str, Any] = await request.json()
		entry = (update.get("entry") or [{}])[0]
		changes = (entry.get("changes") or [{}])[0]
		value = changes.get("value", {})
		messages = value.get("messages", [])
		if not messages:
			return {"ok": True}
		msg = messages[0]
		from_ = msg.get("from")
		text = (msg.get("text") or {}).get("body", "")
		if not (from_ and text):
			return {"ok": True}
		session_id = f"whatsapp:{from_}"
		result = run_conversation(session_id=session_id, message=text, channel="whatsapp", user_meta={"wa_from": from_})
		_wa_send(from_, result.get("assistant_response", ""))
		return {"ok": True}
	except Exception as e:
		raise HTTPException(status_code=500, detail=str(e))