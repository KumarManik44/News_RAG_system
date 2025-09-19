import streamlit as st
import requests
import json
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import pandas as pd
import time

# Configuration - Fixed API URL
API_BASE_URL = "http://localhost:8000"  # Ensure this matches your FastAPI server

# Page config
st.set_page_config(
    page_title="Intelligent News Summarizer",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS (same as before)
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .source-tag {
        background: #e1f5fe;
        padding: 0.2rem 0.5rem;
        border-radius: 1rem;
        font-size: 0.8rem;
        margin: 0.1rem;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)

# Enhanced API call function with better error handling
def call_api(endpoint: str, method: str = "GET", data: dict = None, timeout: int = 10):
    """Make API calls with enhanced error handling and timeout"""
    try:
        url = f"{API_BASE_URL}/{endpoint.lstrip('/')}"
        
        # Add timeout and better error handling
        if method == "GET":
            response = requests.get(url, timeout=timeout)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=timeout)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error {response.status_code}: {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        st.error(f"❌ Cannot connect to API server at {API_BASE_URL}")
        st.info("💡 Make sure the FastAPI server is running: `python start_api.py`")
        return None
    except requests.exceptions.Timeout:
        st.error("⏱️ API request timed out")
        return None
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
        return None

# Main app with better connection status
def main():
    st.markdown('<h1 class="main-header">📰 Intelligent News Summarizer</h1>', unsafe_allow_html=True)
    
    # Sidebar with enhanced connection status
    with st.sidebar:
        st.header("🎛️ Controls")
        
        # API health check with retry
        st.subheader("🔌 Connection Status")
        
        if st.button("🔄 Test Connection"):
            with st.spinner("Testing API connection..."):
                health = call_api("", timeout=5)
                
        health = call_api("", timeout=3)
        if health:
            st.success("✅ API Connected")
            st.caption(f"Version: {health.get('version', 'Unknown')}")
            st.caption(f"Status: {health.get('status', 'Unknown')}")
        else:
            st.error("❌ API Disconnected")
            st.warning("📋 Troubleshooting:")
            st.code("""
# 1. Check if FastAPI is running
python start_api.py

# 2. Verify API is accessible
curl http://localhost:8000

# 3. Check port availability
netstat -an | grep 8000
            """)
        
        st.divider()
        
        # Navigation
        page = st.selectbox(
            "Navigate",
            ["🏠 Dashboard", "❓ Ask Questions", "📊 Trending Topics", "📋 Daily Briefing", "⚙️ System Stats"]
        )
    
    # Main content based on connection status
    if health:  # Only show full interface if API is connected
        if page == "🏠 Dashboard":
            show_dashboard()
        elif page == "❓ Ask Questions":
            show_query_page()
        elif page == "📊 Trending Topics":
            show_trending_page()
        elif page == "📋 Daily Briefing":
            show_briefing_page()
        elif page == "⚙️ System Stats":
            show_stats_page()
    else:
        # Show limited interface when API is disconnected
        st.warning("⚠️ API Server Not Available")
        st.info("""
        **To fix this issue:**
        
        1. **Start the FastAPI server** in a separate terminal:
           ```
           python start_api.py
           ```
        
        2. **Verify the server is running** by visiting: http://localhost:8000
        
        3. **Refresh this page** once the API is running
        """)
        
        # Show basic interface
        st.subheader("🔧 System Information")
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"**Streamlit URL:** {st._config.get_option('server.baseUrlPath') or 'localhost:8502'}")
        with col2:
            st.info(f"**API URL:** {API_BASE_URL}")

# Updated page functions (same logic, better error handling)
def show_dashboard():
    """Dashboard with connection-aware features"""
    st.header("📊 News Analytics Dashboard")
    
    col1, col2, col3 = st.columns(3)
    
    # Get system stats with fallback
    stats = call_api("stats")
    if stats:
        with col1:
            st.metric("Total Articles", stats.get('total_articles', 'N/A'))
        with col2:
            st.metric("Text Chunks", stats.get('total_chunks', 'N/A'))
        with col3:
            st.metric("Embeddings", stats.get('total_embeddings', 'N/A'))
    else:
        st.warning("Unable to load system statistics")
    
    st.divider()
    
    # Quick test queries
    st.subheader("🧪 Test Queries")
    test_queries = [
        "What are the latest AI developments?",
        "How is technology changing business?", 
        "What recent innovations have been announced?"
    ]
    
    for query in test_queries:
        if st.button(f"🔍 {query}", key=query):
            with st.spinner(f"Processing: {query}"):
                result = call_api("query", "POST", {"question": query})
                if result:
                    with st.expander(f"✅ Answer"):
                        st.write(result['answer'][:300] + "...")
                        st.caption(f"Confidence: {result.get('confidence_score', 0):.2f}")

def show_query_page():
    """Enhanced query page with better UX"""
    st.header("❓ Ask About Current News")
    
    question = st.text_area(
        "What would you like to know about current news?",
        placeholder="e.g., What are the latest developments in artificial intelligence?",
        height=100
    )
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        top_k = st.slider("Documents to retrieve", 1, 10, 5)
        score_threshold = st.slider("Confidence threshold", 0.0, 1.0, 0.2)
    
    if st.button("🔍 Get Answer", disabled=not question.strip()):
        with st.spinner("🧠 Analyzing news articles..."):
            result = call_api("query", "POST", {
                "question": question,
                "top_k": top_k,
                "score_threshold": score_threshold
            })
            
            if result:
                st.subheader("📝 Answer")
                st.write(result['answer'])
                
                # Enhanced metrics display
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Confidence", f"{result.get('confidence_score', 0):.2%}")
                with col2:
                    st.metric("Sources", len(result.get('sources', [])))
                with col3:
                    st.metric("Documents", result.get('retrieved_documents', 0))
                with col4:
                    st.metric("Response Time", f"{result.get('processing_time_ms', 0):.0f}ms")
                
                # Sources display
                if result.get('sources'):
                    st.subheader("📚 Sources")
                    for source in result['sources']:
                        st.markdown(f'<div class="source-tag">{source}</div>', unsafe_allow_html=True)

# Keep other functions the same but add connection checks
def show_trending_page():
    st.header("📊 Trending News Topics")
    trending = call_api("trending")
    if not trending:
        st.warning("Unable to load trending topics")
        return
        
    # Rest of function same as before...

def show_briefing_page():
    st.header("📋 Daily News Briefing")
    # Same implementation with connection checks...

def show_stats_page():
    st.header("⚙️ System Statistics")
    # Same implementation with connection checks...

if __name__ == "__main__":
    main()
