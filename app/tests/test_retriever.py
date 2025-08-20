from sqlalchemy import create_engine
from app.config import get_settings
from langchain_postgres import PGVector
import logging
from app.services.rag.retriever import get_embedding_model

logging.basicConfig(level=logging.DEBUG)

_settings = get_settings()

def test_connection():
    try:
        engine = create_engine(_settings.DATABASE_URL)
        with engine.connect() as connection:
            return("Database connection successful.")
    except Exception as e:
        return("Database connection failed: %s", e)
    

def _get_vectorstore():
    global _vectorstore
    if _vectorstore is not None:
        logging.debug("Returning existing vectorstore.")
        return _vectorstore
    if PGVector is None:
        logging.error("PGVector is not available.")
        return None
    if not _settings.DATABASE_URL:
        logging.error("Database URL is not set in settings.")
        return None

    logging.info("Initializing new vectorstore...")
    try:
        _embeddings = get_embedding_model()
        _vectorstore = PGVector(
            embeddings=_embeddings,
            connection=_settings.DATABASE_URL,
            collection_name=f"{_settings.DB_SCHEMA}",
        )
        logging.info("Vectorstore initialized successfully.")
    except Exception as e:
        logging.exception("Error initializing vectorstore: %s", e)
        return None
    return _vectorstore


if __name__ == "__main__":
    res = _get_vectorstore()
    print(res)