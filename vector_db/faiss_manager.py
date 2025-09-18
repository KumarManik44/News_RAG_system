import faiss
import numpy as np
import sqlite3
import pickle
import os
from typing import List, Tuple, Optional, Dict
from embeddings.embedding_generator import EmbeddingGenerator
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

class FAISSManager:
    def __init__(self, 
                 index_path: str = "faiss_index.bin",
                 metadata_path: str = "faiss_metadata.pkl",
                 embedding_dim: int = 384):
        
        self.index_path = index_path
        self.metadata_path = metadata_path
        self.embedding_dim = embedding_dim
        
        # Initialize FAISS index (Flat L2 for exact search, good for small datasets)
        self.index = faiss.IndexFlatL2(embedding_dim)
        
        # Store metadata for each indexed vector
        self.chunk_metadata = []  # List of chunk_ids and metadata
        
        # Load existing index if available
        self.load_index()
        
    def build_index_from_database(self) -> int:
        """Build FAISS index from embeddings stored in database"""
        logger.info("Building FAISS index from database embeddings...")
        
        # Get all embeddings from database
        embedding_generator = EmbeddingGenerator()
        embeddings, chunk_ids = embedding_generator.get_all_embeddings()
        
        if len(embeddings) == 0:
            logger.warning("No embeddings found in database")
            return 0
        
        # Reset index
        self.index = faiss.IndexFlatL2(self.embedding_dim)
        self.chunk_metadata = []
        
        # Add embeddings to FAISS index
        embeddings_array = embeddings.astype('float32')
        self.index.add(embeddings_array)
        
        # Store metadata
        for chunk_id in chunk_ids:
            chunk_info = self._get_chunk_info(chunk_id)
            self.chunk_metadata.append(chunk_info)
        
        logger.info(f"Built FAISS index with {self.index.ntotal} vectors")
        
        # Save index and metadata
        self.save_index()
        
        return self.index.ntotal
    
    def _get_chunk_info(self, chunk_id: str) -> Dict:
        """Get chunk information from database"""
        conn = sqlite3.connect(settings.DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT tc.chunk_id, tc.article_id, tc.content, tc.chunk_index,
                   a.title, a.source, a.published_at, a.url
            FROM text_chunks tc
            JOIN articles a ON tc.article_id = a.id
            WHERE tc.chunk_id = ?
        ''', (chunk_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'chunk_id': result[0],
                'article_id': result[1],
                'content': result[2],
                'chunk_index': result[3],
                'article_title': result[4],
                'source': result[5],
                'published_at': result[6],
                'url': result[7]
            }
        
        return {'chunk_id': chunk_id, 'content': 'Unknown'}
    
    def search_similar(self, 
                      query_embedding: np.ndarray, 
                      k: int = 5,
                      score_threshold: float = None) -> List[Dict]:
        """Search for similar vectors in FAISS index"""
        
        if self.index.ntotal == 0:
            logger.warning("FAISS index is empty")
            return []
        
        # Ensure query embedding is the right shape and type
        if query_embedding.ndim == 1:
            query_embedding = query_embedding.reshape(1, -1)
        
        query_embedding = query_embedding.astype('float32')
        
        # Search in FAISS index
        distances, indices = self.index.search(query_embedding, min(k, self.index.ntotal))
        
        results = []
        for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
            if idx == -1:  # Invalid result
                continue
                
            # Convert L2 distance to similarity score (higher is better)
            similarity_score = 1 / (1 + distance)
            
            # Apply score threshold if specified
            if score_threshold and similarity_score < score_threshold:
                continue
            
            # Get metadata for this result
            metadata = self.chunk_metadata[idx] if idx < len(self.chunk_metadata) else {}
            
            result = {
                'rank': i + 1,
                'similarity_score': float(similarity_score),
                'distance': float(distance),
                **metadata
            }
            
            results.append(result)
        
        return results
    
    def search_by_text(self, 
                      query_text: str, 
                      k: int = 5,
                      score_threshold: float = None) -> List[Dict]:
        """Search using text query (generates embedding first)"""
        
        # Generate embedding for query text
        embedding_generator = EmbeddingGenerator()
        query_embedding = embedding_generator.model.encode([query_text], normalize_embeddings=True)
        
        return self.search_similar(query_embedding, k, score_threshold)
    
    def add_new_embeddings(self, chunk_ids: List[str], embeddings: np.ndarray):
        """Add new embeddings to existing index"""
        
        if len(chunk_ids) != len(embeddings):
            raise ValueError("Number of chunk_ids must match number of embeddings")
        
        # Add to FAISS index
        embeddings_array = embeddings.astype('float32')
        self.index.add(embeddings_array)
        
        # Add metadata
        for chunk_id in chunk_ids:
            chunk_info = self._get_chunk_info(chunk_id)
            self.chunk_metadata.append(chunk_info)
        
        logger.info(f"Added {len(chunk_ids)} new embeddings to index")
        
        # Save updated index
        self.save_index()
    
    def save_index(self):
        """Save FAISS index and metadata to files"""
        try:
            # Save FAISS index
            faiss.write_index(self.index, self.index_path)
            
            # Save metadata
            with open(self.metadata_path, 'wb') as f:
                pickle.dump(self.chunk_metadata, f)
            
            logger.info(f"Saved FAISS index with {self.index.ntotal} vectors")
            
        except Exception as e:
            logger.error(f"Error saving index: {str(e)}")
    
    def load_index(self):
        """Load FAISS index and metadata from files"""
        try:
            if os.path.exists(self.index_path) and os.path.exists(self.metadata_path):
                # Load FAISS index
                self.index = faiss.read_index(self.index_path)
                
                # Load metadata
                with open(self.metadata_path, 'rb') as f:
                    self.chunk_metadata = pickle.load(f)
                
                logger.info(f"Loaded FAISS index with {self.index.ntotal} vectors")
                return True
            else:
                logger.info("No existing index found, will create new one")
                return False
                
        except Exception as e:
            logger.error(f"Error loading index: {str(e)}")
            # Reset to empty index on error
            self.index = faiss.IndexFlatL2(self.embedding_dim)
            self.chunk_metadata = []
            return False
    
    def get_index_stats(self) -> Dict:
        """Get statistics about the FAISS index"""
        return {
            'total_vectors': self.index.ntotal,
            'embedding_dimension': self.embedding_dim,
            'index_type': type(self.index).__name__,
            'metadata_count': len(self.chunk_metadata),
            'index_file_exists': os.path.exists(self.index_path),
            'metadata_file_exists': os.path.exists(self.metadata_path)
        }
