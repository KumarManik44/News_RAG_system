from typing import List, Dict
from .rag_generator import NewsRAGGenerator, RAGResponse
import logging

logger = logging.getLogger(__name__)

class IntelligentNewsSummarizer:
    def __init__(self, openai_api_key: str = None):
        self.rag_generator = NewsRAGGenerator(openai_api_key=openai_api_key)
        
        # Common news query templates
        self.query_templates = {
            'latest_developments': "What are the latest developments in {}?",
            'key_updates': "What are the key updates about {}?",
            'current_status': "What is the current status of {}?",
            'recent_news': "What recent news is available about {}?",
            'market_impact': "How is {} impacting the market or industry?",
            'technology_trends': "What are the latest technology trends in {}?",
            'business_updates': "What are the recent business updates regarding {}?"
        }
    
    def summarize_topic(self, topic: str, query_type: str = 'latest_developments') -> RAGResponse:
        """Summarize a specific news topic"""
        
        if query_type in self.query_templates:
            query = self.query_templates[query_type].format(topic)
        else:
            query = f"What is the latest news about {topic}?"
        
        return self.rag_generator.generate_response(query, top_k=4)
    
    def daily_news_briefing(self, topics: List[str] = None) -> Dict[str, RAGResponse]:
        """Generate a daily news briefing on specified topics"""
        
        if topics is None:
            topics = [
                "artificial intelligence",
                "technology companies",
                "business developments", 
                "market trends"
            ]
        
        briefing = {}
        
        for topic in topics:
            try:
                response = self.summarize_topic(topic, 'latest_developments')
                briefing[topic] = response
                
            except Exception as e:
                logger.error(f"Error generating briefing for {topic}: {str(e)}")
                continue
        
        return briefing
    
    def answer_news_question(self, question: str) -> RAGResponse:
        """Answer a specific question about current news"""
        
        return self.rag_generator.generate_response(question, top_k=5)
    
    def trending_topics_summary(self) -> List[Dict]:
        """Generate summaries for trending topics based on available articles"""
        
        # In a production system, this would analyze article frequency/recency
        # For now, we'll use common business/tech topics
        trending_topics = [
            "artificial intelligence",
            "technology innovation", 
            "business trends",
            "market developments"
        ]
        
        summaries = []
        
        for topic in trending_topics:
            response = self.summarize_topic(topic, 'recent_news')
            
            if response.retrieved_documents:  # Only include topics with content
                summaries.append({
                    'topic': topic,
                    'summary': response.answer,
                    'article_count': len(response.retrieved_documents),
                    'confidence': response.confidence_score,
                    'sources': response.sources[:3]  # Top 3 sources
                })
        
        # Sort by confidence/article count
        summaries.sort(key=lambda x: (x['confidence'], x['article_count']), reverse=True)
        
        return summaries
