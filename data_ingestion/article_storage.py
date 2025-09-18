import sqlite3
from dataclasses import dataclass
from typing import Optional, List
import json

@dataclass
class Article:
    id: str
    title: str
    url: str
    content: str
    summary: str
    source: str
    published_at: str
    language: str
    raw_html: Optional[str] = None
    metadata: Optional[dict] = None

class ArticleStorage:
    def __init__(self, db_path="news_articles.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database with articles table"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS articles (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                url TEXT UNIQUE NOT NULL,
                content TEXT,
                summary TEXT,
                source TEXT,
                published_at TEXT,
                language TEXT,
                raw_html TEXT,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                processed BOOLEAN DEFAULT FALSE
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def store_article(self, article: Article):
        """Store article in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO articles 
            (id, title, url, content, summary, source, published_at, language, raw_html, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            article.id, article.title, article.url, article.content,
            article.summary, article.source, article.published_at,
            article.language, article.raw_html, 
            json.dumps(article.metadata) if article.metadata else None
        ))
        
        conn.commit()
        conn.close()
