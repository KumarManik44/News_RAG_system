import re
from typing import List, Dict, Optional
from dataclasses import dataclass

@dataclass
class TextChunk:
    content: str
    chunk_id: str
    article_id: str
    start_pos: int
    end_pos: int
    chunk_index: int
    metadata: Optional[Dict] = None

class TextChunker:
    def __init__(self, 
                 chunk_size: int = 512,  # Optimal for most embedding models
                 overlap_size: int = 50,  # Maintain context continuity
                 min_chunk_size: int = 100):
        self.chunk_size = chunk_size
        self.overlap_size = overlap_size
        self.min_chunk_size = min_chunk_size
        
        # Sentence boundary patterns for better splitting
        self.sentence_endings = re.compile(r'[.!?]+\s+')
        
    def chunk_by_sentences(self, text: str, article_id: str) -> List[TextChunk]:
        """Chunk text by sentence boundaries with overlap"""
        if not text or len(text.strip()) < self.min_chunk_size:
            return []
            
        # Split into sentences while keeping separators
        sentences = self.sentence_endings.split(text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        chunks = []
        current_chunk = ""
        current_sentences = []
        chunk_index = 0
        start_pos = 0
        
        for i, sentence in enumerate(sentences):
            # Check if adding this sentence exceeds chunk size
            potential_chunk = current_chunk + " " + sentence if current_chunk else sentence
            
            if len(potential_chunk) > self.chunk_size and current_chunk:
                # Create chunk from current sentences
                chunk = self._create_chunk(
                    content=current_chunk,
                    article_id=article_id,
                    chunk_index=chunk_index,
                    start_pos=start_pos
                )
                chunks.append(chunk)
                
                # Calculate overlap for next chunk
                overlap_sentences = self._get_overlap_sentences(
                    current_sentences, 
                    self.overlap_size
                )
                
                # Start new chunk with overlap
                current_chunk = " ".join(overlap_sentences)
                current_sentences = overlap_sentences.copy()
                chunk_index += 1
                start_pos = len(text) - len(current_chunk)
            
            # Add current sentence
            current_chunk = potential_chunk
            current_sentences.append(sentence)
        
        # Add final chunk if it has content
        if current_chunk and len(current_chunk) >= self.min_chunk_size:
            chunk = self._create_chunk(
                content=current_chunk,
                article_id=article_id,
                chunk_index=chunk_index,
                start_pos=start_pos
            )
            chunks.append(chunk)
            
        return chunks
    
    def chunk_by_fixed_size(self, text: str, article_id: str) -> List[TextChunk]:
        """Fallback chunking by fixed character size"""
        chunks = []
        chunk_index = 0
        
        for i in range(0, len(text), self.chunk_size - self.overlap_size):
            chunk_text = text[i:i + self.chunk_size]
            
            if len(chunk_text) >= self.min_chunk_size:
                chunk = self._create_chunk(
                    content=chunk_text,
                    article_id=article_id,
                    chunk_index=chunk_index,
                    start_pos=i
                )
                chunks.append(chunk)
                chunk_index += 1
                
        return chunks
    
    def _create_chunk(self, content: str, article_id: str, 
                     chunk_index: int, start_pos: int) -> TextChunk:
        """Create a TextChunk object with metadata"""
        chunk_id = f"{article_id}_chunk_{chunk_index}"
        
        return TextChunk(
            content=content.strip(),
            chunk_id=chunk_id,
            article_id=article_id,
            start_pos=start_pos,
            end_pos=start_pos + len(content),
            chunk_index=chunk_index,
            metadata={
                'word_count': len(content.split()),
                'char_count': len(content)
            }
        )
    
    def _get_overlap_sentences(self, sentences: List[str], 
                              target_overlap: int) -> List[str]:
        """Get sentences for overlap that fit within target size"""
        if not sentences:
            return []
            
        overlap_sentences = []
        overlap_length = 0
        
        # Start from the end and work backwards
        for sentence in reversed(sentences):
            if overlap_length + len(sentence) <= target_overlap:
                overlap_sentences.insert(0, sentence)
                overlap_length += len(sentence)
            else:
                break
                
        return overlap_sentences
