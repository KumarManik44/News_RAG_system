import os
import sys

# Add current directory to Python path
sys.path.insert(0, os.getcwd())

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting Intelligent News Summarizer API...")
    print("📍 Project directory:", os.getcwd())
    print("🌐 API will be available at: http://localhost:8000")
    print("📚 API docs at: http://localhost:8000/docs")
    
    # Start the FastAPI server
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
