from typing import Dict, Any
from app.services.langgraph.graph import get_compiled_graph
from app.services.memory.vector_memory import add_memory, retrieve_memory
from app.persistence.repositories import ConversationRepository
from app.utils.lang import detect_language, translate_to_language
from app.utils.pii import mask_pii
from app.config import get_settings
from app.services.notifications.email_service import send_support_email
from app.services.notifications.telegram_service import notify_support_telegram


settings = get_settings()
_repo = ConversationRepository()
_graph = get_compiled_graph()


def run_conversation(session_id: str, message: str, channel: str, user_meta: Dict[str, Any]) -> Dict[str, Any]:
	# Load history and locale
	conv = _repo.get_or_create_conversation(session_id=session_id, channel=channel, user_meta=user_meta)
	locale = conv.locale or settings.DEFAULT_LOCALE

	# PII masking before persistence and processing
	masked_message, redactions = mask_pii(message)

	_repo.add_message(conversation_id=conv.id, role="user", content=masked_message, pii_redactions=redactions)
	# Persist memory to vectorstore as well
	try:
		add_memory(session_id=session_id, role="user", content=masked_message)
	except Exception:
		pass

	user_lang = detect_language(masked_message) or locale

	graph_input = {
		"session_id": session_id,
		"channel": channel,
		"user_query": masked_message,
		"conversation_history": _repo.get_history_as_messages(conv.id),
		"current_task": None,
		"user_profile": conv.user_profile or {},
		"knowledge_refs": [],
		"sentiment_score": 0.0,
		"handoff_to_human": False,
		"locale": user_lang or settings.DEFAULT_LOCALE,
		"pii_redactions": redactions,
		"detected_language": user_lang,
		"order_id": None,
	}

	# Optionally retrieve recent memory context to enrich graph input
	try:
		mem_docs = retrieve_memory(session_id=session_id, query_text=masked_message, k=4)
		if mem_docs:
			graph_input["conversation_history"] = (
				[{"type": "human" if d.metadata.get("role") == "user" else "ai", "content": d.page_content} for d in mem_docs]
				+ graph_input["conversation_history"]
			)[:20]
	except Exception:
		pass

	final_state = _graph.invoke(graph_input, config={"configurable": {"thread_id": session_id}})

	answer_raw = final_state.get("assistant_response", "")
	answer = translate_to_language(answer_raw, target_lang=user_lang)

	_repo.add_message(conversation_id=conv.id, role="assistant", content=answer, pii_redactions=[])
	try:
		add_memory(session_id=session_id, role="assistant", content=answer)
	except Exception:
		pass

	# Handover notify if needed
	if final_state.get("handoff_to_human"):
		transcript = _repo.get_transcript(conv.id)
		if settings.SMTP_HOST and settings.SUPPORT_EMAIL_TO:
			send_support_email(subject="AI-CS Handover Needed", body=transcript)
		if settings.TELEGRAM_BOT_TOKEN and settings.TELEGRAM_SUPPORT_CHAT_ID:
			notify_support_telegram(text=transcript)

	return {**final_state, "assistant_response": answer}