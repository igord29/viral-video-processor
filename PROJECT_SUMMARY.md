# Project Summary: Viral Video Processor

## Overview

A complete Python CLI application for downloading, transcribing, and analyzing viral videos using AI to identify the most engaging moments.

## What's Been Built

### ✅ Core Features Implemented

1. **Multi-Platform Video Downloader**
   - YouTube, TikTok, Twitch support via yt-dlp
   - Video metadata fetching (views, likes, duration)
   - Viral criteria detection (view count + engagement rate)
   - Search functionality for finding viral videos

2. **AI-Powered Transcription**
   - OpenAI Whisper integration
   - Multiple model sizes (tiny to large)
   - Word-level timestamps for precise clip timing
   - SRT subtitle export

3. **Engagement Analysis with Claude API**
   - Analyzes transcript segments for viral potential
   - Scores based on 4 criteria:
     - Hook Quality (30%) - attention-grabbing opening
     - Emotional Impact (30%) - emotions triggered
     - Information Density (20%) - valuable content
     - Pacing (20%) - energy and momentum
   - Generates clips between 15-60 seconds (configurable)
   - Ranks clips by engagement score

4. **Interactive Review Workflow**
   - Preview video info before downloading
   - Confirm before processing
   - Review clip candidates before creation
   - Save analysis results

5. **Beautiful CLI Interface**
   - Rich terminal output with colors and formatting
   - Progress indicators
   - Formatted tables for clip candidates
   - Clear status messages

## Project Structure

```
viral-video-processor/
├── app.py                           # Main CLI application
├── requirements.txt                 # Python dependencies
├── .env.template                   # Configuration template
├── .gitignore                      # Git ignore rules
├── README.md                       # Full documentation
├── QUICKSTART.md                   # Quick start guide
├── EXAMPLES.md                     # Usage examples
├── PROJECT_SUMMARY.md              # This file
├── setup.sh / setup.bat            # Setup scripts
│
├── src/
│   ├── __init__.py
│   │
│   ├── downloader/
│   │   ├── __init__.py
│   │   └── video_downloader.py    # yt-dlp integration
│   │
│   ├── transcription/
│   │   ├── __init__.py
│   │   └── whisper_transcriber.py # Whisper integration
│   │
│   ├── analysis/
│   │   ├── __init__.py
│   │   └── engagement_analyzer.py # Claude API analysis
│   │
│   └── utils/
│       ├── __init__.py
│       ├── config.py              # Configuration management
│       └── display.py             # CLI display utilities
│
├── downloads/                      # Downloaded videos
├── videos/                         # Processed videos
└── clips/                          # Generated clips (future)
```

## Commands Available

### 1. Download Command
```bash
python app.py download <URL> [OPTIONS]
```
**Options:**
- `--model`: Whisper model size (tiny/base/small/medium/large)
- `--skip-review`: Skip confirmation prompts
- `--auto-analyze`: Automatically analyze after download

**Workflow:**
1. Fetches video info
2. Displays metadata
3. Asks for download confirmation
4. Downloads video
5. Asks about analysis
6. Transcribes and analyzes
7. Shows top clip candidates

---

### 2. Analyze Command
```bash
python app.py analyze <VIDEO_PATH> [OPTIONS]
```
**Options:**
- `--model`: Whisper model size
- `--skip-review`: Skip confirmation prompts

**Workflow:**
1. Transcribes video
2. Analyzes segments
3. Shows top clip candidates
4. Offers to save results

---

### 3. Search Command
```bash
python app.py search <QUERY> [OPTIONS]
```
**Options:**
- `--limit`: Max results (default: 10)
- `--min-views`: Minimum view count (default: 100k)

**Workflow:**
1. Searches YouTube
2. Sorts by view count
3. Filters by engagement
4. Displays results
5. Offers to download selected video

---

### 4. Config Command
```bash
python app.py config
```
Shows current configuration settings.

---

## Technical Details

### Dependencies

**Core:**
- `yt-dlp` - Video downloading from multiple platforms
- `openai-whisper` - Audio transcription
- `anthropic` - Claude API for engagement analysis
- `moviepy` - Video processing (for future clip creation)
- `opencv-python` - Video analysis (for future features)

**UI/UX:**
- `click` - CLI framework
- `rich` - Beautiful terminal output
- `python-dotenv` - Environment management

**Data:**
- `numpy` - Numerical operations
- `pandas` - Data handling

---

### Configuration (via .env)

```env
# Required
ANTHROPIC_API_KEY=your_key_here

# Optional
REPLICATE_API_TOKEN=your_token_here

# Paths
DOWNLOAD_PATH=./downloads
VIDEO_PATH=./videos
CLIPS_PATH=./clips

# Processing
MAX_CLIP_DURATION=60
MIN_CLIP_DURATION=15
TOP_CLIPS_TO_SHOW=10
```

---

## Key Algorithms

### 1. Clip Generation Algorithm

**Input:** Transcript segments with timestamps
**Process:**
1. Group consecutive segments
2. Ensure duration between MIN and MAX (15-60s default)
3. Create potential clips with full text

**Output:** List of potential clips with text and timing

---

### 2. Engagement Scoring

**Input:** Clip text and context
**Process:**
1. Send to Claude API with scoring prompt
2. Claude analyzes for:
   - Hook Quality (1-10)
   - Emotional Impact (1-10)
   - Information Density (1-10)
   - Pacing (1-10)
3. Calculate weighted score:
   - Score = (Hook × 0.3) + (Emotional × 0.3) + (Info × 0.2) + (Pacing × 0.2)

**Output:** Score (0-10) with detailed breakdown

---

### 3. Viral Detection

**Input:** Video metadata
**Criteria:**
- View count ≥ 100,000
- Engagement rate ≥ 1% (likes/views × 100)

**Output:** Boolean (viral or not)

---

## What Works Now

✅ Download videos from YouTube/TikTok/Twitch
✅ Display video metadata and stats
✅ Transcribe videos with Whisper
✅ Analyze segments with Claude AI
✅ Score clips for engagement potential
✅ Rank and display top candidates
✅ Save analysis results
✅ Search for viral videos
✅ Interactive review workflow
✅ Beautiful CLI interface

---

## Future Features (Not Yet Implemented)

🔲 Automatic clip creation and export
🔲 Video animation style application (Replicate API)
🔲 Audio spike detection
🔲 Scene change detection
🔲 Batch processing mode
🔲 Custom scoring criteria
🔲 Multiple export formats
🔲 Video editing integration

---

## Getting Started

### Quick Start
```bash
# 1. Setup
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# 2. Configure
cp .env.template .env
# Edit .env and add ANTHROPIC_API_KEY

# 3. Run
python app.py download "https://youtube.com/watch?v=..."
```

### First Use Recommendation

Start with a short video (5-10 minutes):
```bash
python app.py download "https://youtube.com/short-video" --model base
```

This will:
- Download quickly
- Transcribe in reasonable time
- Show you how the analysis works

---

## Example Session Output

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
│ Title        How AI Will Change Everything              │
│ Channel      Tech Insights                              │
│ Duration     10:45                                       │
│ Views        2,456,789                                   │
│ Likes        123,456                                     │
│ URL          https://youtube.com/...                    │
╰──────────────────────────────────────────────────────────╯

✓ This video meets viral criteria!

Do you want to download this video? [y/n]: y

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 Step 3: Downloading Video
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ℹ Downloading video: How AI Will Change Everything
✓ Downloaded to: downloads/How AI Will Change Everything.mp4

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 Step 1: Transcribing Video
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ℹ Loading Whisper base model...
✓ Whisper base model loaded
ℹ Transcribing video: How AI Will Change Everything.mp4
✓ Transcription complete: 87 segments
✓ Transcription saved to: downloads/How AI Will Change Everything.json

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 Step 2: Analyzing Engagement Potential
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ℹ Analyzing segments for engagement potential...
ℹ Found 21 potential clips to analyze
✓ Analysis complete: 21 clips scored

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 Step 3: Top Clip Candidates
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

┏━━━━┳━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ #  ┃ Time              ┃ Duration ┃ Score  ┃ Reason                 ┃
┡━━━━╇━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━┩
│ 1  │ 01:23.50-01:53.70 │ 30.2s    │ 8.7/10 │ Strong hook with surp..│
│ 2  │ 03:45.20-04:15.40 │ 30.2s    │ 8.4/10 │ High emotional impact..│
│ 3  │ 07:12.80-07:43.00 │ 30.2s    │ 8.1/10 │ Dense information with│
│ 4  │ 09:05.30-09:35.50 │ 30.2s    │ 7.9/10 │ Excellent pacing and..│
│ 5  │ 02:30.00-03:00.20 │ 30.2s    │ 7.6/10 │ Good storytelling mom..│
└────┴───────────────────┴──────────┴────────┴────────────────────────┘
```

---

## Performance Notes

**Typical Processing Times:**

For a 10-minute video:
- Download: 30s - 1min
- Transcription (base model): ~20 minutes
- Analysis: ~30 seconds
- **Total: ~22 minutes**

**Optimization Tips:**
- Use `tiny` model for faster transcription (~10 min for 10-min video)
- Use `medium/large` for better accuracy but slower (~40-50 min)
- Process shorter videos first to test
- Use `--skip-review` for batch processing

---

## Cost Considerations

**Anthropic API:**
- Claude Sonnet: ~$3 per million input tokens
- Analysis uses ~500 tokens per clip
- 10 clips ≈ 5,000 tokens ≈ $0.015
- **Very affordable for typical use**

**Whisper:**
- Free (runs locally)
- No API costs
- Uses CPU/GPU

---

## Security & Privacy

- All processing is local (except Claude API calls)
- API keys stored in `.env` (not committed to git)
- Downloaded videos stay on your machine
- No data sent anywhere except Claude API for analysis

---

## Testing Checklist

Before first use:
- [ ] Python 3.8+ installed
- [ ] ffmpeg installed
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] .env file created with ANTHROPIC_API_KEY
- [ ] Directories created (downloads, videos, clips)

Test commands:
```bash
python app.py --help          # Should show commands
python app.py config          # Should show config
python app.py search "test"   # Should search YouTube
```

---

## Support & Resources

**Documentation:**
- `README.md` - Full documentation
- `QUICKSTART.md` - Quick start guide
- `EXAMPLES.md` - Usage examples
- This file - Project overview

**Key Files:**
- `app.py` - Main entry point (328 lines)
- `src/downloader/video_downloader.py` - Download logic (199 lines)
- `src/transcription/whisper_transcriber.py` - Transcription (155 lines)
- `src/analysis/engagement_analyzer.py` - Analysis logic (268 lines)

**Total Lines of Code:** ~1,200+ (excluding comments/blanks)

---

## Next Steps

1. **Install and configure** following QUICKSTART.md
2. **Test with a short video** (5-10 minutes)
3. **Review the analysis output** to understand scoring
4. **Experiment with different videos** to see patterns
5. **Adjust configuration** in .env to match your needs
6. **Start analyzing viral content!**

---

## Success Metrics

You'll know it's working when:
- ✓ Videos download successfully
- ✓ Transcription completes without errors
- ✓ Clips are scored and ranked
- ✓ Top clips show clear engagement patterns
- ✓ Scores align with your intuition about viral moments

Happy creating! 🎬✨
