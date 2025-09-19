import subprocess
import time
import threading
import webbrowser

def run_api():
    """Run FastAPI server"""
    subprocess.run(["python", "api/main.py"])

def run_ui():
    """Run Streamlit app"""
    time.sleep(3)  # Wait for API to start
    subprocess.run(["streamlit", "run", "ui/streamlit_app.py", "--server.port", "8501"])

def open_browser():
    """Open browser after delay"""
    time.sleep(5)
    webbrowser.open("http://localhost:8501")

if __name__ == "__main__":
    print("🚀 Starting Intelligent News Summarizer System...")
    
    # Start API server in background
    api_thread = threading.Thread(target=run_api)
    api_thread.daemon = True
    api_thread.start()
    
    print("✅ FastAPI server starting on http://localhost:8000")
    
    # Open browser
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    print("✅ Streamlit UI starting on http://localhost:8501")
    print("🌐 Opening browser automatically...")
    
    # Run Streamlit (blocking)
    run_ui()
