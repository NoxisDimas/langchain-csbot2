from app.services.rag.vector_store import VectorStore
import logging

logger = logging.getLogger(__name__)

def ingest_documents(update_existing: bool = True):
    """
    Ingest documents from uploads folder into vector store using new VectorStore class
    """
    try:
        logger.info("🚀 Starting document ingestion process...")
        
        vector_store = VectorStore()
        result = vector_store.build_vector_store(update_existing=update_existing)
        
        if result:
            logger.info("✅ Document ingestion completed successfully")
            return True
        else:
            logger.warning("⚠️ No documents were ingested")
            return False
            
    except Exception as e:
        logger.error(f"❌ Document ingestion failed: {e}")
        return False

def get_ingestion_stats():
    """
    Get statistics about the vector store and ingestion status
    """
    try:
        vector_store = VectorStore()
        stats = vector_store.get_collection_stats()
        logger.info("📊 Retrieved ingestion statistics")
        return stats
    except Exception as e:
        logger.error(f"❌ Failed to get ingestion stats: {e}")
        return {"error": str(e)}