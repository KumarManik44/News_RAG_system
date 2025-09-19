import streamlit as st
import requests
import json
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import pandas as pd

# Configuration
API_BASE_URL = "http://localhost:8000"  # Change for production

# Page config
st.set_page_config(
    page_title="Intelligent News Summarizer",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
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

# Helper functions
def call_api(endpoint: str, method: str = "GET", data: dict = None):
    """Make API calls with error handling"""
    try:
        url = f"{API_BASE_URL}/{endpoint}"
        
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        st.error("⚠️ Unable to connect to API server. Please ensure the FastAPI server is running.")
        return None
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None

# Main app
def main():
    st.markdown('<h1 class="main-header">📰 Intelligent News Summarizer</h1>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("🎛️ Controls")
        
        # API health check
        health = call_api("")
        if health:
            st.success("✅ API Connected")
            st.caption(f"Version: {health.get('version', 'Unknown')}")
        else:
            st.error("❌ API Disconnected")
        
        st.divider()
        
        # Navigation
        page = st.selectbox(
            "Navigate",
            ["🏠 Dashboard", "❓ Ask Questions", "📊 Trending Topics", "📋 Daily Briefing", "⚙️ System Stats"]
        )
    
    # Main content
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

def show_dashboard():
    """Main dashboard with overview"""
    st.header("📊 News Analytics Dashboard")
    
    col1, col2, col3 = st.columns(3)
    
    # Get system stats
    stats = call_api("stats")
    if stats:
        with col1:
            st.metric("Total Articles", stats['total_articles'])
        with col2:
            st.metric("Text Chunks", stats['total_chunks'])
        with col3:
            st.metric("Embeddings", stats['total_embeddings'])
    
    st.divider()
    
    # Quick actions
    st.subheader("🚀 Quick Actions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📈 View Trending Topics", use_container_width=True):
            st.switch_page("pages/trending.py")  # If using multipage
            
    with col2:
        if st.button("📋 Generate Daily Briefing", use_container_width=True):
            st.switch_page("pages/briefing.py")  # If using multipage
    
    # Recent activity or sample queries
    st.subheader("💡 Sample Queries")
    sample_queries = [
        "What are the latest AI developments?",
        "How is technology changing business?",
        "What recent innovations have been announced?",
    ]
    
    for query in sample_queries:
        if st.button(f"🔍 {query}", key=query):
            # Process sample query
            result = call_api("query", "POST", {"question": query})
            if result:
                with st.expander(f"Answer: {query}"):
                    st.write(result['answer'][:200] + "...")
                    st.caption(f"Confidence: {result['confidence_score']:.2f}")

def show_query_page():
    """Question answering interface"""
    st.header("❓ Ask About Current News")
    
    # Query input
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
        with st.spinner("Analyzing news articles..."):
            result = call_api("query", "POST", {
                "question": question,
                "top_k": top_k,
                "score_threshold": score_threshold
            })
            
            if result:
                # Display answer
                st.subheader("📝 Answer")
                st.write(result['answer'])
                
                # Metrics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Confidence", f"{result['confidence_score']:.2%}")
                with col2:
                    st.metric("Sources", len(result['sources']))
                with col3:
                    st.metric("Documents", result['retrieved_documents'])
                with col4:
                    st.metric("Response Time", f"{result['processing_time_ms']:.0f}ms")
                
                # Sources
                if result['sources']:
                    st.subheader("📚 Sources")
                    for source in result['sources']:
                        st.markdown(f'<div class="source-tag">{source}</div>', unsafe_allow_html=True)

def show_trending_page():
    """Trending topics analysis"""
    st.header("📊 Trending News Topics")
    
    trending = call_api("trending")
    if trending:
        for i, topic in enumerate(trending):
            with st.expander(f"#{i+1} {topic['topic'].title()} (Score: {topic['confidence']:.2f})"):
                st.write(topic['summary'])
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Articles", topic['article_count'])
                with col2:
                    st.metric("Confidence", f"{topic['confidence']:.2%}")
                
                st.write("**Sources:**")
                for source in topic['sources']:
                    st.markdown(f"• {source}")

def show_briefing_page():
    """Daily news briefing"""
    st.header("📋 Daily News Briefing")
    
    # Topic selection
    custom_topics = st.text_input(
        "Custom topics (comma-separated)",
        placeholder="artificial intelligence, blockchain, startups"
    )
    
    if st.button("📋 Generate Briefing"):
        with st.spinner("Generating comprehensive briefing..."):
            endpoint = "briefing"
            if custom_topics:
                endpoint += f"?topics={custom_topics}"
                
            briefing = call_api(endpoint)
            
            if briefing:
                st.success(f"📅 Briefing for {briefing['briefing_date']}")
                st.metric("Topics Covered", briefing['topics_covered'])
                
                for topic, details in briefing['briefings'].items():
                    st.subheader(f"📰 {topic.title()}")
                    st.write(details['summary'])
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Confidence", f"{details['confidence']:.2%}")
                    with col2:
                        st.metric("Sources", details['sources_count'])
                    with col3:
                        st.metric("Articles", details['articles_analyzed'])
                    
                    st.divider()

def show_stats_page():
    """System statistics and monitoring"""
    st.header("⚙️ System Statistics")
    
    stats = call_api("stats")
    if stats:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Data Statistics")
            
            # Create a simple bar chart
            data = {
                'Component': ['Articles', 'Text Chunks', 'Embeddings'],
                'Count': [stats['total_articles'], stats['total_chunks'], stats['total_embeddings']]
            }
            
            fig = px.bar(data, x='Component', y='Count', 
                        title="System Data Overview",
                        color='Component')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("🕐 System Info")
            st.info(f"Last Updated: {stats['last_updated'][:19]}")
            
            if st.button("🔄 Refresh Data"):
                refresh = call_api("refresh", "POST")
                if refresh:
                    st.success("Data refresh initiated!")

if __name__ == "__main__":
    main()
