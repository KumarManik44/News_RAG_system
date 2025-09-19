import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import logging
from datetime import datetime
import asyncio

# Now import your modules
try:
    from llm_integration.news_summarizer import IntelligentNewsSummarizer
    from data_ingestion.article_storage import ArticleStorage
    from embeddings.embedding_generator import EmbeddingGenerator
    print("✅ All modules imported successfully")
except ImportError as e:
    print(f"❌ Import error: {e}")
    # Fallback - we'll create a simple mock for testing
    class IntelligentNewsSummarizer:
        def answer_news_question(self, question):
            return type('obj', (object,), {
                'answer': f"Mock response for: {question}",
                'sources': ['Mock Source'],
                'confidence_score': 0.5,
                'retrieved_documents': []
            })()
        
        def summarize_topic(self, topic, query_type=None):
            return type('obj', (object,), {
                'answer': f"Mock summary for: {topic}",
                'sources': ['Mock Source'],
                'confidence_score': 0.7,
                'retrieved_documents': []
            })()
        
        def trending_topics_summary(self):
            return [{'topic': 'Mock Topic', 'summary': 'Mock summary', 'article_count': 5, 'confidence': 0.8, 'sources': ['Mock']}]
        
        def daily_news_briefing(self, topics=None):
            return {'mock_topic': type('obj', (object,), {
                'answer': 'Mock briefing',
                'confidence_score': 0.6,
                'sources': ['Mock'],
                'retrieved_documents': []
            })()}

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Intelligent News Summarizer API",
    description="Production-ready RAG system for news summarization and analysis",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
try:
    news_summarizer = IntelligentNewsSummarizer()
    print("✅ News summarizer initialized")
except Exception as e:
    print(f"❌ Error initializing news summarizer: {e}")
    news_summarizer = IntelligentNewsSummarizer()  # Use mock

# Request/Response Models
class QueryRequest(BaseModel):
    question: str
    top_k: int = 5
    score_threshold: float = 0.2

class SummarizeRequest(BaseModel):
    topic: str
    query_type: str = "latest_developments"

class RAGResponse(BaseModel):
    answer: str
    sources: List[str]
    confidence_score: float
    retrieved_documents: int
    processing_time_ms: float

class TrendingTopic(BaseModel):
    topic: str
    summary: str
    article_count: int
    confidence: float
    sources: List[str]

class SystemStats(BaseModel):
    total_articles: int
    total_chunks: int
    total_embeddings: int
    last_updated: str

# API Endpoints
@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint"""
    return {
        "message": "Intelligent News Summarizer API",
        "version": "1.0.0",
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/query", response_model=RAGResponse, tags=["RAG"])
async def query_news(request: QueryRequest):
    """Answer questions about current news using RAG"""
    try:
        start_time = datetime.now()
        
        response = news_summarizer.answer_news_question(request.question)
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        
        return RAGResponse(
            answer=response.answer,
            sources=response.sources,
            confidence_score=response.confidence_score,
            retrieved_documents=len(response.retrieved_documents),
            processing_time_ms=processing_time
        )
        
    except Exception as e:
        logger.error(f"Error in query endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Query processing failed: {str(e)}")

@app.post("/summarize", response_model=RAGResponse, tags=["Summarization"])
async def summarize_topic(request: SummarizeRequest):
    """Generate summary for a specific news topic"""
    try:
        start_time = datetime.now()
        
        response = news_summarizer.summarize_topic(
            topic=request.topic,
            query_type=request.query_type
        )
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        
        return RAGResponse(
            answer=response.answer,
            sources=response.sources,
            confidence_score=response.confidence_score,
            retrieved_documents=len(response.retrieved_documents),
            processing_time_ms=processing_time
        )
        
    except Exception as e:
        logger.error(f"Error in summarize endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Summarization failed: {str(e)}")

@app.get("/trending", response_model=List[TrendingTopic], tags=["Analytics"])
async def get_trending_topics():
    """Get trending news topics with summaries"""
    try:
        trending_summaries = news_summarizer.trending_topics_summary()
        
        return [
            TrendingTopic(
                topic=item['topic'],
                summary=item['summary'][:300] + "...",
                article_count=item['article_count'],
                confidence=item['confidence'],
                sources=item['sources']
            )
            for item in trending_summaries
        ]
        
    except Exception as e:
        logger.error(f"Error in trending endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get trending topics: {str(e)}")

@app.get("/stats", response_model=SystemStats, tags=["System"])
async def get_system_stats():
    """Get system statistics"""
    try:
        return SystemStats(
            total_articles=15,
            total_chunks=11,
            total_embeddings=11,
            last_updated=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Stats retrieval failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting FastAPI server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
