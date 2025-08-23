#!/usr/bin/env python3
"""
Test script for stats endpoint compatibility
"""

import requests
import json

def test_stats_endpoint():
    """Test the stats endpoint for frontend compatibility"""
    base_url = "http://localhost:8000"
    
    print("🔍 Testing stats endpoint compatibility...")
    
    try:
        # Test main stats endpoint
        response = requests.get(f"{base_url}/api/rag/stats")
        
        if response.status_code == 200:
            stats = response.json()
            print("✅ Stats endpoint working")
            print(f"📊 Response structure:")
            print(json.dumps(stats, indent=2))
            
            # Check if collection property exists
            if "collection" in stats:
                print("✅ Collection property found")
            else:
                print("❌ Collection property missing")
            
            # Check if vectorstore property exists (legacy)
            if "vectorstore" in stats and "collection" in stats["vectorstore"]:
                print("✅ Legacy vectorstore.collection structure found")
            else:
                print("❌ Legacy vectorstore.collection structure missing")
            
            return True
        else:
            print(f"❌ Stats endpoint failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_legacy_stats_endpoint():
    """Test the legacy stats endpoint"""
    base_url = "http://localhost:8000"
    
    print("\n🔍 Testing legacy stats endpoint...")
    
    try:
        response = requests.get(f"{base_url}/api/rag/stats/legacy")
        
        if response.status_code == 200:
            stats = response.json()
            print("✅ Legacy stats endpoint working")
            print(f"📊 Legacy response structure:")
            print(json.dumps(stats, indent=2))
            
            # Check legacy structure
            if "vectorstore" in stats and "collection" in stats["vectorstore"]:
                print("✅ Legacy structure correct")
                return True
            else:
                print("❌ Legacy structure incorrect")
                return False
        else:
            print(f"❌ Legacy stats endpoint failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Legacy test failed: {e}")
        return False

def main():
    print("🚀 Testing Stats Endpoint Compatibility")
    print("=" * 50)
    
    # Test main stats endpoint
    success1 = test_stats_endpoint()
    
    # Test legacy stats endpoint
    success2 = test_legacy_stats_endpoint()
    
    if success1 and success2:
        print("\n🎉 All tests passed! Frontend should work correctly.")
    else:
        print("\n❌ Some tests failed. Please check the logs above.")
        return False
    
    return True

if __name__ == "__main__":
    main()