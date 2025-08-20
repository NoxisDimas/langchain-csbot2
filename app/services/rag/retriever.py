import logging
from typing import List
from langchain_core.documents import Document
from app.services.llm.provider import get_embedding_model
from app.config import get_settings
from app.utils.lang import detect_language, translate_text
from langchain_postgres import PGVector

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

_settings = get_settings()
_vectorstore = None

def _get_vectorstore():
    global _vectorstore
    if _vectorstore is not None:
        logger.debug("Returning existing vectorstore.")
        return _vectorstore
    if PGVector is None:
        logger.error("PGVector is not available.")
        return None
    if not _settings.DATABASE_URL:
        logger.error("Database URL is not set in settings.")
        return None
    
    logger.info("Initializing new vectorstore...")
    try:
        _embeddings = get_embedding_model()
        _vectorstore = PGVector(
            _embeddings,
            connection=_settings.DATABASE_URL,
            collection_name=f"{_settings.DB_SCHEMA}",
        )
        logger.info("Vectorstore initialized successfully.")
    except Exception as e:
        logger.exception("Error initializing vectorstore: %s", e)
        return None
    return _vectorstore

def retrieve_knowledge(query_text: str) -> List[Document]:
    logger.info("Retrieving knowledge for query: %s", query_text)
    
    vs = _get_vectorstore()
    if vs is None:
        logger.warning("Vectorstore is not available. Returning empty result.")
        return []
    
    # lang = detect_language(query_text)  # You can add the language detection logging if necessary
    q = query_text
    retriever = vs.as_retriever(search_kwargs={"k": 5})
    
    try:
        result = retriever.invoke(q)
        logger.info("Knowledge retrieval successful, found %d documents.", len(result))
    except Exception as e:
        logger.error("Error during knowledge retrieval: %s", e)
        return []
    
    return result
