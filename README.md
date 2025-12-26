# Viral Video Processor

A Python CLI tool for downloading, analyzing, and processing viral videos with AI-powered engagement analysis and clip generation.

## Features

- **Multi-Platform Video Download**: Download videos from YouTube, TikTok, Twitch, and other platforms using yt-dlp
- **Video Metadata Display**: Preview video information before downloading
- **AI-Powered Transcription**: Automatic transcription using OpenAI's Whisper
- **Engagement Analysis**: Use Claude API to analyze transcript segments for viral potential
- **Smart Clip Detection**: Identify the most engaging moments based on:
  - Hook quality (attention-grabbing opening)
  - Emotional impact (excitement, curiosity, humor)
  - Information density (valuable content)
  - Pacing (energy and momentum)
- **Interactive Review Workflow**: Review and approve videos and clips before processing
- **Viral Video Search**: Find trending videos by engagement metrics

## Installation

### Prerequisites

1. **Python 3.8+** installed
2. **ffmpeg** installed (required for video processing)

#### Installing ffmpeg

**Windows:**
```bash
# Using Chocolatey
choco install ffmpeg

# Or download from: https://ffmpeg.org/download.html
```

**macOS:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt update
sudo apt install ffmpeg
```

### Setup

1. **Clone or navigate to the project directory**

2. **Create a virtual environment** (recommended):
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

3. **Install Python dependencies**:
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**:
```bash
# Copy the template
cp .env.template .env

# Edit .env and add your API keys
```

Required API keys:
- `ANTHROPIC_API_KEY`: Get from [Anthropic Console](https://console.anthropic.com/)
- `REPLICATE_API_TOKEN`: (Optional) Get from [Replicate](https://replicate.com/)

## Usage

### Basic Commands

#### Download and Analyze a Video

```bash
python app.py download <VIDEO_URL>
```

Example:
```bash
python app.py download "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

**Workflow:**
1. Fetches video information
2. Displays metadata (title, views, likes, duration)
3. Asks for confirmation to download
4. Downloads the video
5. Asks if you want to analyze for viral clips
6. Transcribes the video
7. Analyzes engagement potential using AI
8. Shows top clip candidates with scores

#### Analyze an Existing Video

```bash
python app.py analyze <VIDEO_PATH>
```

Example:
```bash
python app.py analyze downloads/my_video.mp4
```

#### Search for Viral Videos

```bash
python app.py search "your search query" --limit 10 --min-views 100000
```

Example:
```bash
python app.py search "ai tutorials" --limit 5 --min-views 500000
```

#### View Configuration

```bash
python app.py config
```

### Advanced Options

#### Download with Options

```bash
# Skip review prompts
python app.py download <URL> --skip-review

# Auto-analyze after download
python app.py download <URL> --auto-analyze

# Use different Whisper model
python app.py download <URL> --model small
```

**Whisper Model Options:**
- `tiny`: Fastest, least accurate
- `base`: Good balance (default)
- `small`: Better accuracy
- `medium`: High accuracy, slower
- `large`: Best accuracy, slowest

#### Analyze with Options

```bash
# Use larger Whisper model for better accuracy
python app.py analyze video.mp4 --model medium

# Skip clip review confirmation
python app.py analyze video.mp4 --skip-review
```

## Configuration

Edit `.env` file to customize settings:

```env
# API Keys
ANTHROPIC_API_KEY=your_key_here
REPLICATE_API_TOKEN=your_token_here

# Paths
DOWNLOAD_PATH=./downloads
VIDEO_PATH=./videos
CLIPS_PATH=./clips

# Processing Settings
MAX_CLIP_DURATION=60      # Maximum clip length in seconds
MIN_CLIP_DURATION=15      # Minimum clip length in seconds
TOP_CLIPS_TO_SHOW=10      # Number of top clips to display
```

## How It Works

### 1. Video Download
Uses `yt-dlp` to download videos from multiple platforms with best quality settings.

### 2. Transcription
OpenAI's Whisper model transcribes audio with word-level timestamps for precise clip timing.

### 3. Engagement Analysis
Claude AI analyzes each potential clip segment based on:

- **Hook Quality (30%)**: Does it grab attention immediately?
- **Emotional Impact (30%)**: Does it trigger emotions?
- **Information Density (20%)**: Is there valuable content?
- **Pacing (20%)**: Does it maintain energy?

Each clip receives a score from 1-10, with detailed reasoning.

### 4. Clip Ranking
Clips are sorted by engagement score, showing you the most viral-worthy moments first.

## Project Structure

```
viral-video-processor/
├── app.py                      # Main CLI application
├── requirements.txt            # Python dependencies
├── .env.template              # Environment template
├── README.md                  # This file
├── src/
│   ├── downloader/            # Video downloading
│   │   └── video_downloader.py
│   ├── transcription/         # Audio transcription
│   │   └── whisper_transcriber.py
│   ├── analysis/              # Engagement analysis
│   │   └── engagement_analyzer.py
│   └── utils/                 # Utilities
│       ├── config.py          # Configuration
│       └── display.py         # CLI display helpers
├── downloads/                 # Downloaded videos
├── videos/                    # Processed videos
└── clips/                     # Generated clips
```

## Examples

### Example 1: Download and Analyze a Tutorial

```bash
python app.py download "https://www.youtube.com/watch?v=example"
```

Output:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 Viral Video Processor
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 Step 1: Fetching Video Information
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ℹ Fetching video information from https://...
✓ Video information fetched

╭─────────────────── Video Information ───────────────────╮
│ Title        Amazing AI Tutorial                        │
│ Channel      Tech Channel                               │
│ Duration     15:32                                       │
│ Views        1,234,567                                   │
│ Likes        45,678                                      │
│ URL          https://...                                │
╰──────────────────────────────────────────────────────────╯

✓ This video meets viral criteria!

Do you want to download this video? [y/n]: y
```

### Example 2: Search for Viral Content

```bash
python app.py search "python programming" --min-views 1000000
```

### Example 3: Batch Analysis

```bash
# Analyze multiple videos
for video in downloads/*.mp4; do
    python app.py analyze "$video" --model base
done
```

## Tips

1. **Start with `base` model**: Good balance between speed and accuracy
2. **Use `--skip-review` for automation**: Useful for batch processing
3. **Check viral criteria**: Videos with 100k+ views and high engagement work best
4. **Save analysis results**: Always save when prompted to track which clips work best
5. **Experiment with clip duration**: Adjust `MIN_CLIP_DURATION` and `MAX_CLIP_DURATION` in `.env`

## Troubleshooting

### "ANTHROPIC_API_KEY not set"
- Create `.env` file from `.env.template`
- Add your Anthropic API key

### "ffmpeg not found"
- Install ffmpeg using the instructions above
- Ensure it's in your system PATH

### "Failed to download video"
- Check if URL is valid
- Some platforms may require authentication
- Try updating yt-dlp: `pip install --upgrade yt-dlp`

### Slow transcription
- Use smaller Whisper model: `--model tiny` or `--model base`
- Consider using GPU acceleration (requires CUDA setup)

## Future Features

- [ ] Actual clip creation and export
- [ ] Video animation style application using Replicate
- [ ] Audio spike detection
- [ ] Scene change detection
- [ ] Batch processing mode
- [ ] Custom scoring criteria
- [ ] Export to various formats
- [ ] Integration with video editing tools

## License

MIT License

## Contributing

Contributions welcome! Please feel free to submit issues or pull requests.

## Credits

Built with:
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - Video downloading
- [OpenAI Whisper](https://github.com/openai/whisper) - Transcription
- [Anthropic Claude](https://www.anthropic.com/) - AI analysis
- [Rich](https://github.com/Textualize/rich) - Beautiful CLI output
