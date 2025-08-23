from typing import Dict, Any, List, Optional
from langchain_core.tools import tool
from app.services.ecommerce.registry import get_active_ecommerce
from app.services.rag.retriever import retrieve_knowledge
from app.utils.sentiment import compute_sentiment
from app.utils.lang import detect_language, translate_text
from app.services.notifications.email_service import send_support_email
from app.services.notifications.telegram_service import notify_support_telegram
from app.services.memory.vector_memory import add_memory, retrieve_memory


ecom = get_active_ecommerce()


@tool("analyze_sentiment", return_direct=False)
def analyze_sentiment_tool(text: str) -> str:
	"""Analyze sentiment of text and return a compound score in [-1,1]."""
	s = compute_sentiment(text)
	return str(s)


@tool("extract_order_id", return_direct=False)
def extract_order_id_tool(text: str) -> str:
	"""Extract an order id (5+ digits) from text. Return empty string if none found."""
	import re
	m = re.search(r"[#:]?(\d{5,})", text)
	return m.group(1) if m else ""


@tool("get_order_status", return_direct=False)
def get_order_status_tool(order_id: str) -> Dict[str, Any]:
	"""Get order status for a given order_id from active ecommerce provider."""
	if not order_id:
		return {"error": "missing_order_id"}
	return ecom.get_order_status(order_id)


@tool("search_products", return_direct=False)
def search_products_tool(query: str) -> Dict[str, Any]:
	"""
	Search products in catalog by a free-text query from active ecommerce provider.
	
	args:
	query : query to search product
	"""
	items = ecom.search_products(query)
	return {"items": items}


@tool("retrieve_kb_snippets", return_direct=False)
def retrieve_kb_snippets_tool(query: str, collection_name: Optional[str] = None) -> Dict[str, Any]:
	"""
    Retrieve the top knowledge base snippets based on a given query.

    This function processes a user query, translates it into English (if necessary), 
    and retrieves the top relevant snippets from a knowledge base. The results are 
    returned as a list of strings, with a maximum of five snippets per query.

    Args:
    query (str): A string containing the user's search query or question. 
    The query may be automatically translated to English before processing 
    if required.
    collection_name (str, optional): The collection name to search in. 
    If not provided, uses the default DB_SCHEMA.

    Returns:
    Dict[str, Any]: A dictionary containing the key "snippets", which maps to a list 
    of the top 5 relevant knowledge base snippets (strings). 
    If no relevant snippets are found, the list will be empty.

    Notes:
    - The function will return a maximum of 5 snippets per query.
    - If no relevant snippets are found, the list will be empty.
    - The query is translated internally into English if needed, ensuring accurate results.
    """
	docs = retrieve_knowledge(query, collection_name)
	return {"snippets": [d.page_content for d in docs[:5]]}


@tool("retrieve_memory", return_direct=False)
def retrieve_memory_tool(params: Dict[str, Any]) -> Dict[str, Any]:
	"""Retrieve conversational memory with keys: session_id, query, k (optional)."""
	session_id = params.get("session_id", "")
	query = params.get("query", "")
	k = int(params.get("k", 4))
	docs = retrieve_memory(session_id, query, k=k)
	return {"mem": [d.page_content for d in docs]}


@tool("add_memory", return_direct=False)
def add_memory_tool(params: Dict[str, Any]) -> str:
	"""Add memory with keys: session_id, role, content."""
	session_id = params.get("session_id", "")
	role = params.get("role", "assistant")
	content = params.get("content", "")
	if not (session_id and content):
		return "missing params"
	add_memory(session_id, role, content)
	return "ok"


@tool("translate_to_english", return_direct=False)
def translate_to_english_tool(text: str) -> str:
	"""Translate text to English."""
	return translate_text(text, "en")


@tool("notify_email_support", return_direct=False)
def notify_email_support_tool(params: Dict[str, Any]) -> str:
	"""Send an email to support with keys: subject, body. Returns 'ok' even if SMTP not configured."""
	subject = params.get("subject", "AI-CS Handover Needed")
	body = params.get("body", "")
	try:
		send_support_email(subject=subject, body=body)
		return "ok"
	except Exception:
		return "ok"


@tool("notify_telegram_support", return_direct=False)
def notify_telegram_support_tool(text: str) -> str:
	"""Send a Telegram message to support chat with the given text. Returns 'ok' even if token not configured."""
	try:
		notify_support_telegram(text)
		return "ok"
	except Exception:
		return "ok"