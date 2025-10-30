"""Main audiobook generation coordinator."""

import logging
from pathlib import Path
from typing import List, Optional
from tqdm import tqdm
import time

from .epub_parser import EPUBParser
from .text_processor import TextProcessor
from .tts_engine import KokoroTTSEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AudiobookGenerator:
    """Generate audiobooks from EPUB files using Kokoro TTS."""
    
    def __init__(self, epub_path: str, output_dir: str, voice: str = 'af_heart'):
        """
        Initialize the audiobook generator.
        
        Args:
            epub_path: Path to EPUB file
            output_dir: Directory for output audio files
            voice: Kokoro voice to use
        """
        self.epub_path = Path(epub_path)
        self.output_dir = Path(output_dir)
        self.voice = voice
        
        # Validate input
        if not self.epub_path.exists():
            raise FileNotFoundError(f"EPUB file not found: {epub_path}")
        
        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.epub_parser = EPUBParser(str(self.epub_path))
        self.text_processor = TextProcessor()
        self.tts_engine = None
        
    def generate_audiobook(self) -> List[str]:
        """
        Generate audiobook from EPUB file.
        
        Returns:
            List of generated audio file paths
        """
        logger.info(f"Starting audiobook generation from: {self.epub_path}")
        
        # Parse EPUB
        logger.info("Parsing EPUB file...")
        chapters = self.epub_parser.parse_epub()
        metadata = self.epub_parser.get_metadata()
        
        logger.info(f"Book: {metadata['title']} by {metadata['author']}")
        logger.info(f"Found {len(chapters)} chapters")
        
        # Initialize TTS engine
        logger.info("Initializing TTS engine...")
        self.tts_engine = KokoroTTSEngine(voice=self.voice)
        
        # Generate audio for each chapter
        output_files = []
        total_duration = 0
        
        for i, chapter in enumerate(tqdm(chapters, desc="Generating audiobook")):
            try:
                chapter_num = i + 1
                chapter_title = chapter['title']
                chapter_text = chapter['text']
                
                logger.info(f"\nProcessing Chapter {chapter_num}: {chapter_title}")
                
                # Clean text
                cleaned_text = self.text_processor.clean_text(chapter_text)
                
                if not cleaned_text:
                    logger.warning(f"Skipping empty chapter: {chapter_title}")
                    continue
                
                # Estimate duration
                duration = self.text_processor.estimate_duration(cleaned_text)
                total_duration += duration
                duration_str = self.text_processor.format_duration(duration)
                logger.info(f"Estimated duration: {duration_str}")
                
                # Chunk text for better processing
                chunks = self.text_processor.chunk_text(cleaned_text, max_chars=500)
                logger.info(f"Split into {len(chunks)} chunks")
                
                # Generate audio for each chunk
                chapter_audio_files = []
                for j, chunk in enumerate(chunks):
                    chunk_file = self.output_dir / f"chapter_{chapter_num:03d}_chunk_{j:03d}.wav"
                    
                    success = self.tts_engine.generate_speech(chunk, str(chunk_file))
                    
                    if success:
                        chapter_audio_files.append(str(chunk_file))
                    else:
                        logger.warning(f"Failed to generate audio for chunk {j}")
                
                # Combine chunks into single chapter file
                if chapter_audio_files:
                    chapter_file = self.output_dir / f"chapter_{chapter_num:03d}_{self._sanitize_filename(chapter_title)}.wav"
                    self._combine_audio_files(chapter_audio_files, str(chapter_file))
                    output_files.append(str(chapter_file))
                    
                    # Clean up chunk files
                    for chunk_file in chapter_audio_files:
                        try:
                            Path(chunk_file).unlink()
                        except:
                            pass
                    
                    logger.info(f"✓ Chapter {chapter_num} completed")
                
            except Exception as e:
                logger.error(f"Error processing chapter {i+1}: {e}")
                continue
        
        # Summary
        total_duration_str = self.text_processor.format_duration(total_duration)
        logger.info(f"\n{'='*60}")
        logger.info(f"Audiobook generation complete!")
        logger.info(f"Generated {len(output_files)} chapter files")
        logger.info(f"Estimated total duration: {total_duration_str}")
        logger.info(f"Output directory: {self.output_dir}")
        logger.info(f"{'='*60}\n")
        
        return output_files
    
    def combine_chapters(self, chapter_files: List[str], output_file: str) -> bool:
        """
        Combine all chapter audio files into a single file.
        
        Args:
            chapter_files: List of chapter audio file paths
            output_file: Path for combined output file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            from pydub import AudioSegment
            from pydub.silence import Silence
            
            logger.info("Combining chapters into single file...")
            
            combined = AudioSegment.empty()
            silence = AudioSegment.silent(duration=2000)  # 2 seconds silence
            
            for i, chapter_file in enumerate(tqdm(chapter_files, desc="Combining")):
                try:
                    audio = AudioSegment.from_wav(chapter_file)
                    combined += audio
                    
                    # Add silence between chapters (except after last chapter)
                    if i < len(chapter_files) - 1:
                        combined += silence
                        
                except Exception as e:
                    logger.warning(f"Error loading {chapter_file}: {e}")
                    continue
            
            # Export
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Determine format from extension
            file_format = output_path.suffix[1:].lower()
            if file_format not in ['wav', 'mp3', 'ogg']:
                file_format = 'mp3'
            
            logger.info(f"Exporting as {file_format.upper()}...")
            combined.export(str(output_path), format=file_format)
            
            logger.info(f"✓ Combined audiobook saved to: {output_path}")
            return True
            
        except ImportError:
            logger.error("pydub not installed. Install with: pip install pydub")
            logger.error("Also install ffmpeg for MP3 support")
            return False
        except Exception as e:
            logger.error(f"Error combining chapters: {e}")
            return False
    
    def _combine_audio_files(self, audio_files: List[str], output_file: str) -> bool:
        """
        Combine multiple audio files into one.
        
        Args:
            audio_files: List of audio file paths
            output_file: Output file path
            
        Returns:
            True if successful
        """
        try:
            import soundfile as sf
            import numpy as np
            
            combined_audio = []
            
            for audio_file in audio_files:
                data, samplerate = sf.read(audio_file)
                combined_audio.append(data)
            
            # Concatenate
            full_audio = np.concatenate(combined_audio)
            
            # Save
            sf.write(output_file, full_audio, samplerate)
            return True
            
        except Exception as e:
            logger.error(f"Error combining audio files: {e}")
            return False
    
    @staticmethod
    def _sanitize_filename(filename: str) -> str:
        """
        Sanitize filename to remove invalid characters.
        
        Args:
            filename: Original filename
            
        Returns:
            Sanitized filename
        """
        # Remove invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '')
        
        # Limit length
        if len(filename) > 100:
            filename = filename[:100]
        
        # Replace spaces with underscores
        filename = filename.replace(' ', '_')
        
        return filename