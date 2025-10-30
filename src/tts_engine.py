"""Kokoro TTS engine wrapper."""

import logging
from typing import Optional
from pathlib import Path
import soundfile as sf
import numpy as np

try:
    from kokoro import KPipeline
except ImportError:
    raise ImportError("Kokoro TTS not installed. Run: pip install kokoro")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class KokoroTTSEngine:
    """Wrapper for Kokoro TTS engine."""
    
    # Available voices in Kokoro
    AVAILABLE_VOICES = [
        'af_heart',  # Female, American English
        'af_bella',  # Female, American English
        'af_sarah',  # Female, American English
        'am_adam',   # Male, American English
        'am_michael',  # Male, American English
        'bf_emma',   # Female, British English
        'bf_isabella',  # Female, British English
        'bm_george',  # Male, British English
        'bm_lewis',  # Male, British English
    ]
    
    def __init__(self, lang_code: str = 'a', voice: str = 'af_heart'):
        """
        Initialize Kokoro TTS engine.
        
        Args:
            lang_code: Language code ('a' for American English, 'b' for British)
            voice: Voice name to use
        """
        self.lang_code = lang_code
        self.voice = voice
        self.pipeline = None
        
        try:
            logger.info(f"Initializing Kokoro TTS with voice: {voice}")
            self.pipeline = KPipeline(lang_code=lang_code)
            logger.info("Kokoro TTS initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing Kokoro TTS: {e}")
            logger.error("Make sure espeak-ng is installed on your system")
            raise
    
    def generate_speech(self, text: str, output_path: str) -> bool:
        """
        Generate speech from text and save to file.
        
        Args:
            text: Text to convert to speech
            output_path: Path to save the audio file
            
        Returns:
            True if successful, False otherwise
        """
        if not self.pipeline:
            logger.error("TTS pipeline not initialized")
            return False
        
        if not text or not text.strip():
            logger.warning("Empty text provided")
            return False
        
        try:
            # Generate audio
            generator = self.pipeline(text, voice=self.voice, speed=1.0)
            
            # Collect all audio chunks
            audio_chunks = []
            for _, _, audio in generator:
                audio_chunks.append(audio)
            
            # Concatenate all chunks
            if audio_chunks:
                full_audio = np.concatenate(audio_chunks)
                
                # Save to file
                output_path = Path(output_path)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                sf.write(str(output_path), full_audio, 24000)
                logger.debug(f"Saved audio to {output_path}")
                return True
            else:
                logger.warning("No audio generated")
                return False
                
        except Exception as e:
            logger.error(f"Error generating speech: {e}")
            return False
    
    def set_voice(self, voice: str) -> bool:
        """
        Change the voice.
        
        Args:
            voice: Voice name
            
        Returns:
            True if voice is valid, False otherwise
        """
        if voice in self.AVAILABLE_VOICES:
            self.voice = voice
            logger.info(f"Voice changed to: {voice}")
            return True
        else:
            logger.warning(f"Invalid voice: {voice}")
            return False
    
    @classmethod
    def get_available_voices(cls) -> list:
        """
        Get list of available voices.
        
        Returns:
            List of voice names
        """
        return cls.AVAILABLE_VOICES
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        # Cleanup if needed
        self.pipeline = None