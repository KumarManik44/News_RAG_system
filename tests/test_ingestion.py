import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_ingestion.news_api_client import NewsAPIClient
from data_ingestion.rss_processor import RSSProcessor
from data_ingestion.article_storage import ArticleStorage, Article
from config.settings import settings
from datetime import datetime, timedelta
import hashlib

def test_ingestion():
    # Your previous test code here, but using imported classes
    pass

if __name__ == "__main__":
    test_ingestion()
