import sqlite3
from typing import List, Dict, Optional
from .text_cleaner import TextCleaner
from .language_detector import LanguageDetector
from .text_chunker import TextChunker, TextChunk
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

class TextProcessor:
    def __init__(self, db_path: str = None):
        self.db_path = db_path or settings.DATABASE_PATH
        self.cleaner = TextCleaner()
        self.language_detector = LanguageDetector()
        self.chunker = TextChunker()
        
        self.init_chunks_table()
    
    def init_chunks_table(self):
        """Initialize table for storing processed chunks"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS text_chunks (
                chunk_id TEXT PRIMARY KEY,
                article_id TEXT NOT NULL,
                content TEXT NOT NULL,
                chunk_index INTEGER,
                start_pos INTEGER,
                end_pos INTEGER,
                word_count INTEGER,
                char_count INTEGER,
                language_code TEXT,
                language_confidence REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (article_id) REFERENCES articles (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def process_unprocessed_articles(self) -> int:
        """Process all articles that haven't been processed yet"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get unprocessed articles
        cursor.execute('''
            SELECT id, title, content, summary 
            FROM articles 
            WHERE processed = FALSE AND content IS NOT NULL
        ''')
        
        articles = cursor.fetchall()
        conn.close()
        
        processed_count = 0
        
        for article_id, title, content, summary in articles:
            try:
                # Combine title, content, and summary for processing
                full_text = f"{title}\n\n{content}\n\n{summary}" if summary else f"{title}\n\n{content}"
                
                chunks = self.process_article_text(article_id, full_text)
                
                if chunks:
                    self.store_chunks(chunks)
                    self.mark_article_processed(article_id)
                    processed_count += 1
                    logger.info(f"Processed article {article_id}: {len(chunks)} chunks created")
                
            except Exception as e:
                logger.error(f"Error processing article {article_id}: {str(e)}")
                continue
        
        return processed_count
    
    def process_article_text(self, article_id: str, text: str) -> List[TextChunk]:
        """Process a single article's text into chunks"""
        # Step 1: Clean the text
        cleaned_text = self.cleaner.clean_text(text)
        
        if len(cleaned_text) < 50:  # Skip very short articles
            return []
        
        # Step 2: Detect language
        language_code, confidence = self.language_detector.detect_language(cleaned_text)
        
        # Step 3: Create chunks
        chunks = self.chunker.chunk_by_sentences(cleaned_text, article_id)
        
        # Step 4: Add language metadata to chunks
        for chunk in chunks:
            if chunk.metadata is None:
                chunk.metadata = {}
            chunk.metadata['language_code'] = language_code
            chunk.metadata['language_confidence'] = confidence
        
        return chunks
    
    def store_chunks(self, chunks: List[TextChunk]):
        """Store processed chunks in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for chunk in chunks:
            cursor.execute('''
                INSERT OR REPLACE INTO text_chunks 
                (chunk_id, article_id, content, chunk_index, start_pos, end_pos,
                 word_count, char_count, language_code, language_confidence)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                chunk.chunk_id,
                chunk.article_id,
                chunk.content,
                chunk.chunk_index,
                chunk.start_pos,
                chunk.end_pos,
                chunk.metadata.get('word_count', 0),
                chunk.metadata.get('char_count', 0),
                chunk.metadata.get('language_code'),
                chunk.metadata.get('language_confidence', 0.0)
            ))
        
        conn.commit()
        conn.close()
    
    def mark_article_processed(self, article_id: str):
        """Mark article as processed"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE articles 
            SET processed = TRUE 
            WHERE id = ?
        ''', (article_id,))
        
        conn.commit()
        conn.close()
