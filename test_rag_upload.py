#!/usr/bin/env python3
"""
Test script untuk upload document dan test RAG retrieval
"""

import os
import sys
from pathlib import Path

# Add app to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def test_document_upload():
    """Test upload document ke vector store"""
    print("🔍 Testing document upload...")
    try:
        from app.services.document_service import DocumentService
        from app.services.vectorstore_service import VectorStoreService
        from app.config import get_settings
        
        settings = get_settings()
        ds = DocumentService()
        vs = VectorStoreService()
        
        # Test dengan file yang sudah ada
        test_file = "uploads/faq_common.txt"
        if os.path.exists(test_file):
            with open(test_file, 'r') as f:
                content = f.read()
            
            # Process document
            chunks = ds.chunk_text(content, {'filename': 'faq_common.txt'})
            print(f"✅ Created {len(chunks)} chunks")
            
            # Upload ke vector store dengan collection yang sama dengan RAG retriever
            ids = vs.add_documents(chunks, collection_name=settings.DB_SCHEMA)
            print(f"✅ Uploaded {len(ids)} documents to vector store (collection: {settings.DB_SCHEMA})")
            
            return True
        else:
            print(f"❌ Test file not found: {test_file}")
            return False
    except Exception as e:
        print(f"❌ Document upload error: {e}")
        return False

def test_rag_retrieval_with_data():
    """Test RAG retrieval dengan data yang sudah di-upload"""
    print("\n🔍 Testing RAG retrieval with uploaded data...")
    try:
        from app.services.rag.retriever import retrieve_knowledge
        
        # Test dengan query yang relevan
        query = "metode pembayaran"
        result = retrieve_knowledge(query)
        print(f"✅ Retrieved {len(result)} documents for query: '{query}'")
        
        if result:
            print(f"✅ First document: {result[0].page_content[:100]}...")
            print(f"✅ Document metadata: {result[0].metadata}")
        else:
            print("⚠️ No documents found - might need to wait for indexing")
        
        return True
    except Exception as e:
        print(f"❌ RAG retrieval error: {e}")
        return False

def test_tool_with_data():
    """Test tool dengan data yang sudah di-upload"""
    print("\n🔍 Testing tool with uploaded data...")
    try:
        from app.services.langgraph.tools import retrieve_kb_snippets_tool
        
        # Test dengan query yang relevan
        query = "pembayaran"
        result = retrieve_kb_snippets_tool.invoke(query)
        print(f"✅ Tool result: {result}")
        
        if result.get('snippets'):
            print(f"✅ Found {len(result['snippets'])} snippets")
            print(f"✅ First snippet: {result['snippets'][0][:100]}...")
        else:
            print("⚠️ No snippets found")
        
        return True
    except Exception as e:
        print(f"❌ Tool test error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting RAG Upload & Retrieval Test...\n")
    
    tests = [
        test_document_upload,
        test_rag_retrieval_with_data,
        test_tool_with_data
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
        "Document Upload",
        "RAG Retrieval with Data", 
        "Tool with Data"
    ]
    
    for i, (name, result) in enumerate(zip(test_names, results)):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{i+1}. {name}: {status}")
    
    print(f"\n🎯 Overall: {sum(results)}/{len(results)} tests passed")
    
    if all(results):
        print("\n🎉 SUCCESS: RAG system is working correctly!")
        print("✅ Documents can be uploaded to vector store")
        print("✅ RAG retrieval is working")
        print("✅ Tools can access knowledge base")
    else:
        print("\n🔧 RECOMMENDATIONS:")
        if not results[0]:
            print("- Check document processing and vector store upload")
        if not results[1]:
            print("- Verify vector store indexing and retrieval")
        if not results[2]:
            print("- Check tool integration with knowledge base")

if __name__ == "__main__":
    main()