from data_ingestion.news_api_client import NewsAPIClient
from data_ingestion.rss_processor import RSSProcessor
from data_ingestion.article_storage import ArticleStorage, Article
from config.settings import settings
from datetime import datetime, timedelta
import hashlib
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NewsIngestionPipeline:
    def __init__(self):
        self.api_client = NewsAPIClient(settings.NEWSAPI_KEY)
        self.rss_processor = RSSProcessor()
        self.storage = ArticleStorage(settings.DATABASE_PATH)
        
    def run_full_ingestion(self):
        """Run complete data ingestion pipeline"""
        logger.info("Starting news ingestion pipeline...")
        
        # Ingest from NewsAPI
        self.ingest_from_newsapi()
        
        # Ingest from RSS feeds
        self.ingest_from_rss()
        
        logger.info("News ingestion pipeline completed")
        
    def ingest_from_newsapi(self):
        """Ingest articles from NewsAPI"""
        logger.info("Fetching from NewsAPI...")
        
        news_data = self.api_client.fetch_everything(
            query="artificial intelligence OR technology",
            page_size=settings.DEFAULT_PAGE_SIZE,
            from_date=datetime.now() - timedelta(days=1)
        )
        
        if news_data and news_data.get('articles'):
            for article_data in news_data['articles']:
                article = Article(
                    id=hashlib.md5(article_data['url'].encode()).hexdigest(),
                    title=article_data['title'],
                    url=article_data['url'],
                    content=article_data.get('content', ''),
                    summary=article_data.get('description', ''),
                    source=article_data['source']['name'],
                    published_at=article_data['publishedAt'],
                    language=settings.DEFAULT_LANGUAGE
                )
                self.storage.store_article(article)
                
            logger.info(f"Stored {len(news_data['articles'])} articles from NewsAPI")
    
    def ingest_from_rss(self):
        """Ingest articles from RSS feeds"""
        logger.info("Fetching from RSS feeds...")
        
        total_articles = 0
        for source, feed_url in settings.RSS_FEEDS.items():
            articles = self.rss_processor.fetch_feed(feed_url)
            
            for article_data in articles[:5]:  # Limit to 5 per source
                article = Article(
                    id=article_data['id'],
                    title=article_data['title'],
                    url=article_data['url'],
                    content=article_data['content'],
                    summary=article_data['summary'],
                    source=article_data['source'],
                    published_at=article_data['published'],
                    language=settings.DEFAULT_LANGUAGE
                )
                self.storage.store_article(article)
                
            total_articles += len(articles[:5])
            logger.info(f"Processed {len(articles[:5])} articles from {source}")
        
        logger.info(f"Total RSS articles stored: {total_articles}")

if __name__ == "__main__":
    pipeline = NewsIngestionPipeline()
    pipeline.run_full_ingestion()
