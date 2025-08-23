import logging
from typing import List, Optional
from langchain_core.documents import Document
from app.services.rag.vector_store import VectorStore
from app.utils.lang import detect_language, translate_text

logger = logging.getLogger(__name__)

def retrieve_knowledge(query_text: str, collection_name: Optional[str] = None) -> List[Document]:
    """
    Retrieve knowledge from vector store using the new VectorStore class
    """
    logger.info("Retrieving knowledge for query: %s", query_text)
    
    try:
        vector_store = VectorStore()
        results = vector_store.similarity_search(query_text, k=5)
        
        # Extract documents from (document, score) tuples
        documents = [doc for doc, score in results]
        logger.info("Retrieved %d documents.", len(documents))
        return documents
        
    except Exception as e:
        logger.error("Error retrieving knowledge: %s", e)
        return []

def retrieve_knowledge_with_scores(query_text: str, k: int = 5) -> List[tuple]:
    """
    Retrieve knowledge with similarity scores
    """
    logger.info("Retrieving knowledge with scores for query: %s", query_text)
    
    try:
        vector_store = VectorStore()
        results = vector_store.similarity_search(query_text, k=k)
        logger.info("Retrieved %d documents with scores.", len(results))
        return results
        
    except Exception as e:
        logger.error("Error retrieving knowledge with scores: %s", e)
        return []

def filter_knowledge_by_metadata(key: str, value: str, k: int = 100) -> List[tuple]:
    """
    Filter knowledge by metadata
    """
    logger.info("Filtering knowledge by %s=%s", key, value)
    
    try:
        vector_store = VectorStore()
        results = vector_store.filter_by_metadata(key, value, k=k)
        logger.info("Filtered %d documents.", len(results))
        return results
        
    except Exception as e:
        logger.error("Error filtering knowledge: %s", e)
        return []   
