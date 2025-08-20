from typing import List
from langchain_core.documents import Document
from app.services.llm.provider import get_embedding_model
from app.config import get_settings
from app.utils.lang import detect_language, translate_text
from langchain_postgres import PGVector


_settings = get_settings()


def ingest_documents(docs: List[Document]):
	if PGVector is None:
		raise RuntimeError("langchain-postgres is not installed or DB not configured")
	if not _settings.DATABASE_URL:
		raise RuntimeError("DATABASE_URL not configured")
	embeddings = get_embedding_model()
	vs = PGVector(
		embeddings,
		connection=_settings.DATABASE_URL,
		collection_name=f"{_settings.DB_SCHEMA}",
	)
	vs.add_documents(docs)