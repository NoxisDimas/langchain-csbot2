from typing import List, Dict, Any, Optional
from langchain_core.documents import Document
from app.config import get_settings
from app.services.llm.provider import get_embedding_model
from sqlalchemy import create_engine, text

try:
	from langchain_postgres import PGVector
except Exception:
	PGVector = None  # type: ignore


_settings = get_settings()


class VectorStoreService:
	"""Wrapper for LangChain PGVector vectorstore with simple CRUD ops and multi-tenant filtering via metadata."""

	def __init__(self, default_collection: str = "documents"):
		if PGVector is None:
			raise RuntimeError("langchain-postgres not installed")
		if not _settings.DATABASE_URL:
			raise RuntimeError("DATABASE_URL not configured")
		self._embeddings = get_embedding_model()
		self._default_collection = default_collection

	def _get_store(self, collection_name: Optional[str] = None) -> Any:  # PGVector
		return PGVector(
			self._embeddings,
			connection=_settings.DATABASE_URL,
			collection_name=(collection_name or self._default_collection),
		)

	def get_collection_stats(self, collection_name: Optional[str] = None, user_id: Optional[str] = None) -> Dict[str, Any]:
		"""Return simple stats for a collection (total vectors; optionally filtered by user_id)."""
		engine = create_engine(_settings.DATABASE_URL)
		with engine.connect() as conn:
			# Resolve collection id
			cid = None
			if collection_name:
				row = conn.execute(text("SELECT uuid FROM langchain_pg_collection WHERE name = :name"), {"name": collection_name}).fetchone()
				if row:
					cid = row[0]
			else:
				row = conn.execute(text("SELECT uuid FROM langchain_pg_collection WHERE name = :name"), {"name": self._default_collection}).fetchone()
				if row:
					cid = row[0]
			if not cid:
				return {"collection": collection_name or self._default_collection, "total_vectors": 0}
			params: Dict[str, Any] = {"cid": cid}
			if user_id:
				cnt = conn.execute(text("SELECT COUNT(*) FROM langchain_pg_embedding WHERE collection_id = :cid AND (cmetadata->>'user_id') = :uid"), {"cid": cid, "uid": user_id}).scalar()
			else:
				cnt = conn.execute(text("SELECT COUNT(*) FROM langchain_pg_embedding WHERE collection_id = :cid"), params).scalar()
			return {"collection": collection_name or self._default_collection, "total_vectors": int(cnt or 0)}

	def add_texts(
		self,
		texts: List[str],
		user_id: str,
		collection_name: Optional[str] = None,
		base_metadata: Optional[Dict[str, Any]] = None,
	) -> List[str]:
		vs = self._get_store(collection_name)
		docs = [
			Document(page_content=txt, metadata={**(base_metadata or {}), "user_id": user_id})
			for txt in texts if txt and txt.strip()
		]
		if not docs:
			return []
		return vs.add_documents(docs)

	def add_documents(
		self,
		documents: List[Document],
		collection_name: Optional[str] = None,
	) -> List[str]:
		vs = self._get_store(collection_name)
		return vs.add_documents(documents)

	def delete_ids(self, ids: List[str], collection_name: Optional[str] = None) -> None:
		if not ids:
			return
		vs = self._get_store(collection_name)
		vs.delete(ids)

	def search(
		self,
		query: str,
		user_id: Optional[str] = None,
		collection_name: Optional[str] = None,
		k: int = 5,
		mmr: bool = True,
		filters: Optional[Dict[str, Any]] = None,
	) -> List[Document]:
		if not query or not query.strip():
			return []
		vs = self._get_store(collection_name)
		search_kwargs: Dict[str, Any] = {"k": k}
		flt: Dict[str, Any] = filters.copy() if filters else {}
		if user_id:
			# Prefer vectorstore filtering if supported
			flt = {**flt, "user_id": {"$eq": user_id}}
		if flt:
			search_kwargs["filter"] = flt
		retriever = vs.as_retriever(
			search_type=("mmr" if mmr else "similarity"),
			search_kwargs=search_kwargs,
		)
		try:
			return retriever.invoke(query)
		except Exception:
			# Fallback: no server-side filter support, filter client-side
			docs = retriever.invoke(query)
			if user_id:
				return [d for d in docs if d.metadata.get("user_id") == user_id][:k]
			return docs[:k]

