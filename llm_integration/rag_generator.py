import openai
from typing import Dict, List, Optional
import logging
from vector_db.retriever import DocumentRetriever
from vector_db.faiss_manager import FAISSManager
from config.settings import settings
import os
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class RAGResponse:
    answer: str
    sources: List[str]
    retrieved_documents: List[Dict]
    confidence_score: float
    query: str

class NewsRAGGenerator:
    def __init__(self, 
                 openai_api_key: str = None,
                 model_name: str = "gpt-3.5-turbo",  # Cost-effective for testing
                 temperature: float = 0.1,  # Low for factual responses
                 max_tokens: int = 800):
        
        # Set OpenAI API key
        self.api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        if self.api_key:
            openai.api_key = self.api_key
        
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        # Initialize retriever
        faiss_manager = FAISSManager()
        self.retriever = DocumentRetriever(faiss_manager)
        
        # News summarization prompt template optimized for accuracy
        self.system_prompt = """You are an expert news analyst and summarizer. Your task is to provide accurate, concise, and well-sourced answers about current events based on the provided news articles.

INSTRUCTIONS:
1. Answer the user's question using ONLY the information provided in the retrieved news articles
2. Provide a comprehensive but concise response (200-400 words)
3. Cite sources by mentioning the news outlet and article title
4. If the retrieved articles don't contain enough information to fully answer the question, state this clearly
5. Focus on factual information and avoid speculation
6. Maintain journalistic objectivity and present multiple perspectives when available

FORMAT YOUR RESPONSE AS:
**Summary:** [Main answer to the question]

**Key Points:**
- [Important detail 1]
- [Important detail 2] 
- [Important detail 3]

**Sources:** [List the sources used]"""

    def generate_response(self, 
                         query: str,
                         top_k: int = 3,
                         score_threshold: float = 0.2) -> RAGResponse:
        """
        Generate RAG response for news query
        
        Args:
            query: User question about news
            top_k: Number of documents to retrieve
            score_threshold: Minimum similarity threshold
            
        Returns:
            RAGResponse with answer and sources
        """
        
        logger.info(f"Generating RAG response for: '{query[:50]}...'")
        
        # Step 1: Retrieve relevant documents
        retrieval_result = self.retriever.retrieve_relevant_documents(
            query=query,
            top_k=top_k,
            score_threshold=score_threshold,
            include_sources=True
        )
        
        if not retrieval_result['retrieved_documents']:
            return RAGResponse(
                answer="I couldn't find any relevant news articles to answer your question. Please try rephrasing your query or asking about a different topic.",
                sources=[],
                retrieved_documents=[],
                confidence_score=0.0,
                query=query
            )
        
        # Step 2: Prepare context for LLM
        context_text = self._format_context(retrieval_result['retrieved_documents'])
        
        # Step 3: Create the prompt
        user_prompt = f"""RETRIEVED NEWS ARTICLES:

{context_text}

USER QUESTION: {query}

Please provide a comprehensive answer based on the news articles above."""
        
        # Step 4: Generate response using OpenAI
        try:
            if self.api_key:
                response = self._call_openai(user_prompt)
            else:
                # Fallback to local LLM or simple template
                response = self._fallback_response(query, retrieval_result)
            
            # Calculate confidence based on retrieval scores
            avg_similarity = retrieval_result['search_metadata']['avg_similarity']
            confidence_score = min(avg_similarity * 2, 1.0)  # Scale to 0-1
            
            return RAGResponse(
                answer=response,
                sources=retrieval_result['sources'],
                retrieved_documents=retrieval_result['retrieved_documents'],
                confidence_score=confidence_score,
                query=query
            )
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            
            # Return fallback response on error
            return RAGResponse(
                answer=self._fallback_response(query, retrieval_result),
                sources=retrieval_result['sources'],
                retrieved_documents=retrieval_result['retrieved_documents'],
                confidence_score=0.5,
                query=query
            )
    
    def _call_openai(self, user_prompt: str) -> str:
        """Call OpenAI API for response generation"""
        
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        response = openai.ChatCompletion.create(
            model=self.model_name,
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            top_p=0.9,
            frequency_penalty=0.1,
            presence_penalty=0.1
        )
        
        return response.choices[0].message.content.strip()
    
    def _fallback_response(self, query: str, retrieval_result: Dict) -> str:
        """Generate a simple template-based response when OpenAI is not available"""
        
        docs = retrieval_result['retrieved_documents']
        
        if not docs:
            return f"I found no relevant articles to answer: '{query}'"
        
        # Simple extractive summary
        top_content = docs[0]['content'][:300] + "..."
        
        response = f"""**Summary:** Based on the retrieved news articles, here's what I found regarding '{query}':

{top_content}

**Key Points:**
"""
        
        # Add bullet points from top articles
        for i, doc in enumerate(docs[:3]):
            title = doc.get('article_title', 'Unknown Article')[:60]
            response += f"- {title}... (Source: {doc.get('source', 'Unknown')})\n"
        
        response += f"\n**Sources:** {len(docs)} relevant articles found from {', '.join(set(doc.get('source', 'Unknown') for doc in docs))}"
        
        return response
    
    def _format_context(self, documents: List[Dict]) -> str:
        """Format retrieved documents for LLM context"""
        
        formatted_context = ""
        
        for i, doc in enumerate(documents, 1):
            formatted_context += f"""
Article {i}:
Title: {doc.get('article_title', 'Unknown Title')}
Source: {doc.get('source', 'Unknown Source')}
Content: {doc.get('content', '')[:400]}...
Similarity Score: {doc.get('similarity_score', 0):.3f}

---
"""
        
        return formatted_context
    
    def batch_summarize_topics(self, topics: List[str]) -> Dict[str, RAGResponse]:
        """Summarize multiple news topics in batch"""
        
        results = {}
        
        for topic in topics:
            try:
                response = self.generate_response(topic)
                results[topic] = response
                logger.info(f"Successfully processed topic: {topic}")
                
            except Exception as e:
                logger.error(f"Error processing topic '{topic}': {str(e)}")
                results[topic] = RAGResponse(
                    answer=f"Error processing topic: {str(e)}",
                    sources=[],
                    retrieved_documents=[],
                    confidence_score=0.0,
                    query=topic
                )
        
        return results
