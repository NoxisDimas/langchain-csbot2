from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any

from app.services.conversation import run_conversation


router = APIRouter()


class ChatRequest(BaseModel):
	session_id: str
	message: str
	channel: str = "web"
	user_meta: Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
	answer: str
	handoff_to_human: bool = False
	current_task: Optional[str] = None
	metadata: Dict[str, Any] = {}


@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
	try:
		result = run_conversation(
			session_id=req.session_id,
			message=req.message,
			channel=req.channel,
			user_meta=req.user_meta or {},
		)
		return ChatResponse(
			answer=result.get("assistant_response", ""),
			handoff_to_human=result.get("handoff_to_human", False),
			current_task=result.get("current_task"),
			metadata={k: v for k, v in result.items() if k not in {"assistant_response", "handoff_to_human", "current_task"}},
		)
	except Exception as e:
		raise HTTPException(status_code=500, detail=str(e))