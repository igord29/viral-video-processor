# Quick Start Guide

Get started with Viral Video Processor in 5 minutes!

## 1. Initial Setup (One-time)

### Windows
```bash
# Run the setup script
setup.bat
```

### macOS/Linux
```bash
# Make setup script executable
chmod +x setup.sh

# Run setup
./setup.sh
```

### Manual Setup
```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.template .env
```

## 2. Configure API Key

Edit `.env` file and add your Anthropic API key:

```env
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

Get your key from: https://console.anthropic.com/

## 3. Verify Installation

```bash
python app.py --help
```

You should see the command list!

## 4. Try Your First Video

### Example 1: Download and Analyze
```bash
python app.py download "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

This will:
1. Show video info
2. Ask for confirmation
3. Download the video
4. Ask if you want to analyze it
5. Transcribe and analyze for viral clips
6. Show top clip candidates

### Example 2: Search for Viral Videos
```bash
python app.py search "python tutorial" --limit 5
```

This will show you top 5 viral Python tutorials!

### Example 3: Analyze Existing Video
```bash
python app.py analyze path/to/video.mp4
```

## Common Commands

### Download with auto-analysis
```bash
python app.py download <URL> --auto-analyze
```

### Skip confirmation prompts
```bash
python app.py download <URL> --skip-review
```

### Use better transcription quality
```bash
python app.py download <URL> --model medium
```

### View configuration
```bash
python app.py config
```

## Tips for Best Results

1. **Start Small**: Try with a 5-10 minute video first
2. **Use Base Model**: Good balance of speed and accuracy
3. **Check Viral Criteria**: Videos with 100k+ views work best
4. **Save Results**: Always save analysis when prompted
5. **Adjust Settings**: Edit `.env` to customize clip duration

## Troubleshooting

### Command not found
Make sure you activated the virtual environment:
```bash
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### Missing API Key
Edit `.env` and add `ANTHROPIC_API_KEY=your-key-here`

### FFmpeg not found
Install ffmpeg:
```bash
# Windows (with Chocolatey)
choco install ffmpeg

# macOS
brew install ffmpeg

# Linux
sudo apt install ffmpeg
```

## What to Expect

### Processing Times (approximate)
- **Download**: 30s - 2min (depending on video length)
- **Transcription**:
  - tiny model: ~1x video length
  - base model: ~2x video length
  - medium model: ~4x video length
- **Analysis**: 10-30s per clip (using Claude API)

### Example Output

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 Top Clip Candidates
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

┏━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━┓
┃ #  ┃ Time          ┃ Duration ┃ Score  ┃ Reason      ┃
┡━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━┩
│ 1  │ 02:15 - 02:45 │ 30.0s    │ 8.5/10 │ Strong hook │
│ 2  │ 05:30 - 06:00 │ 30.0s    │ 8.2/10 │ High energy │
│ 3  │ 08:45 - 09:15 │ 30.0s    │ 7.8/10 │ Emotional   │
└────┴───────────────┴──────────┴────────┴─────────────┘
```

## Next Steps

1. **Review the README**: See `README.md` for full documentation
2. **Customize Settings**: Edit `.env` for your preferences
3. **Explore Features**: Try search, analyze, and download commands
4. **Save Your Work**: Always save analysis results for reference

## Need Help?

- Check `README.md` for detailed documentation
- Run `python app.py COMMAND --help` for command-specific help
- Review the troubleshooting section above

Happy processing! 🎬✨
