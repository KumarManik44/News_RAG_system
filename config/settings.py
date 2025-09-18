import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    # API Keys
    NEWSAPI_KEY = os.getenv('NEWSAPI_KEY', 'your_newsapi_key_here')
    
    # Database
    DATABASE_PATH = os.getenv('DATABASE_PATH', 'news_articles.db')
    
    # RSS Feeds
    RSS_FEEDS = {
        'bbc': 'http://feeds.bbci.co.uk/news/rss.xml',
        'cnn': 'http://rss.cnn.com/rss/edition.rss',
        'reuters': 'https://feeds.reuters.com/reuters/topNews',
        'techcrunch': 'https://techcrunch.com/feed/'
    }
    
    # Processing settings
    DEFAULT_LANGUAGE = 'en'
    DEFAULT_PAGE_SIZE = 10
    
settings = Settings()
