#!/usr/bin/env python3
"""
EPUB to Audiobook Converter
Converts EPUB files to audiobooks using Kokoro TTS
"""

import argparse
import sys
import logging
from pathlib import Path

from src.audio_generator import AudiobookGenerator
from src.tts_engine import KokoroTTSEngine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('audiobook_converter.log')
    ]
)
logger = logging.getLogger(__name__)


def print_banner():
    """Print welcome banner."""
    banner = """
    ╔═══════════════════════════════════════════════════════╗
    ║                                                       ║
    ║       EPUB to Audiobook Converter                    ║
    ║       Powered by Kokoro TTS                          ║
    ║                                                       ║
    ╚═══════════════════════════════════════════════════════╝
    """
    print(banner)


def list_voices():
    """List available voices and exit."""
    print("\nAvailable Voices:")
    print("-" * 40)
    voices = KokoroTTSEngine.get_available_voices()
    for voice in voices:
        print(f"  • {voice}")
    print("-" * 40)
    print(f"\nTotal: {len(voices)} voices available\n")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Convert EPUB files to audiobooks using Kokoro TTS',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s -i book.epub
  %(prog)s -i book.epub -o ./audiobooks -v am_adam
  %(prog)s -i book.epub --combine -f mp3
  %(prog)s --list-voices
        """
    )
    
    parser.add_argument(
        '-i', '--input',
        type=str,
        help='Path to EPUB file (required unless --list-voices)'
    )
    
    parser.add_argument(
        '-o', '--output',
        type=str,
        default='./output',
        help='Output directory (default: ./output)'
    )
    
    parser.add_argument(
        '-v', '--voice',
        type=str,
        default='af_heart',
        help='Kokoro voice name (default: af_heart)'
    )
    
    parser.add_argument(
        '-c', '--combine',
        action='store_true',
        help='Combine all chapters into a single file'
    )
    
    parser.add_argument(
        '-f', '--format',
        type=str,
        choices=['wav', 'mp3'],
        default='mp3',
        help='Output format for combined file (default: mp3)'
    )
    
    parser.add_argument(
        '--list-voices',
        action='store_true',
        help='List available voices and exit'
    )
    
    args = parser.parse_args()
    
    # Handle list-voices
    if args.list_voices:
        list_voices()
        return 0
    
    # Validate required arguments
    if not args.input:
        parser.error("the following arguments are required: -i/--input")
    
    print_banner()
    
    # Validate input file
    input_path = Path(args.input)
    if not input_path.exists():
        logger.error(f"Input file not found: {args.input}")
        return 1
    
    if input_path.suffix.lower() != '.epub':
        logger.error(f"Input file must be an EPUB file")
        return 1
    
    # Validate voice
    available_voices = KokoroTTSEngine.get_available_voices()
    if args.voice not in available_voices:
        logger.error(f"Invalid voice: {args.voice}")
        logger.info(f"Available voices: {', '.join(available_voices)}")
        logger.info("Use --list-voices to see all available voices")
        return 1
    
    # Create output directory
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Input file: {input_path}")
    logger.info(f"Output directory: {output_dir}")
    logger.info(f"Voice: {args.voice}")
    
    try:
        # Generate audiobook
        generator = AudiobookGenerator(
            epub_path=str(input_path),
            output_dir=str(output_dir),
            voice=args.voice
        )
        
        chapter_files = generator.generate_audiobook()
        
        if not chapter_files:
            logger.error("No audio files were generated")
            return 1
        
        # Combine chapters if requested
        if args.combine:
            combined_filename = f"{input_path.stem}_complete.{args.format}"
            combined_path = output_dir / combined_filename
            
            success = generator.combine_chapters(
                chapter_files,
                str(combined_path)
            )
            
            if success:
                logger.info(f"\n✓ Combined audiobook: {combined_path}")
            else:
                logger.warning("Failed to combine chapters, but individual files are available")
        
        # Success summary
        print("\n" + "="*60)
        print("✓ CONVERSION COMPLETE!")
        print("="*60)
        print(f"Generated {len(chapter_files)} chapter files")
        print(f"Output location: {output_dir}")
        
        if args.combine and success:
            print(f"Combined file: {combined_path}")
        
        print("="*60 + "\n")
        
        return 0
        
    except KeyboardInterrupt:
        logger.info("\nConversion cancelled by user")
        return 130
    except Exception as e:
        logger.error(f"Error during conversion: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())