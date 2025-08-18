from typing import List
from langchain.schema import Document
from app.services.llm.provider import get_embedding_model
from app.config import get_settings
from app.utils.lang import detect_language, translate_text

try:
	from langchain_postgres import PGVector
except Exception:
	PGVector = None  # type: ignore


_settings = get_settings()
_memstore = None


def _get_memstore():
	global _memstore
	if _memstore is not None:
		return _memstore
	if PGVector is None:
		return None
	embeddings = get_embedding_model()
	_memstore = PGVector(
		embeddings=embeddings,
		connection=_settings.DATABASE_URL,
		collection_name=f"{_settings.DB_SCHEMA}_memory",
	)
	return _memstore


def add_memory(session_id: str, role: str, content: str):
	vs = _get_memstore()
	if vs is None or not content:
		return
	doc = Document(page_content=content, metadata={"session_id": session_id, "role": role})
	vs.add_documents([doc])


def retrieve_memory(session_id: str, query_text: str, k: int = 4) -> List[Document]:
	vs = _get_memstore()
	if vs is None or not query_text:
		return []
	lang = detect_language(query_text)
	q = query_text if lang == "en" else translate_text(query_text, "en")
	retriever = vs.as_retriever(search_kwargs={"k": k, "filter": {"session_id": {"$eq": session_id}}})
	try:
		return retriever.get_relevant_documents(q)
	except Exception:
		# Fallback without filter if backend doesn't support it
		docs = retriever.get_relevant_documents(q)
		return [d for d in docs if d.metadata.get("session_id") == session_id][:k]