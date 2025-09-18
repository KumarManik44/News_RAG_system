from sentence_transformers import SentenceTransformer
import numpy as np
import sqlite3
from typing import List, Dict, Optional, Tuple
import torch
import logging
from config.settings import settings

logger = logging.getLogger(__name__)

class EmbeddingGenerator:
    def __init__(self, 
                 model_name: str = "all-MiniLM-L6-v2",  # Fast and efficient
                 batch_size: int = 32,  # Optimal for memory and speed
                 device: str = None):
        
        # Auto-detect device
        if device is None:
            device = 'cuda' if torch.cuda.is_available() else 'cpu'
        
        self.device = device
        self.batch_size = batch_size
        self.model_name = model_name
        
        logger.info(f"Initializing embedding model: {model_name} on {device}")
        
        # Load the sentence transformer model
        self.model = SentenceTransformer(model_name, device=device)
        
        # Get embedding dimension
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
        logger.info(f"Embedding dimension: {self.embedding_dim}")
        
        # Initialize embeddings table
        self.init_embeddings_table()
    
    def init_embeddings_table(self):
        """Initialize table for storing embeddings"""
        conn = sqlite3.connect(settings.DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS embeddings (
                chunk_id TEXT PRIMARY KEY,
                embedding BLOB NOT NULL,
                embedding_dim INTEGER NOT NULL,
                model_name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (chunk_id) REFERENCES text_chunks (chunk_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def generate_embeddings_for_unprocessed_chunks(self) -> int:
        """Generate embeddings for all chunks that don't have embeddings yet"""
        
        # Get chunks without embeddings
        unprocessed_chunks = self._get_unprocessed_chunks()
        
        if not unprocessed_chunks:
            logger.info("No unprocessed chunks found")
            return 0
        
        logger.info(f"Generating embeddings for {len(unprocessed_chunks)} chunks")
        
        # Process in batches for memory efficiency
        total_processed = 0
        
        for i in range(0, len(unprocessed_chunks), self.batch_size):
            batch_chunks = unprocessed_chunks[i:i + self.batch_size]
            
            # Extract texts and chunk_ids
            chunk_ids = [chunk[0] for chunk in batch_chunks]
            texts = [chunk[1] for chunk in batch_chunks]
            
            try:
                # Generate embeddings for batch
                embeddings = self.model.encode(
                    texts,
                    batch_size=len(texts),
                    convert_to_tensor=False,  # Keep as numpy arrays
                    normalize_embeddings=True,  # Normalize for better similarity search
                    show_progress_bar=True if i == 0 else False
                )
                
                # Store embeddings
                self._store_embeddings_batch(chunk_ids, embeddings)
                
                total_processed += len(batch_chunks)
                logger.info(f"Processed batch {i//self.batch_size + 1}: {total_processed}/{len(unprocessed_chunks)} chunks")
                
            except Exception as e:
                logger.error(f"Error processing batch {i//self.batch_size + 1}: {str(e)}")
                continue
        
        logger.info(f"Successfully generated embeddings for {total_processed} chunks")
        return total_processed
    
    def _get_unprocessed_chunks(self) -> List[Tuple[str, str]]:
        """Get chunks that don't have embeddings yet"""
        conn = sqlite3.connect(settings.DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT tc.chunk_id, tc.content
            FROM text_chunks tc
            LEFT JOIN embeddings e ON tc.chunk_id = e.chunk_id
            WHERE e.chunk_id IS NULL
            ORDER BY tc.chunk_id
        ''')
        
        chunks = cursor.fetchall()
        conn.close()
        
        return chunks
    
    def _store_embeddings_batch(self, chunk_ids: List[str], embeddings: np.ndarray):
        """Store a batch of embeddings in the database"""
        conn = sqlite3.connect(settings.DATABASE_PATH)
        cursor = conn.cursor()
        
        # Convert embeddings to bytes for storage
        embedding_data = []
        for chunk_id, embedding in zip(chunk_ids, embeddings):
            embedding_bytes = embedding.astype(np.float32).tobytes()
            embedding_data.append((
                chunk_id,
                embedding_bytes,
                self.embedding_dim,
                self.model_name
            ))
        
        cursor.executemany('''
            INSERT OR REPLACE INTO embeddings 
            (chunk_id, embedding, embedding_dim, model_name)
            VALUES (?, ?, ?, ?)
        ''', embedding_data)
        
        conn.commit()
        conn.close()
    
    def get_embedding_by_chunk_id(self, chunk_id: str) -> Optional[np.ndarray]:
        """Retrieve embedding for a specific chunk"""
        conn = sqlite3.connect(settings.DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT embedding, embedding_dim 
            FROM embeddings 
            WHERE chunk_id = ?
        ''', (chunk_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            embedding_bytes, dim = result
            embedding = np.frombuffer(embedding_bytes, dtype=np.float32)
            return embedding.reshape(-1)
        
        return None
    
    def get_all_embeddings(self) -> Tuple[np.ndarray, List[str]]:
        """Get all embeddings and their corresponding chunk IDs"""
        conn = sqlite3.connect(settings.DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT chunk_id, embedding, embedding_dim 
            FROM embeddings 
            ORDER BY chunk_id
        ''')
        
        results = cursor.fetchall()
        conn.close()
        
        if not results:
            return np.array([]), []
        
        embeddings = []
        chunk_ids = []
        
        for chunk_id, embedding_bytes, dim in results:
            embedding = np.frombuffer(embedding_bytes, dtype=np.float32)
            embeddings.append(embedding.reshape(-1))
            chunk_ids.append(chunk_id)
        
        return np.array(embeddings), chunk_ids
    
    def get_embedding_stats(self) -> Dict:
        """Get statistics about stored embeddings"""
        conn = sqlite3.connect(settings.DATABASE_PATH)
        cursor = conn.cursor()
        
        # Total embeddings count
        cursor.execute("SELECT COUNT(*) FROM embeddings")
        total_count = cursor.fetchone()[0]
        
        # Model distribution
        cursor.execute('''
            SELECT model_name, COUNT(*) 
            FROM embeddings 
            GROUP BY model_name
        ''')
        model_distribution = cursor.fetchall()
        
        # Embedding dimension info
        cursor.execute("SELECT DISTINCT embedding_dim FROM embeddings")
        dimensions = cursor.fetchall()
        
        conn.close()
        
        return {
            'total_embeddings': total_count,
            'model_distribution': dict(model_distribution),
            'embedding_dimensions': [dim[0] for dim in dimensions]
        }
