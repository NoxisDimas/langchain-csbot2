#!/usr/bin/env python3
"""
Script untuk upload file yang sudah ada di folder uploads ke RAG system
"""

import os
import sys
from pathlib import Path

# Add app to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def upload_existing_files():
    """Upload file yang sudah ada di folder uploads"""
    print("🚀 Uploading existing files to RAG system...")
    
    try:
        from app.services.document_service import DocumentService
        from app.services.vectorstore_service import VectorStoreService
        from app.config import get_settings
        
        settings = get_settings()
        ds = DocumentService()
        vs = VectorStoreService()
        
        uploads_dir = Path("uploads")
        if not uploads_dir.exists():
            print("❌ Uploads directory not found!")
            return False
        
        # Get all files in uploads directory
        files = list(uploads_dir.glob("*"))
        if not files:
            print("❌ No files found in uploads directory!")
            return False
        
        print(f"📁 Found {len(files)} files in uploads directory")
        
        total_uploaded = 0
        
        for file_path in files:
            if file_path.is_file():
                print(f"\n📄 Processing {file_path.name}...")
                
                try:
                    # Read file content
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    if not content.strip():
                        print(f"   ⚠️ File {file_path.name} is empty, skipping...")
                        continue
                    
                    # Process document
                    chunks = ds.chunk_text(content, {'filename': file_path.name})
                    print(f"   ✅ Created {len(chunks)} chunks")
                    
                    if not chunks:
                        print(f"   ⚠️ No chunks created for {file_path.name}, skipping...")
                        continue
                    
                    # Upload ke vector store
                    ids = vs.add_documents(chunks, collection_name=settings.DB_SCHEMA)
                    print(f"   ✅ Uploaded {len(ids)} documents to collection '{settings.DB_SCHEMA}'")
                    
                    total_uploaded += len(ids)
                    
                except Exception as e:
                    print(f"   ❌ Error processing {file_path.name}: {e}")
                    continue
        
        print(f"\n🎉 Upload completed! Total documents uploaded: {total_uploaded}")
        
        # Test retrieval
        print("\n🧪 Testing retrieval...")
        from app.services.rag.retriever import retrieve_knowledge
        
        test_queries = [
            "metode pembayaran",
            "loyalty program",
            "shipping",
            "return policy"
        ]
        
        for query in test_queries:
            result = retrieve_knowledge(query)
            print(f"   Query: '{query}' -> Found {len(result)} documents")
            if result:
                print(f"      First doc: {result[0].page_content[:50]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Upload error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function"""
    print("🚀 Existing Files Upload Script")
    print("=" * 50)
    
    if upload_existing_files():
        print("\n✅ Upload completed successfully!")
        print("🎯 RAG system now has data from existing files!")
    else:
        print("\n❌ Upload failed!")
        print("🔧 Please check your files and database connection.")

if __name__ == "__main__":
    main()