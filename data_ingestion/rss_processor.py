import feedparser
from urllib.parse import urljoin
import hashlib

class RSSProcessor:
    def __init__(self):
        self.rss_feeds = {
            'bbc': 'http://feeds.bbci.co.uk/news/rss.xml',
            'cnn': 'http://rss.cnn.com/rss/edition.rss',
            'reuters': 'https://feeds.reuters.com/reuters/topNews',
            'techcrunch': 'https://techcrunch.com/feed/'
        }
    
    def fetch_feed(self, feed_url):
        """Parse RSS feed and extract articles"""
        feed = feedparser.parse(feed_url)
        articles = []
        
        for entry in feed.entries:
            article = {
                'title': entry.get('title', ''),
                'url': entry.get('link', ''),
                'published': entry.get('published', ''),
                'summary': entry.get('summary', ''),
                'source': feed.feed.get('title', 'Unknown'),
                'content': entry.get('content', [{}])[0].get('value', '') if entry.get('content') else ''
            }
            
            # Generate unique ID
            article['id'] = hashlib.md5(
                f"{article['url']}{article['published']}".encode()
            ).hexdigest()
            
            articles.append(article)
            
        return articles
