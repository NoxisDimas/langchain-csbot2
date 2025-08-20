from typing import TypedDict, List, Literal, Optional, Dict, Any


class MessageDict(TypedDict):
	type: Literal["human", "ai", "system"]
	content: str


class GraphState(TypedDict, total=False):
	session_id: str
	channel: str
	conversation_history: List[MessageDict]
	user_query: str
	current_task: Optional[str]
	user_profile: Dict[str, Any]
	knowledge_refs: List[Dict[str, Any]]
	sentiment_score: float
	handoff_to_human: bool
	locale: str
	pii_redactions: Dict[str, Any]
	detected_language: str
	order_id: Optional[str]
	assistant_response: str