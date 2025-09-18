import requests
import json
from datetime import datetime, timedelta
import time

class NewsAPIClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://newsapi.org/v2"
        
    def fetch_everything(self, query=None, sources=None, language='en', 
                        page_size=100, from_date=None):
        """Fetch articles using everything endpoint"""
        url = f"{self.base_url}/everything"
        
        params = {
            'apiKey': self.api_key,
            'pageSize': min(page_size, 100),  # API limit
            'language': language,
            'sortBy': 'publishedAt'
        }
        
        if query:
            params['q'] = query
        if sources:
            params['sources'] = sources
        if from_date:
            params['from'] = from_date.isoformat()
            
        response = requests.get(url, params=params)
        return response.json() if response.status_code == 200 else None
