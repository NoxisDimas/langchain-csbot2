#!/usr/bin/env python3
"""
Database setup script for RAG system
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import ProgrammingError
from app.config import get_settings
from app.services.database_service import DatabaseService

def setup_database():
    """Setup database and create initial schema"""
    settings = get_settings()
    
    print("🚀 Setting up RAG Database...")
    
    try:
        # Create database service
        db_service = DatabaseService()
        
        # Test connection
        print("📡 Testing database connection...")
        with db_service.get_session() as session:
            session.execute(text("SELECT 1"))
        print("✅ Database connection successful")
        
        # Create vector extension
        print("🔧 Creating pgvector extension...")
        if db_service.create_vector_extension():
            print("✅ pgvector extension created/verified")
        else:
            print("❌ Failed to create pgvector extension")
            return False
        
        # Create default schema and tables
        print("🏗️ Creating default schema and tables...")
        if db_service.create_tables("public"):
            print("✅ Default schema and tables created")
        else:
            print("❌ Failed to create default schema")
            return False
        
        # Create default knowledge base
        print("📚 Creating default knowledge base...")
        default_kb = db_service.create_knowledge_base("default", "Default knowledge base for documents")
        if default_kb:
            print(f"✅ Default knowledge base created: {default_kb.name}")
        else:
            print("❌ Failed to create default knowledge base")
            return False
        
        print("\n🎉 Database setup completed successfully!")
        print("\n📋 Summary:")
        print(f"   - Database URL: {settings.database_url}")
        print(f"   - Default Knowledge Base: {default_kb.name if default_kb else 'None'}")
        print(f"   - Schema: {default_kb.schema_name if default_kb else 'None'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        return False

def check_database_status():
    """Check database status and configuration"""
    settings = get_settings()
    
    print("🔍 Checking database status...")
    
    try:
        db_service = DatabaseService()
        
        # Check connection
        with db_service.get_session() as session:
            result = session.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"✅ PostgreSQL Version: {version}")
        
        # Check pgvector extension
        with db_service.get_session() as session:
            result = session.execute(text("SELECT extname FROM pg_extension WHERE extname = 'vector'"))
            if result.fetchone():
                print("✅ pgvector extension is installed")
            else:
                print("❌ pgvector extension is not installed")
        
        # List knowledge bases
        kbs = db_service.list_knowledge_bases()
        print(f"📚 Knowledge Bases: {len(kbs)}")
        for kb in kbs:
            print(f"   - {kb.name} (schema: {kb.schema_name})")
        
        # Vectorstore stats
        from app.services.vectorstore_service import VectorStoreService
        vs = VectorStoreService()
        stats = vs.get_collection_stats()
        print(f"📦 Vectorstore: collection={stats.get('collection')} total_vectors={stats.get('total_vectors')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Database check failed: {e}")
        return False

def main():
    """Main function"""
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "setup":
            success = setup_database()
            sys.exit(0 if success else 1)
        elif command == "status":
            success = check_database_status()
            sys.exit(0 if success else 1)
        else:
            print(f"Unknown command: {command}")
            print("Available commands: setup, status")
            sys.exit(1)
    else:
        print("RAG Database Setup Script")
        print("\nUsage:")
        print("  python setup_database.py setup   - Setup database and create initial schema")
        print("  python setup_database.py status  - Check database status")
        print("\nEnvironment Variables:")
        print("  DATABASE_URL - PostgreSQL connection string")
        print("  OPENAI_API_KEY - OpenAI API key for embeddings")
        print("  OLLAMA_BASE_URL - Ollama base URL (optional)")

if __name__ == "__main__":
    main()