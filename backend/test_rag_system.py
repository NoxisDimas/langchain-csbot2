#!/usr/bin/env python3
"""
Test script for RAG system
"""

import os
import sys
import requests
import json
from pathlib import Path

# Add app to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.database_service import DatabaseService
from app.services.document_service import DocumentService
from app.services.vectorstore_service import VectorStoreService

class RAGSystemTester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.api_base = f"{base_url}/api/rag"
        
    def test_health(self):
        """Test health endpoint"""
        print("🔍 Testing health endpoint...")
        try:
            response = requests.get(f"{self.api_base}/health")
            if response.status_code == 200:
                print("✅ Health check passed")
                return True
            else:
                print(f"❌ Health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return False
    
    def test_knowledge_base_creation(self):
        """Test knowledge base creation"""
        print("🔍 Testing knowledge base creation...")
        try:
            kb_data = {
                "name": "test_kb",
                "description": "Test knowledge base for testing"
            }
            response = requests.post(f"{self.api_base}/knowledge-bases", json=kb_data)
            if response.status_code == 200:
                print("✅ Knowledge base creation passed")
                return True
            else:
                print(f"❌ Knowledge base creation failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Knowledge base creation error: {e}")
            return False
    
    def test_knowledge_bases_list(self):
        """Test knowledge bases listing"""
        print("🔍 Testing knowledge bases listing...")
        try:
            response = requests.get(f"{self.api_base}/knowledge-bases")
            if response.status_code == 200:
                kbs = response.json()
                print(f"✅ Found {len(kbs)} knowledge bases")
                return True
            else:
                print(f"❌ Knowledge bases listing failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Knowledge bases listing error: {e}")
            return False
    
    def test_stats(self):
        """Test stats endpoint"""
        print("🔍 Testing stats endpoint...")
        try:
            response = requests.get(f"{self.api_base}/stats")
            if response.status_code == 200:
                stats = response.json()
                print(f"✅ Stats: {stats}")
                return True
            else:
                print(f"❌ Stats failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Stats error: {e}")
            return False
    
    def test_search(self):
        """Test search functionality"""
        print("🔍 Testing search functionality...")
        try:
            search_data = {
                "query": "test query",
                "knowledge_base": None,
                "limit": 5
            }
            response = requests.post(f"{self.api_base}/search", json=search_data)
            if response.status_code == 200:
                results = response.json()
                print(f"✅ Search returned {len(results)} results")
                return True
            else:
                print(f"❌ Search failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Search error: {e}")
            return False
    
    def test_database_services(self):
        """Test database services directly"""
        print("🔍 Testing database services...")
        try:
            db_service = DatabaseService()
            
            # Test connection
            with db_service.get_session() as session:
                session.execute("SELECT 1")
            print("✅ Database connection successful")
            
            # Test knowledge base operations
            kb = db_service.get_knowledge_base("default")
            if kb:
                print(f"✅ Found default knowledge base: {kb.name}")
            else:
                print("⚠️ Default knowledge base not found")
            
            return True
        except Exception as e:
            print(f"❌ Database services error: {e}")
            return False
    
    def test_document_services(self):
        """Test document services"""
        print("🔍 Testing document services...")
        try:
            doc_service = DocumentService()
            
            # Test file type detection
            test_files = [
                "test.pdf",
                "test.txt",
                "test.csv",
                "test.docx",
                "test.md"
            ]
            
            for file in test_files:
                is_supported = doc_service.is_supported_file(file)
                print(f"  {file}: {'✅' if is_supported else '❌'}")
            
            return True
        except Exception as e:
            print(f"❌ Document services error: {e}")
            return False
    
    def test_vectorstore_services(self):
        """Test vectorstore services"""
        print("🔍 Testing vectorstore services...")
        try:
            vs = VectorStoreService()
            stats = vs.get_collection_stats()
            print(f"✅ Vectorstore stats: {stats}")
            return True
        except Exception as e:
            print(f"❌ Vectorstore services error: {e}")
            return False
    
    def create_test_file(self):
        """Create a test file for upload testing"""
        test_content = """
        This is a test document for the RAG system.
        
        It contains various topics:
        1. Machine Learning
        2. Natural Language Processing
        3. Vector Databases
        4. Document Processing
        
        This document will be used to test the upload and search functionality
        of the RAG system.
        """
        
        test_file_path = "test_document.txt"
        with open(test_file_path, "w") as f:
            f.write(test_content)
        
        return test_file_path
    
    def test_file_upload(self):
        """Test file upload functionality"""
        print("🔍 Testing file upload...")
        try:
            # Create test file
            test_file_path = self.create_test_file()
            
            # Upload file
            with open(test_file_path, "rb") as f:
                files = {"file": ("test_document.txt", f, "text/plain")}
                data = {"knowledge_base": "default"}
                
                response = requests.post(
                    f"{self.api_base}/upload",
                    files=files,
                    data=data
                )
            
            # Clean up test file
            os.remove(test_file_path)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ File upload successful: {result}")
                return True
            else:
                print(f"❌ File upload failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ File upload error: {e}")
            return False
    
    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting RAG System Tests...")
        print("=" * 50)
        
        tests = [
            ("Health Check", self.test_health),
            ("Database Services", self.test_database_services),
            ("Document Services", self.test_document_services),
            ("Vectorstore Services", self.test_vectorstore_services),
            ("Knowledge Base Creation", self.test_knowledge_base_creation),
            ("Knowledge Bases List", self.test_knowledge_bases_list),
            ("Stats", self.test_stats),
            ("Search", self.test_search),
            ("File Upload", self.test_file_upload),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n📋 Running: {test_name}")
            try:
                if test_func():
                    passed += 1
                else:
                    print(f"❌ {test_name} failed")
            except Exception as e:
                print(f"❌ {test_name} error: {e}")
        
        print("\n" + "=" * 50)
        print(f"📊 Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! RAG system is working correctly.")
        else:
            print("⚠️ Some tests failed. Please check the configuration.")
        
        return passed == total

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test RAG System")
    parser.add_argument("--url", default="http://localhost:8000", help="Base URL for API")
    parser.add_argument("--test", help="Run specific test")
    
    args = parser.parse_args()
    
    tester = RAGSystemTester(args.url)
    
    if args.test:
        # Run specific test
        test_method = getattr(tester, f"test_{args.test}", None)
        if test_method:
            test_method()
        else:
            print(f"Test '{args.test}' not found")
    else:
        # Run all tests
        tester.run_all_tests()

if __name__ == "__main__":
    main()