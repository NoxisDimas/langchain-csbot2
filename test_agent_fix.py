#!/usr/bin/env python3
"""
Test script untuk memverifikasi perbaikan OutputParserException
"""

import os
import sys
import requests
import json
import time
from pathlib import Path

# Add app to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

class AgentFixTester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.api_base = f"{base_url}/api"
        
    def test_simple_greeting(self):
        """Test dengan greeting sederhana"""
        print("🔍 Testing simple greeting...")
        try:
            response = requests.post(f"{self.api_base}/chat", json={
                "session_id": "test_greeting",
                "message": "halo",
                "channel": "web"
            })
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Greeting test passed: {result.get('answer', '')}")
                return True
            else:
                print(f"❌ Greeting test failed: {response.status_code}")
                print(f"Error: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Greeting test error: {e}")
            return False
    
    def test_complex_query(self):
        """Test dengan query kompleks yang sebelumnya error"""
        print("🔍 Testing complex query...")
        try:
            response = requests.post(f"{self.api_base}/chat", json={
                "session_id": "test_complex",
                "message": "Apa arti halo dalam bahasa Inggris?",
                "channel": "web"
            })
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Complex query test passed: {result.get('answer', '')}")
                return True
            else:
                print(f"❌ Complex query test failed: {response.status_code}")
                print(f"Error: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Complex query test error: {e}")
            return False
    
    def test_order_status_query(self):
        """Test dengan query status pesanan"""
        print("🔍 Testing order status query...")
        try:
            response = requests.post(f"{self.api_base}/chat", json={
                "session_id": "test_order",
                "message": "Bagaimana status pesanan saya?",
                "channel": "web"
            })
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Order status test passed: {result.get('answer', '')}")
                return True
            else:
                print(f"❌ Order status test failed: {response.status_code}")
                print(f"Error: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Order status test error: {e}")
            return False
    
    def test_product_recommendation(self):
        """Test dengan query rekomendasi produk"""
        print("🔍 Testing product recommendation...")
        try:
            response = requests.post(f"{self.api_base}/chat", json={
                "session_id": "test_product",
                "message": "Saya mencari laptop untuk gaming",
                "channel": "web"
            })
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Product recommendation test passed: {result.get('answer', '')}")
                return True
            else:
                print(f"❌ Product recommendation test failed: {response.status_code}")
                print(f"Error: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Product recommendation test error: {e}")
            return False
    
    def test_edge_cases(self):
        """Test dengan edge cases"""
        print("🔍 Testing edge cases...")
        test_cases = [
            ("", "Empty message"),
            ("a" * 2000, "Very long message"),
            ("Hello! How are you? Can you help me with my order #12345?", "Mixed language and order ID"),
            ("Terima kasih banyak atas bantuannya", "Thank you message"),
        ]
        
        results = []
        for message, description in test_cases:
            try:
                response = requests.post(f"{self.api_base}/chat", json={
                    "session_id": f"test_edge_{hash(message)}",
                    "message": message,
                    "channel": "web"
                })
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ {description}: {result.get('answer', '')[:50]}...")
                    results.append(True)
                else:
                    print(f"❌ {description} failed: {response.status_code}")
                    results.append(False)
            except Exception as e:
                print(f"❌ {description} error: {e}")
                results.append(False)
        
        return all(results)
    
    def test_conversation_flow(self):
        """Test alur percakapan"""
        print("🔍 Testing conversation flow...")
        try:
            session_id = f"test_flow_{int(time.time())}"
            
            # First message
            response1 = requests.post(f"{self.api_base}/chat", json={
                "session_id": session_id,
                "message": "halo",
                "channel": "web"
            })
            
            if response1.status_code != 200:
                print(f"❌ First message failed: {response1.status_code}")
                return False
            
            # Second message
            response2 = requests.post(f"{self.api_base}/chat", json={
                "session_id": session_id,
                "message": "terima kasih",
                "channel": "web"
            })
            
            if response2.status_code == 200:
                result = response2.json()
                print(f"✅ Conversation flow test passed: {result.get('answer', '')}")
                return True
            else:
                print(f"❌ Second message failed: {response2.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Conversation flow test error: {e}")
            return False
    
    def run_all_tests(self):
        """Run semua test"""
        print("🚀 Starting Agent Fix Tests...")
        print("=" * 50)
        
        tests = [
            ("Simple Greeting", self.test_simple_greeting),
            ("Complex Query", self.test_complex_query),
            ("Order Status", self.test_order_status_query),
            ("Product Recommendation", self.test_product_recommendation),
            ("Edge Cases", self.test_edge_cases),
            ("Conversation Flow", self.test_conversation_flow),
        ]
        
        results = []
        for test_name, test_func in tests:
            print(f"\n📋 Running {test_name} test...")
            try:
                result = test_func()
                results.append((test_name, result))
                if result:
                    print(f"✅ {test_name} test PASSED")
                else:
                    print(f"❌ {test_name} test FAILED")
            except Exception as e:
                print(f"❌ {test_name} test ERROR: {e}")
                results.append((test_name, False))
        
        print("\n" + "=" * 50)
        print("📊 Test Results Summary:")
        print("=" * 50)
        
        passed = 0
        total = len(results)
        
        for test_name, result in results:
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{test_name}: {status}")
            if result:
                passed += 1
        
        print(f"\nOverall: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! Agent fix is working correctly.")
            return True
        else:
            print("⚠️  Some tests failed. Please check the implementation.")
            return False


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Agent OutputParserException fix")
    parser.add_argument("--base-url", default="http://localhost:8000", 
                       help="Base URL for the API (default: http://localhost:8000)")
    parser.add_argument("--test", choices=["greeting", "complex", "order", "product", "edge", "flow", "all"],
                       default="all", help="Specific test to run (default: all)")
    
    args = parser.parse_args()
    
    tester = AgentFixTester(args.base_url)
    
    if args.test == "all":
        success = tester.run_all_tests()
        sys.exit(0 if success else 1)
    elif args.test == "greeting":
        success = tester.test_simple_greeting()
    elif args.test == "complex":
        success = tester.test_complex_query()
    elif args.test == "order":
        success = tester.test_order_status_query()
    elif args.test == "product":
        success = tester.test_product_recommendation()
    elif args.test == "edge":
        success = tester.test_edge_cases()
    elif args.test == "flow":
        success = tester.test_conversation_flow()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()