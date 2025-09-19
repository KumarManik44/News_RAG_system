import requests
import time

def test_connection():
    api_url = "http://localhost:8000"
    
    print("🔍 Testing API Connection...")
    print(f"API URL: {api_url}")
    
    try:
        # Test basic connectivity
        response = requests.get(f"{api_url}/", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API is working!")
            print(f"   Status: {data.get('status')}")
            print(f"   Message: {data.get('message')}")
            print(f"   Version: {data.get('version')}")
            
            # Test query endpoint
            print("\n🧪 Testing query endpoint...")
            query_response = requests.post(f"{api_url}/query", 
                json={"question": "test question"}, 
                timeout=10)
            
            if query_response.status_code == 200:
                print("✅ Query endpoint working!")
            else:
                print(f"❌ Query endpoint failed: {query_response.status_code}")
            
            return True
        else:
            print(f"❌ API returned status code: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed - API server not running")
        print("\n💡 To fix:")
        print("   1. Run: python start_api.py")
        print("   2. Wait for 'Uvicorn running on http://0.0.0.0:8000'")
        print("   3. Try this test again")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    if test_connection():
        print("\n🎉 Connection test passed!")
        print("🚀 You can now run Streamlit: streamlit run ui/streamlit_app.py")
    else:
        print("\n⚠️  Connection test failed!")
