from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
import os
import shutil
import logging
from pydantic import BaseModel
from datetime import datetime

from app.services.rag.vector_store import VectorStore
from app.services.rag.ingest import ingest_documents, get_ingestion_stats
from app.config import get_settings

router = APIRouter(prefix="/rag", tags=["RAG System"])
logger = logging.getLogger(__name__)

settings = get_settings()

# Pydantic models
class SearchRequest(BaseModel):
    query: str
    limit: int = 5

class SearchResponse(BaseModel):
    content: str
    metadata: Dict[str, Any]
    similarity_score: float

class UploadResponse(BaseModel):
    filename: str
    status: str
    message: str

class CollectionInfo(BaseModel):
    name: str
    document_count: int
    embedding_model: str
    database_url: str

class StatsResponse(BaseModel):
    collection_name: str
    database_url: str
    embedding_model: str
    uploads_folder: str
    files_count: int
    collection: CollectionInfo

@router.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """Upload a file to the uploads folder"""
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Check if file type is supported
        supported_extensions = ['.txt', '.csv', '.pdf', '.docx', '.xlsx', '.md']
        file_ext = os.path.splitext(file.filename)[1].lower()
        
        if file_ext not in supported_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type: {file_ext}. Supported: {', '.join(supported_extensions)}"
            )
        
        # Read file content
        file_content = await file.read()
        if not file_content:
            raise HTTPException(status_code=400, detail="Empty file")
        
        # Save file to uploads folder
        uploads_dir = os.path.join(os.path.dirname(__file__), "..", "..", "..", "uploads")
        os.makedirs(uploads_dir, exist_ok=True)
        
        file_path = os.path.join(uploads_dir, file.filename)
        with open(file_path, "wb") as buffer:
            buffer.write(file_content)
        
        logger.info(f"✅ File uploaded: {file.filename}")
        
        return UploadResponse(
            filename=file.filename,
            status="uploaded",
            message=f"File {file.filename} uploaded successfully to uploads folder."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Upload failed: {e}")
        raise HTTPException(status_code=500, detail="Internal error")

@router.post("/ingest")
async def ingest_uploaded_files(update_existing: bool = True):
    """Ingest all files from uploads folder into vector store"""
    try:
        logger.info("🚀 Starting ingestion of uploaded files...")
        
        success = ingest_documents(update_existing=update_existing)
        
        if success:
            return {
                "status": "success",
                "message": "Documents ingested successfully into vector store",
                "update_existing": update_existing
            }
        else:
            return {
                "status": "warning",
                "message": "No documents were ingested (uploads folder might be empty)",
                "update_existing": update_existing
            }
            
    except Exception as e:
        logger.error(f"❌ Ingestion failed: {e}")
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")

@router.post("/search", response_model=List[SearchResponse])
async def search_documents(req: SearchRequest):
    """Search documents using vector similarity"""
    try:
        if not req.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        vector_store = VectorStore()
        results = vector_store.similarity_search(req.query, k=req.limit)
        
        search_results = []
        for doc, score in results:
            search_results.append(SearchResponse(
                content=doc.page_content,
                metadata=doc.metadata,
                similarity_score=float(score)
            ))
        
        logger.info(f"🔍 Search completed: {len(search_results)} results for query: {req.query[:50]}...")
        return search_results
        
    except Exception as e:
        logger.error(f"❌ Search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search/filter")
async def filter_documents(
    key: str,
    value: str,
    k: int = 100,
    offset: int = 0
):
    """Filter documents by metadata"""
    try:
        if key not in ["category", "title", "source"]:
            raise HTTPException(
                status_code=400, 
                detail="Only 'category', 'title', or 'source' are supported as filters"
            )
        
        vector_store = VectorStore()
        results = vector_store.filter_by_metadata(key, value, k=k, offset=offset)
        
        filtered_results = []
        for doc, score in results:
            filtered_results.append({
                "content": doc.page_content,
                "metadata": doc.metadata,
                "similarity_score": float(score)
            })
        
        logger.info(f"🔍 Filter completed: {len(filtered_results)} results for {key}={value}")
        return {
            "results": filtered_results,
            "total": len(filtered_results),
            "filter": {key: value}
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Filter failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_stats():
    """Get vector store statistics with frontend compatibility"""
    try:
        stats = get_ingestion_stats()
        
        if "error" in stats:
            raise HTTPException(status_code=500, detail=stats["error"])
        
        # Return both new and legacy structure for maximum compatibility
        return {
            # New structure
            "collection_name": stats.get("collection_name", "ai_cs"),
            "database_url": stats.get("database_url", "Unknown"),
            "embedding_model": stats.get("embedding_model", "Unknown"),
            "uploads_folder": stats.get("uploads_folder", "Unknown"),
            "files_count": stats.get("files_count", 0),
            "collection": {
                "name": stats.get("collection_name", "ai_cs"),
                "document_count": stats.get("files_count", 0),
                "embedding_model": stats.get("embedding_model", "Unknown"),
                "database_url": stats.get("database_url", "Unknown")
            },
            # Legacy structure for frontend compatibility
            "vectorstore": {
                "collection": {
                    "name": stats.get("collection_name", "ai_cs"),
                    "document_count": stats.get("files_count", 0),
                    "embedding_model": stats.get("embedding_model", "Unknown"),
                    "database_url": stats.get("database_url", "Unknown")
                }
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Stats failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test vector store connection
        vector_store = VectorStore()
        stats = vector_store.get_collection_stats()
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "services": {
                "database": "connected",
                "vector_store": "available",
                "embedding_model": "available"
            },
            "stats": stats
        }
    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")

@router.delete("/files/{filename}")
async def delete_file(filename: str):
    """Delete a file from uploads folder"""
    try:
        uploads_dir = os.path.join(os.path.dirname(__file__), "..", "..", "..", "uploads")
        file_path = os.path.join(uploads_dir, filename)
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        os.remove(file_path)
        logger.info(f"🗑️ File deleted: {filename}")
        
        return {
            "status": "success",
            "message": f"File {filename} deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ File deletion failed: {e}")
        raise HTTPException(status_code=500, detail="Internal error")

@router.get("/files")
async def list_files():
    """List all files in uploads folder"""
    try:
        uploads_dir = os.path.join(os.path.dirname(__file__), "..", "..", "..", "uploads")
        
        if not os.path.exists(uploads_dir):
            return {"files": []}
        
        files = []
        for filename in os.listdir(uploads_dir):
            file_path = os.path.join(uploads_dir, filename)
            if os.path.isfile(file_path):
                file_stat = os.stat(file_path)
                files.append({
                    "filename": filename,
                    "size": file_stat.st_size,
                    "modified": datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
                    "extension": os.path.splitext(filename)[1].lower()
                })
        
        return {"files": files}
        
    except Exception as e:
        logger.error(f"❌ File listing failed: {e}")
        raise HTTPException(status_code=500, detail="Internal error")

# Backward compatibility endpoints
class KnowledgeBaseCreate(BaseModel):
    name: str
    description: Optional[str] = None

class KnowledgeBaseResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    schema_name: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

@router.post("/knowledge-bases", response_model=KnowledgeBaseResponse)
async def create_knowledge_base(kb_data: KnowledgeBaseCreate):
    """Backward compatibility: Create a knowledge base (now uses single collection)"""
    try:
        logger.info(f"🔄 Backward compatibility: Creating knowledge base '{kb_data.name}'")
        
        # In the new system, we use a single collection
        # This endpoint now just returns a mock response for compatibility
        return KnowledgeBaseResponse(
            id="default",
            name=kb_data.name,
            description=kb_data.description,
            schema_name=settings.DB_SCHEMA,
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
    except Exception as e:
        logger.error(f"❌ Knowledge base creation failed: {e}")
        raise HTTPException(status_code=500, detail="Internal error")

@router.get("/knowledge-bases", response_model=List[KnowledgeBaseResponse])
async def list_knowledge_bases():
    """Backward compatibility: List knowledge bases (now uses single collection)"""
    try:
        logger.info("🔄 Backward compatibility: Listing knowledge bases")
        
        # In the new system, we use a single collection
        # Return a default knowledge base for compatibility
        return [
            KnowledgeBaseResponse(
                id="default",
                name="Default Knowledge Base",
                description="Default knowledge base using single collection",
                schema_name=settings.DB_SCHEMA,
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
        ]
    except Exception as e:
        logger.error(f"❌ Knowledge bases listing failed: {e}")
        raise HTTPException(status_code=500, detail="Internal error")

@router.delete("/knowledge-bases/{kb_name}")
async def delete_knowledge_base(kb_name: str):
    """Backward compatibility: Delete knowledge base (not applicable in new system)"""
    try:
        logger.info(f"🔄 Backward compatibility: Deleting knowledge base '{kb_name}'")
        
        # In the new system, we don't delete collections
        # Just return success for compatibility
        return {"message": f"Knowledge base '{kb_name}' deleted successfully (no-op in new system)"}
    except Exception as e:
        logger.error(f"❌ Knowledge base deletion failed: {e}")
        raise HTTPException(status_code=500, detail="Internal error")

# Legacy stats endpoint for frontend compatibility
@router.get("/stats/legacy")
async def get_legacy_stats():
    """Legacy stats endpoint with old structure for frontend compatibility"""
    try:
        stats = get_ingestion_stats()
        
        if "error" in stats:
            raise HTTPException(status_code=500, detail=stats["error"])
        
        # Return legacy structure that frontend expects
        return {
            "vectorstore": {
                "collection": {
                    "name": stats.get("collection_name", "ai_cs"),
                    "document_count": stats.get("files_count", 0),
                    "embedding_model": stats.get("embedding_model", "Unknown"),
                    "database_url": stats.get("database_url", "Unknown")
                }
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Legacy stats failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))