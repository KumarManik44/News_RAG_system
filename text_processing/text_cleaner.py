import re
import html
from typing import List, Optional
import unicodedata

class TextCleaner:
    def __init__(self):
        # Common patterns to remove
        self.html_pattern = re.compile(r'<[^>]+>')
        self.url_pattern = re.compile(r'https?://[^\s]+')
        self.email_pattern = re.compile(r'\S+@\S+')
        self.extra_whitespace = re.compile(r'\s+')
        
        # News-specific patterns
        self.byline_pattern = re.compile(r'^By\s+[A-Za-z\s]+\s*[-–]\s*', re.MULTILINE)
        self.timestamp_pattern = re.compile(r'\d{1,2}:\d{2}\s*(AM|PM|am|pm)')
        self.copyright_pattern = re.compile(r'©.*?\d{4}.*?$', re.MULTILINE)
        
    def clean_text(self, text: str) -> str:
        """Clean and normalize text content"""
        if not text or not text.strip():
            return ""
        
        # Decode HTML entities
        text = html.unescape(text)
        
        # Remove HTML tags
        text = self.html_pattern.sub(' ', text)
        
        # Remove URLs and emails
        text = self.url_pattern.sub(' ', text)
        text = self.email_pattern.sub(' ', text)
        
        # Remove news-specific patterns
        text = self.byline_pattern.sub('', text)
        text = self.timestamp_pattern.sub('', text)
        text = self.copyright_pattern.sub('', text)
        
        # Normalize unicode characters
        text = unicodedata.normalize('NFKD', text)
        
        # Clean whitespace
        text = self.extra_whitespace.sub(' ', text)
        text = text.strip()
        
        return text
    
    def extract_sentences(self, text: str) -> List[str]:
        """Split text into sentences for better processing"""
        # Simple sentence splitting (can be enhanced with spaCy/NLTK)
        sentences = re.split(r'[.!?]+', text)
        
        # Clean and filter sentences
        cleaned_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 10:  # Filter very short sentences
                cleaned_sentences.append(sentence)
        
        return cleaned_sentences
