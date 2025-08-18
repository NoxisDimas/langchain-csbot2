import os
import json
from typing import List, Dict, Any, Optional
from sqlalchemy import text
from langchain_openai import OpenAIEmbeddings
from langchain_community.embeddings import OllamaEmbeddings
from app.services.database_service import DatabaseService
from app.persistence.models import DocumentEmbedding
from app.config import get_settings

settings = get_settings()

class EmbeddingService:
    def __init__(self):
        self.db_service = DatabaseService()
        self.embeddings_model = self._initialize_embeddings_model()
    
    def _initialize_embeddings_model(self):
        """Initialize embeddings model based on configuration"""
        if settings.openai_api_key:
            return OpenAIEmbeddings(
                openai_api_key=settings.openai_api_key,
                model="text-embedding-3-small"
            )
        elif settings.ollama_base_url:
            return OllamaEmbeddings(
                model="llama2",
                base_url=settings.ollama_base_url
            )
        else:
            # Fallback to OpenAI with default settings
            return OpenAIEmbeddings()
    
    def create_embeddings_for_chunks(self, chunks: List[DocumentEmbedding]) -> List[List[float]]:
        """Create embeddings for a list of text chunks"""
        if not chunks:
            return []
        
        texts = [chunk.chunk_text for chunk in chunks]
        try:
            embeddings = self.embeddings_model.embed_documents(texts)
            return embeddings
        except Exception as e:
            print(f"Error creating embeddings: {e}")
            return []
    
    def create_embedding_for_text(self, text: str) -> Optional[List[float]]:
        """Create embedding for a single text"""
        try:
            embedding = self.embeddings_model.embed_query(text)
            return embedding
        except Exception as e:
            print(f"Error creating embedding: {e}")
            return None
    
    def update_chunk_embeddings(self, chunks: List[DocumentEmbedding]) -> bool:
        """Update embeddings for existing chunks"""
        try:
            if not chunks:
                return True
            
            # Create embeddings
            embeddings = self.create_embeddings_for_chunks(chunks)
            
            if len(embeddings) != len(chunks):
                print("Mismatch between chunks and embeddings count")
                return False
            
            # Update database with embeddings
            with self.db_service.get_session() as session:
                for chunk, embedding in zip(chunks, embeddings):
                    # Convert embedding to PostgreSQL vector format
                    embedding_str = f"[{','.join(map(str, embedding))}]"
                    
                    # Update the chunk with embedding
                    session.execute(
                        text("""
                            UPDATE document_embeddings 
                            SET embedding = :embedding::vector 
                            WHERE id = :chunk_id
                        """),
                        {
                            "embedding": embedding_str,
                            "chunk_id": chunk.id
                        }
                    )
                
                session.commit()
                return True
                
        except Exception as e:
            print(f"Error updating chunk embeddings: {e}")
            return False
    
    def search_similar_chunks(self, query: str, knowledge_base_name: str = None, limit: int = 5) -> List[Dict[str, Any]]:
        """Search for similar chunks using vector similarity"""
        try:
            # Create embedding for query
            query_embedding = self.create_embedding_for_text(query)
            if not query_embedding:
                return []
            
            # Convert to PostgreSQL vector format
            embedding_str = f"[{','.join(map(str, query_embedding))}]"
            
            # Build search query
            search_query = """
                SELECT 
                    de.id,
                    de.chunk_text,
                    de.metadata,
                    de.chunk_index,
                    d.filename,
                    d.file_type,
                    1 - (de.embedding <=> :embedding::vector) as similarity
                FROM document_embeddings de
                JOIN documents d ON de.document_id = d.id
                WHERE de.embedding IS NOT NULL
            """
            
            params = {"embedding": embedding_str}
            
            # Add knowledge base filter if specified
            if knowledge_base_name:
                search_query += " AND d.metadata::jsonb->>'knowledge_base' = :kb_name"
                params["kb_name"] = knowledge_base_name
            
            search_query += """
                ORDER BY de.embedding <=> :embedding::vector
                LIMIT :limit
            """
            params["limit"] = limit
            
            # Execute search
            with self.db_service.get_session() as session:
                result = session.execute(text(search_query), params)
                rows = result.fetchall()
                
                return [
                    {
                        "id": str(row.id),
                        "chunk_text": row.chunk_text,
                        "metadata": json.loads(row.metadata) if row.metadata else {},
                        "chunk_index": row.chunk_index,
                        "filename": row.filename,
                        "file_type": row.file_type,
                        "similarity": float(row.similarity)
                    }
                    for row in rows
                ]
                
        except Exception as e:
            print(f"Error searching similar chunks: {e}")
            return []
    
    def get_chunks_without_embeddings(self, knowledge_base_name: str = None) -> List[DocumentEmbedding]:
        """Get chunks that don't have embeddings yet"""
        with self.db_service.get_session() as session:
            query = session.query(DocumentEmbedding).filter(
                DocumentEmbedding.embedding.is_(None)
            )
            
            if knowledge_base_name:
                # Join with documents to filter by knowledge base
                query = query.join(Document).filter(
                    Document.metadata.contains(f'"knowledge_base": "{knowledge_base_name}"')
                )
            
            return query.all()
    
    def process_pending_embeddings(self, knowledge_base_name: str = None, batch_size: int = 100) -> int:
        """Process all pending embeddings in batches"""
        try:
            chunks_without_embeddings = self.get_chunks_without_embeddings(knowledge_base_name)
            
            if not chunks_without_embeddings:
                return 0
            
            processed_count = 0
            
            # Process in batches
            for i in range(0, len(chunks_without_embeddings), batch_size):
                batch = chunks_without_embeddings[i:i + batch_size]
                
                if self.update_chunk_embeddings(batch):
                    processed_count += len(batch)
                    print(f"Processed {len(batch)} embeddings")
                else:
                    print(f"Failed to process batch {i//batch_size + 1}")
            
            return processed_count
            
        except Exception as e:
            print(f"Error processing pending embeddings: {e}")
            return 0
    
    def get_embedding_stats(self, knowledge_base_name: str = None) -> Dict[str, Any]:
        """Get statistics about embeddings"""
        try:
            with self.db_service.get_session() as session:
                # Total chunks
                total_query = session.query(DocumentEmbedding)
                if knowledge_base_name:
                    total_query = total_query.join(Document).filter(
                        Document.metadata.contains(f'"knowledge_base": "{knowledge_base_name}"')
                    )
                total_chunks = total_query.count()
                
                # Chunks with embeddings
                with_embeddings_query = session.query(DocumentEmbedding).filter(
                    DocumentEmbedding.embedding.is_not(None)
                )
                if knowledge_base_name:
                    with_embeddings_query = with_embeddings_query.join(Document).filter(
                        Document.metadata.contains(f'"knowledge_base": "{knowledge_base_name}"')
                    )
                chunks_with_embeddings = with_embeddings_query.count()
                
                # Chunks without embeddings
                chunks_without_embeddings = total_chunks - chunks_with_embeddings
                
                return {
                    "total_chunks": total_chunks,
                    "chunks_with_embeddings": chunks_with_embeddings,
                    "chunks_without_embeddings": chunks_without_embeddings,
                    "completion_percentage": (chunks_with_embeddings / total_chunks * 100) if total_chunks > 0 else 0
                }
                
        except Exception as e:
            print(f"Error getting embedding stats: {e}")
            return {
                "total_chunks": 0,
                "chunks_with_embeddings": 0,
                "chunks_without_embeddings": 0,
                "completion_percentage": 0
            }