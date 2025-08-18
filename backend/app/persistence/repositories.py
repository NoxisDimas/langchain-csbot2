from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.persistence.db import get_db
from app.persistence.models import Conversation, Message, SensitiveData, Base
from app.config import get_settings


settings = get_settings()


class ConversationRepository:
	def __init__(self):
		pass

	def get_or_create_conversation(self, session_id: str, channel: str, user_meta: Dict[str, Any]) -> Conversation:
		with next(get_db()) as db:  # type: ignore
			stmt = select(Conversation).where(Conversation.session_id == session_id)
			conv = db.execute(stmt).scalar_one_or_none()
			if conv:
				return conv
			conv = Conversation(session_id=session_id, channel=channel, user_profile=user_meta)
			db.add(conv)
			db.commit()
			db.refresh(conv)
			return conv

	def add_message(self, conversation_id: int, role: str, content: str, pii_redactions: Optional[dict] = None) -> Message:
		with next(get_db()) as db:  # type: ignore
			msg = Message(conversation_id=conversation_id, role=role, content=content, pii_redactions=pii_redactions or {})
			db.add(msg)
			db.commit()
			db.refresh(msg)
			return msg

	def get_history_as_messages(self, conversation_id: int) -> List[Dict[str, Any]]:
		with next(get_db()) as db:  # type: ignore
			stmt = select(Message).where(Message.conversation_id == conversation_id).order_by(Message.id.asc())
			rows = db.execute(stmt).scalars().all()
			return [{"type": "human" if r.role == "user" else "ai", "content": r.content} for r in rows]

	def get_transcript(self, conversation_id: int) -> str:
		with next(get_db()) as db:  # type: ignore
			stmt = select(Message).where(Message.conversation_id == conversation_id).order_by(Message.id.asc())
			rows = db.execute(stmt).scalars().all()
			lines = []
			for r in rows:
				prefix = "User" if r.role == "user" else "Assistant"
				lines.append(f"{prefix}: {r.content}")
			return "\n".join(lines)

	def store_sensitive(self, conversation_id: int, data: Dict[str, Any]) -> SensitiveData:
		with next(get_db()) as db:  # type: ignore
			rec = SensitiveData(conversation_id=conversation_id, data=data, expires_at=SensitiveData.ttl_from_now(settings.SENSITIVE_TTL_HOURS))
			db.add(rec)
			db.commit()
			db.refresh(rec)
			return rec