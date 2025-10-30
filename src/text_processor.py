"""Text processing utilities for preparing text for TTS."""

import re
from typing import List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TextProcessor:
    """Process and prepare text for TTS conversion."""
    
    @staticmethod
    def clean_text(text: str) -> str:
        """
        Clean text for TTS processing.
        
        Args:
            text: Raw text to clean
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Remove multiple spaces
        text = re.sub(r' +', ' ', text)
        
        # Remove multiple newlines but preserve paragraph breaks
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        
        # Remove single newlines (join paragraphs)
        text = re.sub(r'(?<!\n)\n(?!\n)', ' ', text)
        
        # Fix common issues
        text = text.replace('\r', '')
        text = text.replace('\t', ' ')
        
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Handle common special characters
        replacements = {
            '"': '"',
            '"': '"',
            ''': "'",
            ''': "'",
            '–': '-',
            '—': '-',
            '…': '...',
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        # Remove excessive punctuation
        text = re.sub(r'\.{4,}', '...', text)
        text = re.sub(r'!{2,}', '!', text)
        text = re.sub(r'\?{2,}', '?', text)
        
        # Strip leading/trailing whitespace
        text = text.strip()
        
        return text
    
    @staticmethod
    def chunk_text(text: str, max_chars: int = 500) -> List[str]:
        """
        Split text into chunks suitable for TTS processing.
        
        Args:
            text: Text to split
            max_chars: Maximum characters per chunk
            
        Returns:
            List of text chunks
        """
        if not text:
            return []
        
        # First split by paragraph
        paragraphs = text.split('\n\n')
        chunks = []
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
            
            # If paragraph is short enough, add it as is
            if len(paragraph) <= max_chars:
                chunks.append(paragraph)
                continue
            
            # Otherwise, split by sentences
            sentences = re.split(r'(?<=[.!?])\s+', paragraph)
            current_chunk = ""
            
            for sentence in sentences:
                # If adding this sentence would exceed limit
                if len(current_chunk) + len(sentence) + 1 > max_chars:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                        current_chunk = ""
                    
                    # If single sentence is too long, split it
                    if len(sentence) > max_chars:
                        words = sentence.split()
                        temp_chunk = ""
                        
                        for word in words:
                            if len(temp_chunk) + len(word) + 1 > max_chars:
                                if temp_chunk:
                                    chunks.append(temp_chunk.strip())
                                temp_chunk = word
                            else:
                                temp_chunk += (" " + word) if temp_chunk else word
                        
                        if temp_chunk:
                            current_chunk = temp_chunk
                    else:
                        current_chunk = sentence
                else:
                    current_chunk += (" " + sentence) if current_chunk else sentence
            
            if current_chunk:
                chunks.append(current_chunk.strip())
        
        logger.info(f"Split text into {len(chunks)} chunks")
        return chunks
    
    @staticmethod
    def estimate_duration(text: str, words_per_minute: int = 150) -> float:
        """
        Estimate audio duration based on word count.
        
        Args:
            text: Text to estimate duration for
            words_per_minute: Average speaking rate
            
        Returns:
            Estimated duration in seconds
        """
        if not text:
            return 0.0
        
        word_count = len(text.split())
        duration_minutes = word_count / words_per_minute
        duration_seconds = duration_minutes * 60
        
        return duration_seconds
    
    @staticmethod
    def format_duration(seconds: float) -> str:
        """
        Format duration in seconds to readable string.
        
        Args:
            seconds: Duration in seconds
            
        Returns:
            Formatted duration string (e.g., "1h 23m 45s")
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        parts = []
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")
        if secs > 0 or not parts:
            parts.append(f"{secs}s")
        
        return " ".join(parts)