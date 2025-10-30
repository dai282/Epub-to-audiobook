# 📚 EPUB to Audiobook Converter

Convert your EPUB ebooks into high-quality audiobooks using the powerful Kokoro TTS engine. Fast, free, and runs completely offline on your local machine.

## ✨ Features

- 🎙️ **Natural-sounding voices** - Choose from 9 professional voice options
- 📖 **Automatic chapter detection** - Smart parsing of EPUB structure
- ⚡ **Fast processing** - Lightweight 82M parameter model
- 🎵 **Multiple formats** - Export as WAV or MP3
- 🔊 **High-quality audio** - 24kHz sample rate
- 💻 **100% local** - No internet required, complete privacy
- 🆓 **Completely free** - Open source with permissive licensing
- 📊 **Progress tracking** - Real-time conversion progress and estimates

## 🎬 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Convert an EPUB file
python main.py -i yourbook.epub

# Use a different voice and combine chapters
python main.py -i yourbook.epub -v am_adam --combine -f mp3
```

## 📋 Requirements

- **Python** 3.9 or higher
- **espeak-ng** (text-to-phoneme conversion)
- **ffmpeg** (optional, for MP3 export)

## 🔧 Installation

### Step 1: Install espeak-ng

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install espeak-ng
```

**macOS:**
```bash
brew install espeak-ng
```

**Windows:**
1. Download the installer from [espeak-ng releases](https://github.com/espeak-ng/espeak-ng/releases)
2. Run the `.msi` installer (e.g., `espeak-ng-X.XX.X-x64.msi`)
3. The installer automatically adds espeak-ng to your PATH

### Step 2: Install Python dependencies

```bash
# Clone this repository
git clone https://github.com/yourusername/epub-to-audiobook.git
cd epub-to-audiobook

# Install required packages
pip install -r requirements.txt
```

### Step 3: Install ffmpeg (Optional - for MP3 export)

**Linux:**
```bash
sudo apt-get install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Windows:**
Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH

## 🚀 Usage

### Basic Commands

**Convert an EPUB file:**
```bash
python main.py -i book.epub
```

**Specify output directory:**
```bash
python main.py -i book.epub -o ./my_audiobooks
```

**Choose a different voice:**
```bash
python main.py -i book.epub -v af_bella
```

**Combine all chapters into one file:**
```bash
python main.py -i book.epub --combine
```

**Export as MP3:**
```bash
python main.py -i book.epub --combine -f mp3
```

**List all available voices:**
```bash
python main.py --list-voices
```

### Complete Example

```bash
python main.py -i "The Great Gatsby.epub" \
  -o ./audiobooks \
  -v am_michael \
  --combine \
  -f mp3
```

## 🎤 Available Voices

### American English
| Voice | Gender | Description |
|-------|--------|-------------|
| `af_heart` | Female | Clear, warm (default) |
| `af_bella` | Female | Smooth, professional |
| `af_sarah` | Female | Friendly, expressive |
| `am_adam` | Male | Deep, confident |
| `am_michael` | Male | Clear, articulate |

### British English
| Voice | Gender | Description |
|-------|--------|-------------|
| `bf_emma` | Female | Refined, clear |
| `bf_isabella` | Female | Elegant, smooth |
| `bm_george` | Male | Distinguished, warm |
| `bm_lewis` | Male | Professional, clear |

## 🎛️ Command-Line Options

```
usage: main.py [-h] [-i INPUT] [-o OUTPUT] [-v VOICE] [-c] 
               [-f {wav,mp3}] [--list-voices]

options:
  -h, --help            Show this help message and exit
  -i, --input INPUT     Path to EPUB file (required)
  -o, --output OUTPUT   Output directory (default: ./output)
  -v, --voice VOICE     Voice name (default: af_heart)
  -c, --combine         Combine all chapters into single file
  -f, --format {wav,mp3}
                        Output format for combined file (default: mp3)
  --list-voices         List all available voices and exit
```

## 📁 Output Structure

### Individual Chapter Files (default)
```
output/
├── chapter_001_Introduction.wav
├── chapter_002_Chapter_One.wav
├── chapter_003_Chapter_Two.wav
└── ...
```

### Combined Audiobook (with --combine)
```
output/
├── chapter_001_Introduction.wav
├── chapter_002_Chapter_One.wav
├── ...
└── BookTitle_complete.mp3  ← All chapters in one file
```

## 🏗️ Project Structure

```
epub-to-audiobook/
├── src/
│   ├── __init__.py              # Package initialization
│   ├── epub_parser.py           # EPUB parsing and text extraction
│   ├── text_processor.py        # Text cleaning and chunking
│   ├── tts_engine.py            # Kokoro TTS integration
│   └── audio_generator.py       # Audiobook generation coordinator
├── main.py                      # CLI entry point
├── requirements.txt             # Python dependencies
├── README.md                    # This file
├── LICENSE                      # MIT License
└── .gitignore                   # Git ignore rules
```

## 🔍 How It Works

1. **📖 EPUB Parsing** - Extracts text content and chapter structure from EPUB files
2. **✂️ Text Processing** - Cleans and optimizes text for natural speech synthesis
3. **🎙️ Speech Generation** - Converts text to speech using Kokoro TTS
4. **🎵 Audio Assembly** - Saves chapters individually or combines into single file
5. **💾 Export** - Outputs in your chosen format (WAV or MP3)

## ⚡ Performance

- **Processing Speed**: ~10-30 minutes for a 300-page book
- **Audio Quality**: 24kHz sample rate, high fidelity
- **Disk Space**: ~1-2 MB per minute of audio (WAV format)
- **Memory Usage**: 1-2 GB RAM during conversion
- **GPU Acceleration**: Automatic if CUDA-capable GPU is available

## 🛠️ Troubleshooting

### "espeak-ng not found" error

**Solution**: Ensure espeak-ng is installed and accessible:
```bash
# Test installation
espeak-ng --version
```

If not found, reinstall following the installation instructions above.

### "No module named 'kokoro'" error

**Solution**: Install dependencies:
```bash
pip install -r requirements.txt
```

### MP3 export fails

**Solution**: Install ffmpeg:
```bash
# Linux
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg

# Windows - download from ffmpeg.org
```

### Out of memory errors

**Solution**: For very large books, generate chapters individually without `--combine`:
```bash
python main.py -i largebook.epub  # Creates separate chapter files
```

### Poor audio quality or robotic voice

**Solutions**:
- Try different voices using `-v` flag
- Ensure your EPUB has clean, well-formatted text
- Check that espeak-ng is properly installed

### Processing is very slow

**Solutions**:
- Close other applications to free up resources
- Check if GPU acceleration is being used (automatic with CUDA)
- Consider processing in smaller chunks (individual chapters)

## 🎓 Advanced Usage

### Using as a Python Library

```python
from src.audio_generator import AudiobookGenerator

# Initialize generator
generator = AudiobookGenerator(
    epub_path="path/to/book.epub",
    output_dir="./audiobooks",
    voice="af_bella"
)

# Generate audiobook
chapter_files = generator.generate_audiobook()

# Optionally combine chapters
generator.combine_chapters(
    chapter_files,
    "complete_audiobook.mp3"
)
```

### Batch Processing Multiple Books

```bash
# Create a simple bash script
for book in *.epub; do
    python main.py -i "$book" -o "./audiobooks" -v af_heart --combine -f mp3
done
```

### Custom Text Processing

Edit `src/text_processor.py` to customize:
- Text cleaning rules
- Chunk size for TTS processing
- Speaking rate estimation
- Duration calculations

## ⚠️ Limitations

- Only supports EPUB format (no PDF, MOBI, etc.)
- Currently supports English voices only
- Pronunciation of uncommon words may not be perfect
- Very large books (1000+ pages) require significant processing time
- No built-in DRM removal (input files must be DRM-free)

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### Third-Party Licenses

- **Kokoro TTS**: Apache 2.0 License
- **ebooklib**: AGPL-3.0 License
- **Other dependencies**: See individual package licenses

## 🙏 Acknowledgments

- [Kokoro TTS](https://github.com/hexgrad/kokoro) - Exceptional open-source TTS engine
- [ebooklib](https://github.com/aerkalov/ebooklib) - Robust EPUB parsing library
- [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/) - HTML/XML parsing
- All contributors and testers who make this project better

## 📊 Changelog

### Version 1.0.0 (Current)
- Initial release
- EPUB to audiobook conversion
- 9 English voices (American & British)
- Automatic chapter detection
- WAV and MP3 export
- Command-line interface
- Progress tracking
- Duration estimation

---

**Made with ❤️ by Dai**

**Star ⭐ this repo if you find it useful!**

---

## 📸 Screenshots

```
╔═══════════════════════════════════════════════════════╗
║                                                       ║
║       EPUB to Audiobook Converter                    ║
║       Powered by Kokoro TTS                          ║
║                                                       ║
╚═══════════════════════════════════════════════════════╝

Input file: example.epub
Output directory: ./output
Voice: af_heart

Parsing EPUB file...
Book: Example Book by John Doe
Found 15 chapters

Processing Chapter 1: Introduction
Estimated duration: 5m 23s
Split into 12 chunks
✓ Chapter 1 completed

[Progress bar: ████████░░ 80%]

Generating audiobook: 12/15 chapters complete
```

