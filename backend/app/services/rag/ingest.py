from typing import List
from langchain.schema import Document
from app.services.llm.provider import get_embedding_model
from app.config import get_settings

try:
	from langchain_postgres import PGVector
except Exception:
	PGVector = None  # type: ignore


_settings = get_settings()


def ingest_documents(docs: List[Document]):
	if PGVector is None:
		raise RuntimeError("langchain-postgres is not installed or DB not configured")
	embeddings = get_embedding_model()
	vs = PGVector(
		connection_string=_settings.DATABASE_URL,
		collection_name=f"{_settings.DB_SCHEMA}",
		embedding_function=embeddings,
	)
	vs.add_documents(docs)