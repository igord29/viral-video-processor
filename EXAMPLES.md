# Usage Examples

Complete examples for different use cases.

## Basic Usage Examples

### 1. Download a Single Video

```bash
python app.py download "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

**What happens:**
1. Fetches video metadata
2. Shows title, views, likes, duration
3. Asks: "Do you want to download this video?"
4. Downloads to `downloads/` folder
5. Asks: "Do you want to analyze this video for viral clips?"
6. If yes: transcribes and analyzes
7. Shows top 10 clip candidates with scores

---

### 2. Search and Download

```bash
# Search for viral videos
python app.py search "AI tutorial" --limit 5 --min-views 100000

# Then download one
python app.py download "https://youtube.com/watch?v=..."
```

---

### 3. Analyze an Existing Video

```bash
python app.py analyze downloads/my_video.mp4
```

---

## Advanced Examples

### 4. Automated Workflow (No Prompts)

```bash
python app.py download "https://youtube.com/..." --skip-review --auto-analyze
```

This will:
- Download without asking
- Automatically analyze after download
- Still show results but skip confirmations

---

### 5. High-Quality Analysis

```bash
# Use medium model for better transcription
python app.py download "https://youtube.com/..." --model medium

# Or for existing video
python app.py analyze video.mp4 --model medium
```

**Model comparison:**
- `tiny`: Fast, less accurate (~1x video length)
- `base`: Balanced (default) (~2x video length)
- `small`: Better accuracy (~3x video length)
- `medium`: High quality (~4x video length)
- `large`: Best quality (~5x+ video length)

---

### 6. Batch Processing Videos

```bash
# Create a script to process multiple URLs
cat urls.txt | while read url; do
    python app.py download "$url" --skip-review --auto-analyze
done
```

Or with a shell script:
```bash
#!/bin/bash
# process_videos.sh

urls=(
    "https://youtube.com/watch?v=video1"
    "https://youtube.com/watch?v=video2"
    "https://youtube.com/watch?v=video3"
)

for url in "${urls[@]}"; do
    echo "Processing: $url"
    python app.py download "$url" --skip-review --auto-analyze
    echo "---"
done
```

---

### 7. Custom Configuration

Edit `.env` to customize:

```env
# Show top 20 clips instead of 10
TOP_CLIPS_TO_SHOW=20

# Prefer longer clips (30-90 seconds)
MIN_CLIP_DURATION=30
MAX_CLIP_DURATION=90

# Save to custom folders
DOWNLOAD_PATH=./my_downloads
CLIPS_PATH=./my_clips
```

Then run normally:
```bash
python app.py download "https://youtube.com/..."
```

---

## Real-World Workflows

### Workflow 1: Content Creator Looking for Viral Moments

```bash
# 1. Download your video
python app.py download "https://youtube.com/your-video"

# 2. Review the analysis
# Check which moments scored highest

# 3. Use the timestamps to create clips manually
# Or wait for automatic clip creation feature
```

**Output example:**
```
Top Clip Candidates:

# 1  02:15.30 - 02:45.50    30.2s    8.5/10    "Strong hook with emotional appeal"
# 2  05:30.00 - 06:00.20    30.2s    8.2/10    "High energy pacing and clear value"
# 3  08:45.10 - 09:15.30    30.2s    7.8/10    "Emotional storytelling moment"
```

---

### Workflow 2: Researcher Analyzing Viral Patterns

```bash
# 1. Search for viral videos in a niche
python app.py search "productivity tips" --limit 20 --min-views 1000000

# 2. Download top performers
python app.py download "https://youtube.com/..." --auto-analyze

# 3. Save analysis results (when prompted)
# Creates .analysis.json file

# 4. Compare patterns across videos
# Review saved .analysis.json files
```

---

### Workflow 3: Learning What Makes Content Viral

```bash
# Download and analyze successful videos
python app.py download "https://youtube.com/successful-video" --auto-analyze

# Check what scored high:
# - Hook quality: How did they open?
# - Emotional impact: What emotions were triggered?
# - Information density: How much value packed in?
# - Pacing: How did they maintain energy?

# Apply learnings to your content
```

---

## Understanding the Output

### Video Information Display

```
╭─────────────────── Video Information ───────────────────╮
│ Title        How to Build Viral AI Apps                 │
│ Channel      Tech Tutorials                             │
│ Duration     15:32                                       │
│ Views        1,234,567                                   │
│ Likes        45,678                                      │
│ Upload Date  20231215                                    │
│ URL          https://youtube.com/watch?v=...            │
╰──────────────────────────────────────────────────────────╯

✓ This video meets viral criteria!
```

**Viral Criteria:**
- Views ≥ 100,000
- Engagement rate ≥ 1% (likes/views)

---

### Clip Candidate Analysis

```
┏━━━━┳━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┓
┃ #  ┃ Time              ┃ Duration ┃ Score  ┃ Reason              ┃
┡━━━━╇━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━┩
│ 1  │ 02:15.30-02:45.50 │ 30.2s    │ 8.5/10 │ Opens with surpr... │
│ 2  │ 05:30.00-06:00.20 │ 30.2s    │ 8.2/10 │ High energy, cle... │
│ 3  │ 08:45.10-09:15.30 │ 30.2s    │ 7.8/10 │ Emotional storytel..│
└────┴───────────────────┴──────────┴────────┴─────────────────────┘
```

**Score Interpretation:**
- **8.0-10.0**: Excellent viral potential - use these!
- **6.0-7.9**: Good potential - worth considering
- **4.0-5.9**: Moderate potential - might work for specific audiences
- **0.0-3.9**: Low potential - probably skip

---

## Tips for Different Video Types

### Educational/Tutorial Videos
```bash
# Use medium model for better technical term transcription
python app.py download "https://youtube.com/tutorial" --model medium

# Look for clips with:
# - High information density scores
# - Clear "aha moment" indicators
# - Strong hook scores (attention-grabbing setups)
```

### Entertainment Videos
```bash
# Use base model (faster, good enough)
python app.py download "https://youtube.com/funny-video" --model base

# Look for clips with:
# - High emotional impact scores
# - Good pacing scores
# - Humor indicators in reasons
```

### Podcast/Interview Clips
```bash
# Use small or medium model for better accuracy with conversations
python app.py download "https://youtube.com/podcast" --model small

# Look for clips with:
# - Controversial or surprising statements
# - High emotional impact
# - Story-telling moments
```

---

## Saving and Using Results

### Analysis Files

When you save analysis, you get a `.analysis.json` file:

```json
{
  "video_info": {
    "title": "Video Title",
    "views": 1234567,
    "likes": 45678
  },
  "top_clips": [
    {
      "start_time": 135.3,
      "end_time": 165.5,
      "duration": 30.2,
      "score": 8.5,
      "reason": "Strong hook with emotional appeal",
      "hook_quality": 9,
      "emotional_impact": 8,
      "information_density": 8,
      "pacing": 9
    }
  ],
  "all_clips": [...]
}
```

You can use this to:
1. Track what works across videos
2. Build a database of viral patterns
3. Create automated clip extraction scripts

---

## Performance Optimization

### For Faster Processing
```bash
# Use tiny model (fastest)
python app.py download "url" --model tiny --auto-analyze

# Or skip analysis during download
python app.py download "url"
# (say no to analysis)

# Analyze later
python app.py analyze downloads/video.mp4 --model tiny
```

### For Best Quality
```bash
# Use large model (slowest but best)
python app.py download "url" --model large --auto-analyze
```

---

## Troubleshooting Examples

### Problem: Download fails

```bash
# Try updating yt-dlp
pip install --upgrade yt-dlp

# Then retry
python app.py download "url"
```

### Problem: Transcription is slow

```bash
# Use faster model
python app.py analyze video.mp4 --model tiny

# Or process shorter videos first
python app.py download "short-video-url"
```

### Problem: Analysis seems inaccurate

```bash
# Use better transcription model
python app.py analyze video.mp4 --model medium

# Better transcription = better analysis
```

---

## Next Steps

1. Start with a short video (5-10 minutes)
2. Use default settings first
3. Experiment with different models
4. Save successful analyses
5. Build your own viral pattern database

Happy creating! 🎬✨
