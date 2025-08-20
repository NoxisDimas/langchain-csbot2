from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
import uuid
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy import text

from app.services.database_service import DatabaseService
from app.services.document_service import DocumentService
from app.services.vectorstore_service import VectorStoreService
from app.config import get_settings

router = APIRouter(prefix="/rag", tags=["RAG System"])

# Pydantic models
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

class SearchResponse(BaseModel):
    id: str
    chunk_text: str
    metadata: Dict[str, Any]
    chunk_index: int
    filename: str
    file_type: str
    similarity: float

class UploadResponse(BaseModel):
    document_id: str
    filename: str
    status: str
    message: str


class SearchRequest(BaseModel):
    query: str
    knowledge_base: Optional[str] = None
    limit: int = 5


class ProcessEmbeddingsRequest(BaseModel):
    knowledge_base: Optional[str] = None
    batch_size: int = 100


class VectorAddRequest(BaseModel):
    texts: List[str]
    user_id: str
    collection_name: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class VectorDeleteRequest(BaseModel):
    ids: List[str]
    collection_name: Optional[str] = None

# Initialize services
settings = get_settings()
try:
    db_service = DatabaseService()
    document_service = DocumentService()
    vector_service = VectorStoreService()
except Exception as e:
    print(f"Warning: Failed to initialize database services: {e}")
    db_service = None
    document_service = None
    vector_service = None

@router.post("/knowledge-bases", response_model=KnowledgeBaseResponse)
async def create_knowledge_base(kb_data: KnowledgeBaseCreate):
    """Create a new knowledge base"""
    try:
        kb = db_service.create_knowledge_base(kb_data.name, kb_data.description)
        if not kb:
            # If creation failed (possibly due to unique constraint), return existing if it exists
            kb = db_service.get_knowledge_base(kb_data.name)
            if not kb:
                raise HTTPException(status_code=400, detail="Failed to create knowledge base")
        
        return KnowledgeBaseResponse(
            id=str(kb.id),
            name=kb.name,
            description=kb.description,
            schema_name=kb.schema_name,
            is_active=kb.is_active,
            created_at=kb.created_at,
            updated_at=kb.updated_at
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal error")

@router.get("/knowledge-bases", response_model=List[KnowledgeBaseResponse])
async def list_knowledge_bases():
    """List all knowledge bases"""
    try:
        kbs = db_service.list_knowledge_bases()
        return [
            KnowledgeBaseResponse(
                id=str(kb.id),
                name=kb.name,
                description=kb.description,
                schema_name=kb.schema_name,
                is_active=kb.is_active,
                created_at=kb.created_at,
                updated_at=kb.updated_at
            )
            for kb in kbs
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal error")

@router.delete("/knowledge-bases/{kb_name}")
async def delete_knowledge_base(kb_name: str):
    """Delete a knowledge base"""
    try:
        success = db_service.delete_knowledge_base(kb_name)
        if not success:
            raise HTTPException(status_code=404, detail="Knowledge base not found")
        
        return {"message": f"Knowledge base '{kb_name}' deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal error")

@router.post("/upload", response_model=UploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    knowledge_base: str = Form("default")
):
    """Upload and process a file"""
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        if not document_service.is_supported_file(file.filename):
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type: {document_service.get_file_extension(file.filename)}"
            )
        
        # Read file content
        file_content = await file.read()
        if not file_content:
            raise HTTPException(status_code=400, detail="Empty file")
        
        # RAG-only: process to chunks and ingest to vectorstore
        chunks = document_service.process_file_to_chunks(file_content, file.filename, knowledge_base)
        if not chunks:
            raise HTTPException(status_code=400, detail="No text content extracted from file")
        
        # Use knowledge_base parameter as collection name, fallback to DB_SCHEMA
        collection_name = knowledge_base if knowledge_base and knowledge_base.strip() else settings.DB_SCHEMA
        ids = vector_service.add_documents(chunks, collection_name=collection_name)
        return UploadResponse(
            document_id=ids[0] if ids else str(uuid.uuid4()),
            filename=file.filename,
            status="uploaded",
            message=f"File uploaded and {len(ids)} chunks ingested into vectorstore."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal error")

## legacy background embedding was removed

## legacy documents endpoint removed

## legacy documents delete removed

@router.post("/search", response_model=List[SearchResponse])
async def search_documents(req: SearchRequest):
    """Search documents using vector similarity (LangChain PGVector only)."""
    try:
        if not req.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        user_filter = None  # extend with authenticated user context
        # Use knowledge_base parameter as collection name, fallback to DB_SCHEMA
        collection_name = req.knowledge_base if req.knowledge_base and req.knowledge_base.strip() else settings.DB_SCHEMA
        docs = vector_service.search(query=req.query, user_id=user_filter, k=req.limit, collection_name=collection_name)
        return [
            SearchResponse(
                id=doc.metadata.get("id", str(uuid.uuid4())),
                chunk_text=doc.page_content,
                metadata=doc.metadata,
                chunk_index=doc.metadata.get("chunk_index", 0),
                filename=doc.metadata.get("filename", ""),
                file_type=doc.metadata.get("file_type", ""),
                similarity=float(doc.metadata.get("similarity", 0.0)),
            )
            for doc in docs
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Legacy endpoint removed

@router.get("/stats")
async def get_stats(collection_name: Optional[str] = None, user_id: Optional[str] = None):
    """Vectorstore-centric stats."""
    try:
        vs_stats = vector_service.get_collection_stats(collection_name=collection_name, user_id=user_id)
        return {
            "vectorstore": vs_stats,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        with db_service.get_session() as session:
            session.execute(text("SELECT 1"))
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "services": {
                "database": "connected",
                "embedding_model": "available"
            }
        }
    except Exception:
        raise HTTPException(status_code=503, detail="Service unhealthy")


# --- VectorStore CRUD (LangChain PGVector) ---
@router.post("/vector/add")
async def vector_add(req: VectorAddRequest):
    try:
        if not vector_service:
            raise HTTPException(status_code=503, detail="Vector service unavailable")
        ids = vector_service.add_texts(
            texts=req.texts,
            user_id=req.user_id,
            collection_name=req.collection_name,
            base_metadata=req.metadata or {},
        )
        return {"inserted": len(ids), "ids": ids}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Internal error")


@router.post("/vector/delete")
async def vector_delete(req: VectorDeleteRequest):
    try:
        if not vector_service:
            raise HTTPException(status_code=503, detail="Vector service unavailable")
        vector_service.delete_ids(req.ids, collection_name=req.collection_name)
        return {"deleted": len(req.ids)}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Internal error")