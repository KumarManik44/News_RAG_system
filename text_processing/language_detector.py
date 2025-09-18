from langdetect import detect, detect_langs
from langdetect.lang_detect_exception import LangDetectException
from typing import Tuple, Optional, List, Dict

class LanguageDetector:
    def __init__(self):
        # Map ISO codes to readable names
        self.language_names = {
            'en': 'English',
            'es': 'Spanish', 
            'fr': 'French',
            'de': 'German',
            'it': 'Italian',
            'pt': 'Portuguese',
            'ru': 'Russian',
            'zh-cn': 'Chinese (Simplified)',
            'ja': 'Japanese',
            'ko': 'Korean',
            'ar': 'Arabic',
            'hi': 'Hindi'
        }
        
    def detect_language(self, text: str) -> Tuple[Optional[str], float]:
        """Detect primary language of text with confidence score"""
        if not text or len(text.strip()) < 10:
            return None, 0.0
            
        try:
            # Get detailed language probabilities
            languages = detect_langs(text)
            
            if languages:
                primary_lang = languages[0]
                return primary_lang.lang, primary_lang.prob
            else:
                return None, 0.0
                
        except LangDetectException:
            # Fallback to simple detection
            try:
                lang = detect(text)
                return lang, 0.8  # Assume reasonable confidence
            except:
                return 'en', 0.5  # Default to English with low confidence
    
    def is_english_dominant(self, text: str, threshold: float = 0.7) -> bool:
        """Check if text is predominantly English"""
        lang, confidence = self.detect_language(text)
        return lang == 'en' and confidence >= threshold
    
    def get_language_name(self, lang_code: str) -> str:
        """Convert language code to readable name"""
        return self.language_names.get(lang_code, lang_code.upper())
