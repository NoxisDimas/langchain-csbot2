#!/usr/bin/env python3
"""
Test script for the new RAG system
"""

import os
import sys
import requests
import json
import time
from pathlib import Path

# Add app to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

class NewRAGSystemTester:
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
    
    def test_file_upload(self, test_file_path):
        """Test file upload"""
        print(f"🔍 Testing file upload: {test_file_path}")
        try:
            with open(test_file_path, 'rb') as f:
                files = {'file': f}
                response = requests.post(f"{self.api_base}/upload", files=files)
                
            if response.status_code == 200:
                result = response.json()
                print(f"✅ File upload successful: {result}")
                return True
            else:
                print(f"❌ File upload failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ File upload error: {e}")
            return False
    
    def test_list_files(self):
        """Test file listing"""
        print("🔍 Testing file listing...")
        try:
            response = requests.get(f"{self.api_base}/files")
            if response.status_code == 200:
                files = response.json()
                print(f"✅ Found {len(files.get('files', []))} files")
                return True
            else:
                print(f"❌ File listing failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ File listing error: {e}")
            return False
    
    def test_ingestion(self):
        """Test document ingestion"""
        print("🔍 Testing document ingestion...")
        try:
            response = requests.post(f"{self.api_base}/ingest", params={"update_existing": True})
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Ingestion successful: {result}")
                return True
            else:
                print(f"❌ Ingestion failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Ingestion error: {e}")
            return False
    
    def test_search(self, query="test query"):
        """Test search functionality"""
        print(f"🔍 Testing search with query: {query}")
        try:
            search_data = {
                "query": query,
                "limit": 5
            }
            response = requests.post(f"{self.api_base}/search", json=search_data)
            if response.status_code == 200:
                results = response.json()
                print(f"✅ Search returned {len(results)} results")
                return True
            else:
                print(f"❌ Search failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Search error: {e}")
            return False
    
    def test_filter(self, key="category", value="txt file"):
        """Test filter functionality"""
        print(f"🔍 Testing filter with {key}={value}")
        try:
            response = requests.get(f"{self.api_base}/search/filter", params={
                "key": key,
                "value": value,
                "k": 10
            })
            if response.status_code == 200:
                results = response.json()
                print(f"✅ Filter returned {len(results.get('results', []))} results")
                return True
            else:
                print(f"❌ Filter failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Filter error: {e}")
            return False
    
    def create_test_file(self, filename="test_document.txt", content="This is a test document for RAG system testing."):
        """Create a test file in uploads folder"""
        uploads_dir = os.path.join(os.path.dirname(__file__), "uploads")
        os.makedirs(uploads_dir, exist_ok=True)
        
        file_path = os.path.join(uploads_dir, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Created test file: {file_path}")
        return file_path
    
    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting new RAG system tests...")
        
        # Test 1: Health check
        if not self.test_health():
            print("❌ Health check failed, stopping tests")
            return False
        
        # Test 2: Stats
        self.test_stats()
        
        # Test 3: Create and upload test file
        test_file = self.create_test_file()
        if not self.test_file_upload(test_file):
            print("❌ File upload failed, stopping tests")
            return False
        
        # Test 4: List files
        self.test_list_files()
        
        # Test 5: Ingestion
        if not self.test_ingestion():
            print("❌ Ingestion failed, stopping tests")
            return False
        
        # Wait a bit for ingestion to complete
        time.sleep(2)
        
        # Test 6: Search
        if not self.test_search("test document"):
            print("❌ Search failed")
            return False
        
        # Test 7: Filter
        self.test_filter("category", "txt file")
        
        print("✅ All tests completed successfully!")
        return True

def main():
    tester = NewRAGSystemTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 New RAG system is working correctly!")
    else:
        print("\n❌ Some tests failed. Please check the logs above.")
        sys.exit(1)

if __name__ == "__main__":
    main()