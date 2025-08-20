#!/usr/bin/env python3
"""
Debug script untuk mengidentifikasi masalah RAG system
"""

import os
import sys
from pathlib import Path

# Add app to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def test_config():
    """Test konfigurasi environment"""
    print("🔍 Testing configuration...")
    try:
        from app.config import get_settings
        settings = get_settings()
        print(f"✅ DATABASE_URL: {settings.DATABASE_URL}")
        print(f"✅ DB_SCHEMA: {settings.DB_SCHEMA}")
        print(f"✅ OPENAI_API_KEY: {bool(settings.OPENAI_API_KEY and settings.OPENAI_API_KEY.strip())}")
        print(f"✅ OLLAMA_BASE_URL: {settings.OLLAMA_BASE_URL}")
        print(f"✅ GROQ_API_KEY: {bool(settings.GROQ_API_KEY and settings.GROQ_API_KEY.strip())}")
        return True
    except Exception as e:
        print(f"❌ Config error: {e}")
        return False

def test_embedding_model():
    """Test embedding model"""
    print("\n🔍 Testing embedding model...")
    try:
        from app.services.llm.provider import get_embedding_model
        embeddings = get_embedding_model()
        print(f"✅ Embedding model: {type(embeddings).__name__}")
        
        # Test embedding
        test_text = "test query"
        vector = embeddings.embed_query(test_text)
        print(f"✅ Embedding created: {len(vector)} dimensions")
        return True
    except Exception as e:
        print(f"❌ Embedding error: {e}")
        return False

def test_document_processing():
    """Test document processing"""
    print("\n🔍 Testing document processing...")
    try:
        from app.services.document_service import DocumentService
        ds = DocumentService()
        
        # Test with existing file
        test_file = "uploads/faq_common.txt"
        if os.path.exists(test_file):
            with open(test_file, 'r') as f:
                content = f.read()
            
            chunks = ds.chunk_text(content, {'filename': 'faq_common.txt'})
            print(f"✅ Created {len(chunks)} chunks")
            print(f"✅ First chunk: {chunks[0].page_content[:50]}...")
            return True
        else:
            print(f"❌ Test file not found: {test_file}")
            return False
    except Exception as e:
        print(f"❌ Document processing error: {e}")
        return False

def test_vectorstore_connection():
    """Test vectorstore connection"""
    print("\n🔍 Testing vectorstore connection...")
    try:
        from app.services.rag.retriever import _get_vectorstore
        vs = _get_vectorstore()
        if vs is None:
            print("❌ Vectorstore is None - likely database connection issue")
            return False
        print(f"✅ Vectorstore created: {type(vs).__name__}")
        return True
    except Exception as e:
        print(f"❌ Vectorstore error: {e}")
        return False

def test_rag_retrieval():
    """Test RAG retrieval"""
    print("\n🔍 Testing RAG retrieval...")
    try:
        from app.services.rag.retriever import retrieve_knowledge
        result = retrieve_knowledge("test query")
        print(f"✅ Retrieved {len(result)} documents")
        if result:
            print(f"✅ First document: {result[0].page_content[:100]}...")
        else:
            print("⚠️ No documents found - this might be expected if no data is ingested")
        return True
    except Exception as e:
        print(f"❌ RAG retrieval error: {e}")
        return False

def test_tool_integration():
    """Test tool integration"""
    print("\n🔍 Testing tool integration...")
    try:
        from app.services.langgraph.tools import retrieve_kb_snippets_tool
        result = retrieve_kb_snippets_tool("test query")
        print(f"✅ Tool result: {result}")
        return True
    except Exception as e:
        print(f"❌ Tool integration error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting RAG System Debug...\n")
    
    tests = [
        test_config,
        test_embedding_model,
        test_document_processing,
        test_vectorstore_connection,
        test_rag_retrieval,
        test_tool_integration
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append(False)
    
    print("\n" + "="*50)
    print("📊 SUMMARY:")
    print("="*50)
    
    test_names = [
        "Configuration",
        "Embedding Model", 
        "Document Processing",
        "Vectorstore Connection",
        "RAG Retrieval",
        "Tool Integration"
    ]
    
    for i, (name, result) in enumerate(zip(test_names, results)):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{i+1}. {name}: {status}")
    
    print(f"\n🎯 Overall: {sum(results)}/{len(results)} tests passed")
    
    if not all(results):
        print("\n🔧 RECOMMENDATIONS:")
        if not results[0]:
            print("- Check .env file configuration")
        if not results[1]:
            print("- Verify LLM provider settings (OpenAI/Ollama/Groq)")
        if not results[2]:
            print("- Check document processing dependencies")
        if not results[3]:
            print("- Ensure PostgreSQL is running and accessible")
            print("- Verify DATABASE_URL in .env file")
        if not results[4]:
            print("- Check if documents have been ingested to vectorstore")
        if not results[5]:
            print("- Verify tool dependencies and imports")

if __name__ == "__main__":
    main()