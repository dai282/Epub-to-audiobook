"""EPUB file parser for extracting text content."""

import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EPUBParser:
    """Parser for EPUB files to extract chapters and metadata."""
    
    def __init__(self, epub_path: str):
        """
        Initialize the EPUB parser.
        
        Args:
            epub_path: Path to the EPUB file
        """
        self.epub_path = epub_path
        self.book = None
        
    def parse_epub(self) -> List[Dict[str, str]]:
        """
        Parse the EPUB file and extract all chapters.
        
        Returns:
            List of dictionaries containing chapter title and text
            
        Raises:
            FileNotFoundError: If EPUB file doesn't exist
            Exception: If EPUB file is invalid or corrupted
        """
        try:
            self.book = epub.read_epub(self.epub_path)
        except FileNotFoundError:
            logger.error(f"EPUB file not found: {self.epub_path}")
            raise
        except Exception as e:
            logger.error(f"Error reading EPUB file: {e}")
            raise Exception(f"Invalid or corrupted EPUB file: {e}")
        
        chapters = []
        
        # Get all document items (chapters)
        items = list(self.book.get_items_of_type(ebooklib.ITEM_DOCUMENT))
        
        for i, item in enumerate(items):
            try:
                # Extract HTML content
                content = item.get_content()
                
                # Parse HTML and extract text
                soup = BeautifulSoup(content, 'lxml')
                
                # Remove script and style elements
                for script in soup(["script", "style"]):
                    script.decompose()
                
                # Get text
                text = soup.get_text()
                
                # Clean up whitespace
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                text = ' '.join(chunk for chunk in chunks if chunk)
                
                # Skip if empty
                if not text or len(text.strip()) < 50:
                    continue
                
                # Try to get chapter title
                title = self._extract_title(soup) or f"Chapter {len(chapters) + 1}"
                
                chapters.append({
                    'title': title,
                    'text': text
                })
                
                logger.info(f"Extracted: {title} ({len(text)} characters)")
                
            except Exception as e:
                logger.warning(f"Error processing item {i}: {e}")
                continue
        
        if not chapters:
            raise Exception("No readable content found in EPUB file")
        
        logger.info(f"Successfully extracted {len(chapters)} chapters")
        return chapters
    
    def _extract_title(self, soup: BeautifulSoup) -> Optional[str]:
        """
        Extract chapter title from HTML soup.
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            Chapter title or None
        """
        # Try different heading tags
        for tag in ['h1', 'h2', 'h3', 'title']:
            heading = soup.find(tag)
            if heading and heading.get_text().strip():
                return heading.get_text().strip()
        return None
    
    def get_metadata(self) -> Dict[str, str]:
        """
        Extract metadata from the EPUB file.
        
        Returns:
            Dictionary containing title, author, and language
        """
        if not self.book:
            try:
                self.book = epub.read_epub(self.epub_path)
            except Exception as e:
                logger.error(f"Error reading EPUB metadata: {e}")
                return {'title': 'Unknown', 'author': 'Unknown', 'language': 'en'}
        
        metadata = {
            'title': 'Unknown',
            'author': 'Unknown',
            'language': 'en'
        }
        
        try:
            # Get title
            title = self.book.get_metadata('DC', 'title')
            if title:
                metadata['title'] = title[0][0]
            
            # Get author
            author = self.book.get_metadata('DC', 'creator')
            if author:
                metadata['author'] = author[0][0]
            
            # Get language
            language = self.book.get_metadata('DC', 'language')
            if language:
                metadata['language'] = language[0][0]
                
        except Exception as e:
            logger.warning(f"Error extracting metadata: {e}")
        
        return metadata