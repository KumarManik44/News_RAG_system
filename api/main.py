from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import logging
from datetime import datetime
import asyncio

from llm_integration.news_summarizer import IntelligentNewsSummarizer
from data_ingestion.news_api_client import NewsAPIClient
from data_ingestion.rss_processor import RSSProcessor
from data_ingestion.article_storage import ArticleStorage
from text_processing.processor import TextProcessor
from embeddings.embedding_generator import EmbeddingGenerator
from vector_db.faiss_manager import FAISSManager

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
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
news_summarizer = IntelligentNewsSummarizer()

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
    """
    Answer questions about current news using RAG
    """
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
    """
    Generate summary for a specific news topic
    """
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
    """
    Get trending news topics with summaries
    """
    try:
        trending_summaries = news_summarizer.trending_topics_summary()
        
        return [
            TrendingTopic(
                topic=item['topic'],
                summary=item['summary'][:300] + "...",  # Truncate for API response
                article_count=item['article_count'],
                confidence=item['confidence'],
                sources=item['sources']
            )
            for item in trending_summaries
        ]
        
    except Exception as e:
        logger.error(f"Error in trending endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get trending topics: {str(e)}")

@app.get("/briefing", tags=["Analytics"])
async def daily_briefing(topics: Optional[str] = None):
    """
    Generate daily news briefing
    """
    try:
        if topics:
            topic_list = [topic.strip() for topic in topics.split(',')]
        else:
            topic_list = None
            
        briefing = news_summarizer.daily_news_briefing(topic_list)
        
        formatted_briefing = {}
        for topic, response in briefing.items():
            formatted_briefing[topic] = {
                "summary": response.answer,
                "confidence": response.confidence_score,
                "sources_count": len(response.sources),
                "articles_analyzed": len(response.retrieved_documents)
            }
            
        return {
            "briefing_date": datetime.now().strftime("%Y-%m-%d"),
            "topics_covered": len(formatted_briefing),
            "briefings": formatted_briefing
        }
        
    except Exception as e:
        logger.error(f"Error in briefing endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Briefing generation failed: {str(e)}")

@app.get("/stats", response_model=SystemStats, tags=["System"])
async def get_system_stats():
    """
    Get system statistics
    """
    try:
        # Get database statistics
        storage = ArticleStorage()
        embedding_generator = EmbeddingGenerator()
        
        # This is a simplified version - you'd implement proper stats methods
        return SystemStats(
            total_articles=15,  # From your test results
            total_chunks=11,    # From your test results
            total_embeddings=11, # From your test results
            last_updated=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Stats retrieval failed: {str(e)}")

# Background task for data refresh
@app.post("/refresh", tags=["System"])
async def refresh_data(background_tasks: BackgroundTasks):
    """
    Trigger background data refresh
    """
    def refresh_pipeline():
        try:
            logger.info("Starting data refresh pipeline...")
            # Add your refresh logic here
            logger.info("Data refresh completed")
        except Exception as e:
            logger.error(f"Data refresh failed: {str(e)}")
    
    background_tasks.add_task(refresh_pipeline)
    return {"message": "Data refresh initiated", "status": "in_progress"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
