from typing import List, Dict, Optional
from .faiss_manager import FAISSManager
from embeddings.embedding_generator import EmbeddingGenerator
import logging

logger = logging.getLogger(__name__)

class DocumentRetriever:
    def __init__(self, faiss_manager: FAISSManager = None):
        self.faiss_manager = faiss_manager or FAISSManager()
        self.embedding_generator = EmbeddingGenerator()
        
    def retrieve_relevant_documents(self, 
                                  query: str, 
                                  top_k: int = 5,
                                  score_threshold: float = 0.3,
                                  include_sources: bool = True) -> Dict:
        """
        Main retrieval method for RAG system
        
        Args:
            query: User query text
            top_k: Number of top documents to retrieve
            score_threshold: Minimum similarity score
            include_sources: Whether to include source information
        
        Returns:
            Dictionary containing retrieved documents and metadata
        """
        
        logger.info(f"Retrieving documents for query: '{query[:50]}...'")
        
        # Search for similar documents
        search_results = self.faiss_manager.search_by_text(
            query_text=query,
            k=top_k,
            score_threshold=score_threshold
        )
        
        if not search_results:
            return {
                'query': query,
                'retrieved_documents': [],
                'sources': [],
                'context_text': '',
                'total_results': 0
            }
        
        # Format results for RAG
        retrieved_docs = []
        sources = set()
        context_parts = []
        
        for i, result in enumerate(search_results):
            doc_info = {
                'rank': result['rank'],
                'content': result.get('content', ''),
                'similarity_score': result['similarity_score'],
                'chunk_id': result.get('chunk_id', ''),
                'article_title': result.get('article_title', 'Unknown'),
                'source': result.get('source', 'Unknown')
            }
            
            if include_sources:
                doc_info.update({
                    'article_id': result.get('article_id', ''),
                    'published_at': result.get('published_at', ''),
                    'url': result.get('url', '')
                })
                
                sources.add(f"{result.get('source', 'Unknown')} - {result.get('article_title', 'Unknown')}")
            
            retrieved_docs.append(doc_info)
            
            # Build context text for LLM
            context_parts.append(f"[Document {i+1}]: {result.get('content', '')}")
        
        # Combine all context
        context_text = "\n\n".join(context_parts)
        
        return {
            'query': query,
            'retrieved_documents': retrieved_docs,
            'sources': list(sources),
            'context_text': context_text,
            'total_results': len(retrieved_docs),
            'search_metadata': {
                'top_k_requested': top_k,
                'score_threshold': score_threshold,
                'avg_similarity': sum(doc['similarity_score'] for doc in retrieved_docs) / len(retrieved_docs) if retrieved_docs else 0
            }
        }
    
    def retrieve_by_filters(self, 
                           query: str,
                           source_filter: Optional[str] = None,
                           date_filter: Optional[str] = None,
                           top_k: int = 5) -> Dict:
        """Retrieve documents with additional filtering"""
        
        # Get all results first
        all_results = self.faiss_manager.search_by_text(query, k=top_k * 2)  # Get more to filter
        
        # Apply filters
        filtered_results = []
        
        for result in all_results:
            # Source filter
            if source_filter and source_filter.lower() not in result.get('source', '').lower():
                continue
                
            # Date filter (basic implementation)
            if date_filter and date_filter not in result.get('published_at', ''):
                continue
            
            filtered_results.append(result)
            
            if len(filtered_results) >= top_k:
                break
        
        return self.retrieve_relevant_documents(query, top_k=len(filtered_results))
