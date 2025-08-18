from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
import uuid
from pydantic import BaseModel
from datetime import datetime

from app.services.database_service import DatabaseService
from app.services.document_service import DocumentService
from app.services.embedding_service import EmbeddingService

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

class DocumentResponse(BaseModel):
    id: str
    filename: str
    file_type: str
    file_size: int
    is_processed: bool
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

# Initialize services
db_service = DatabaseService()
document_service = DocumentService()
embedding_service = EmbeddingService()

@router.post("/knowledge-bases", response_model=KnowledgeBaseResponse)
async def create_knowledge_base(kb_data: KnowledgeBaseCreate):
    """Create a new knowledge base"""
    try:
        kb = db_service.create_knowledge_base(kb_data.name, kb_data.description)
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
        raise HTTPException(status_code=500, detail=str(e))

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
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/knowledge-bases/{kb_name}")
async def delete_knowledge_base(kb_name: str):
    """Delete a knowledge base"""
    try:
        success = db_service.delete_knowledge_base(kb_name)
        if not success:
            raise HTTPException(status_code=404, detail="Knowledge base not found")
        
        return {"message": f"Knowledge base '{kb_name}' deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload", response_model=UploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    knowledge_base: str = "default",
    background_tasks: BackgroundTasks = None
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
        
        # Process file
        document = await document_service.process_file(file_content, file.filename, knowledge_base)
        if not document:
            raise HTTPException(status_code=500, detail="Failed to process file")
        
        # Add background task to create embeddings
        if background_tasks:
            background_tasks.add_task(
                process_embeddings_background,
                str(document.id),
                knowledge_base
            )
        
        return UploadResponse(
            document_id=str(document.id),
            filename=document.filename,
            status="uploaded",
            message="File uploaded and processed successfully. Embeddings will be created in background."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def process_embeddings_background(document_id: str, knowledge_base: str):
    """Background task to process embeddings"""
    try:
        # Get chunks for the document
        chunks = document_service.get_document_chunks(document_id)
        if chunks:
            # Create embeddings
            embedding_service.update_chunk_embeddings(chunks)
            print(f"Created embeddings for document {document_id}")
    except Exception as e:
        print(f"Error processing embeddings for document {document_id}: {e}")

@router.get("/documents", response_model=List[DocumentResponse])
async def list_documents(knowledge_base: Optional[str] = None):
    """List all documents"""
    try:
        documents = db_service.get_documents(knowledge_base)
        return [
            DocumentResponse(
                id=str(doc.id),
                filename=doc.filename,
                file_type=doc.file_type,
                file_size=doc.file_size,
                is_processed=doc.is_processed,
                created_at=doc.created_at,
                updated_at=doc.updated_at
            )
            for doc in documents
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/documents/{document_id}")
async def delete_document(document_id: str):
    """Delete a document"""
    try:
        success = db_service.delete_document(document_id)
        if not success:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return {"message": "Document deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search", response_model=List[SearchResponse])
async def search_documents(
    query: str,
    knowledge_base: Optional[str] = None,
    limit: int = 5
):
    """Search documents using vector similarity"""
    try:
        if not query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        results = embedding_service.search_similar_chunks(query, knowledge_base, limit)
        
        return [
            SearchResponse(
                id=result["id"],
                chunk_text=result["chunk_text"],
                metadata=result["metadata"],
                chunk_index=result["chunk_index"],
                filename=result["filename"],
                file_type=result["file_type"],
                similarity=result["similarity"]
            )
            for result in results
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/process-embeddings")
async def process_pending_embeddings(
    knowledge_base: Optional[str] = None,
    batch_size: int = 100
):
    """Process all pending embeddings"""
    try:
        processed_count = embedding_service.process_pending_embeddings(knowledge_base, batch_size)
        return {
            "message": f"Processed {processed_count} embeddings",
            "processed_count": processed_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_stats(knowledge_base: Optional[str] = None):
    """Get system statistics"""
    try:
        # Get embedding stats
        embedding_stats = embedding_service.get_embedding_stats(knowledge_base)
        
        # Get knowledge base stats
        kbs = db_service.list_knowledge_bases()
        kb_count = len(kbs)
        
        # Get document stats
        documents = db_service.get_documents(knowledge_base)
        doc_count = len(documents)
        
        return {
            "knowledge_bases": kb_count,
            "documents": doc_count,
            "embeddings": embedding_stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        with db_service.get_session() as session:
            session.execute("SELECT 1")
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "services": {
                "database": "connected",
                "embedding_model": "available"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")