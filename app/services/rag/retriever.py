import logging
from typing import List, Optional
from langchain_core.documents import Document
from app.services.llm.provider import get_embedding_model
from app.config import get_settings
from app.utils.lang import detect_language, translate_text
from langchain_postgres import PGVector

_settings = get_settings()
logger = logging.getLogger(__name__)
    
    # Use provided collection name or fallback to DB_SCHEMA
def _get_vectorstore(collection_name: Optional[str] = None):
    """Get vectorstore with specified collection name"""
    if PGVector is None:
        logger.error("PGVector is not available.")
        return None
    if not _settings.DATABASE_URL:
        logger.error("Database URL is not set in settings.")
        return None
    
    # Use provided collection name or fallback to DB_SCHEMA
    cname = collection_name or _settings.DB_SCHEMA
    logger.info(f"Initializing vectorstore for collection: {cname}")
    
    try:
        _embeddings = get_embedding_model()
        vectorstore = PGVector(
            _embeddings,
            connection=_settings.DATABASE_URL,
            collection_name=cname,
        )
        logger.info("Vectorstore initialized successfully.")
        return vectorstore
    except Exception as e:
        logger.exception("Error initializing vectorstore: %s", e)
        return None
    
def retrieve_knowledge(query_text: str, collection_name: Optional[str] = None) -> List[Document]:
    logger.info("Retrieving knowledge for query: %s from collection: %s", query_text, collection_name or _settings.DB_SCHEMA)
    
    vs = _get_vectorstore(collection_name)
    if vs is None:
        logger.warning("Vectorstore is not available. Returning empty result.")
        return []
    result = vs.similarity_search(query_text, k=5)
    logger.info("Retrieved %d documents.", len(result))
    return result   
