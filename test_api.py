import requests
import json

def test_api():
    base_url = "http://localhost:8000"
    
    print("🧪 Testing API Endpoints...")
    
    # Test health check
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
        else:
            print("❌ Health check failed")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return
    
    # Test query endpoint
    try:
        query_data = {
            "question": "What are the latest AI developments?",
            "top_k": 3,
            "score_threshold": 0.2
        }
        
        response = requests.post(f"{base_url}/query", json=query_data)
        if response.status_code == 200:
            print("✅ Query endpoint working")
            result = response.json()
            print(f"   Answer preview: {result['answer'][:100]}...")
        else:
            print(f"❌ Query failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Query error: {e}")
    
    # Test stats
    try:
        response = requests.get(f"{base_url}/stats")
        if response.status_code == 200:
            print("✅ Stats endpoint working")
            print(f"   Stats: {response.json()}")
        else:
            print(f"❌ Stats failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Stats error: {e}")

if __name__ == "__main__":
    test_api()
