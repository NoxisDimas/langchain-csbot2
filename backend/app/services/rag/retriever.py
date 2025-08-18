from typing import List
from langchain.schema import Document
from app.services.llm.provider import get_embedding_model
from app.config import get_settings
from app.utils.lang import detect_language, translate_text

try:
	from langchain_postgres import PGVector
except Exception:  # pragma: no cover - optional import at dev time
	PGVector = None  # type: ignore


_settings = get_settings()
_vectorstore = None


def _get_vectorstore():
	global _vectorstore
	if _vectorstore is not None:
		return _vectorstore
	if PGVector is None:
		return None
	_embeddings = get_embedding_model()
	_vectorstore = PGVector(
		connection_string=_settings.DATABASE_URL,
		collection_name=f"{_settings.DB_SCHEMA}",
		embedding_function=_embeddings,
	)
	return _vectorstore


def retrieve_knowledge(query_text: str) -> List[Document]:
	vs = _get_vectorstore()
	if vs is None:
		return []
	# lang = detect_language(query_text)
	q = query_text
	retriever = vs.as_retriever(search_kwargs={"k": 5})
	return retriever.get_relevant_documents(q)