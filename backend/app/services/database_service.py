import os
import json
from typing import Optional, List, Dict, Any
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import ProgrammingError
from app.config import get_settings
from app.persistence.models import Base, Document, DocumentEmbedding, KnowledgeBase
import uuid

settings = get_settings()

class DatabaseService:
    def __init__(self):
        self.engine = create_engine(settings.database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.inspector = inspect(self.engine)
    
    def get_session(self):
        return self.SessionLocal()
    
    def check_schema_exists(self, schema_name: str) -> bool:
        """Check if a schema exists in the database"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(
                    "SELECT schema_name FROM information_schema.schemata WHERE schema_name = :schema_name"
                ), {"schema_name": schema_name})
                return result.fetchone() is not None
        except Exception as e:
            print(f"Error checking schema existence: {e}")
            return False
    
    def create_schema(self, schema_name: str) -> bool:
        """Create a new schema in the database"""
        try:
            with self.engine.connect() as conn:
                conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema_name}"))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error creating schema: {e}")
            return False
    
    def create_vector_extension(self) -> bool:
        """Create pgvector extension if it doesn't exist"""
        try:
            with self.engine.connect() as conn:
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error creating vector extension: {e}")
            return False
    
    def create_tables(self, schema_name: str = "public") -> bool:
        """Create tables in the specified schema"""
        try:
            # Create schema if it doesn't exist
            if not self.check_schema_exists(schema_name):
                if not self.create_schema(schema_name):
                    return False
            
            # Create vector extension
            if not self.create_vector_extension():
                return False
            
            # Create tables with schema prefix
            metadata = Base.metadata
            for table in metadata.tables.values():
                table.schema = schema_name
            
            metadata.create_all(bind=self.engine)
            return True
        except Exception as e:
            print(f"Error creating tables: {e}")
            return False
    
    def get_knowledge_base(self, name: str) -> Optional[KnowledgeBase]:
        """Get knowledge base by name"""
        with self.get_session() as session:
            return session.query(KnowledgeBase).filter(KnowledgeBase.name == name).first()
    
    def create_knowledge_base(self, name: str, description: str = None) -> Optional[KnowledgeBase]:
        """Create a new knowledge base"""
        try:
            schema_name = f"kb_{name.lower().replace(' ', '_')}"
            
            # Check if knowledge base already exists
            existing_kb = self.get_knowledge_base(name)
            if existing_kb:
                return existing_kb
            
            # Create schema and tables
            if not self.create_tables(schema_name):
                return None
            
            # Create knowledge base record
            with self.get_session() as session:
                kb = KnowledgeBase(
                    name=name,
                    description=description,
                    schema_name=schema_name
                )
                session.add(kb)
                session.commit()
                session.refresh(kb)
                return kb
        except Exception as e:
            print(f"Error creating knowledge base: {e}")
            return None
    
    def list_knowledge_bases(self) -> List[KnowledgeBase]:
        """List all knowledge bases"""
        with self.get_session() as session:
            return session.query(KnowledgeBase).filter(KnowledgeBase.is_active == True).all()
    
    def delete_knowledge_base(self, name: str) -> bool:
        """Delete a knowledge base and its schema"""
        try:
            with self.get_session() as session:
                kb = session.query(KnowledgeBase).filter(KnowledgeBase.name == name).first()
                if not kb:
                    return False
                
                # Drop schema
                with self.engine.connect() as conn:
                    conn.execute(text(f"DROP SCHEMA IF EXISTS {kb.schema_name} CASCADE"))
                    conn.commit()
                
                # Delete knowledge base record
                session.delete(kb)
                session.commit()
                return True
        except Exception as e:
            print(f"Error deleting knowledge base: {e}")
            return False
    
    def get_documents(self, knowledge_base_name: str = None) -> List[Document]:
        """Get documents, optionally filtered by knowledge base"""
        with self.get_session() as session:
            query = session.query(Document)
            if knowledge_base_name:
                kb = self.get_knowledge_base(knowledge_base_name)
                if kb:
                    # This would need to be implemented based on your schema structure
                    pass
            return query.all()
    
    def get_document_by_id(self, document_id: str) -> Optional[Document]:
        """Get document by ID"""
        with self.get_session() as session:
            return session.query(Document).filter(Document.id == document_id).first()
    
    def delete_document(self, document_id: str) -> bool:
        """Delete a document and its embeddings"""
        try:
            with self.get_session() as session:
                document = session.query(Document).filter(Document.id == document_id).first()
                if not document:
                    return False
                
                # Delete file from filesystem
                if os.path.exists(document.file_path):
                    os.remove(document.file_path)
                
                # Delete document and related embeddings
                session.delete(document)
                session.commit()
                return True
        except Exception as e:
            print(f"Error deleting document: {e}")
            return False