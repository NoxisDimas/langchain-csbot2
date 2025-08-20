from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import requests
from app.config import get_settings


router = APIRouter()
settings = get_settings()


class TicketRequest(BaseModel):
	title: str
	description: str
	customer_id: str | None = None


@router.post("/ticket")
def create_ticket(req: TicketRequest):
	if not (settings.CRM_BASE_URL and settings.CRM_API_KEY):
		return {"ok": True, "message": "crm not configured"}
	try:
		r = requests.post(
			f"{settings.CRM_BASE_URL.rstrip('/')}/tickets",
			headers={"Authorization": f"Bearer {settings.CRM_API_KEY}", "Content-Type": "application/json"},
			json=req.model_dump(),
			timeout=20,
		)
		r.raise_for_status()
		return {"ok": True, "id": r.json().get("id")}
	except Exception as e:
		raise HTTPException(status_code=500, detail=str(e))