# Viral Video Processor - Windows Edition

**AI-Powered Viral Video Analysis & Clip Generation for Windows**

A comprehensive Python CLI tool optimized for Windows that downloads, analyzes, and processes viral videos using AI-powered engagement analysis, audio spike detection, and scene change detection.

---

## 🎯 Key Features

### Download & Input Methods
- ✅ **Single video** download from YouTube/TikTok/Twitch
- ✅ **Playlist downloads** - get entire playlists automatically
- ✅ **Multiple URLs** - process several videos at once
- ✅ **Batch from file** - load URLs from text files
- ✅ **Parallel downloads** - download multiple videos simultaneously

### AI-Powered Analysis
- ✅ **Whisper transcription** - automatic speech-to-text
- ✅ **Claude API analysis** - engagement scoring based on:
  - Hook quality (30%)
  - Emotional impact (30%)
  - Information density (20%)
  - Pacing (20%)

### Advanced Detection (New!)
- ✅ **Audio spike detection** - identify dramatic audio moments
- ✅ **Beat drop detection** - find musical highlights
- ✅ **Scene change detection** - detect cuts and transitions
- ✅ **Motion analysis** - identify high-energy visual moments
- ✅ **Face detection** - find moments with faces (often viral)

### Windows Optimizations
- ✅ **Path handling** - automatic Windows path management
- ✅ **Long path support** - handles Windows 260-char limit
- ✅ **Safe filenames** - removes invalid Windows characters
- ✅ **Colorama integration** - colored terminal output
- ✅ **PowerShell scripts** - automated setup

---

## 🚀 Quick Start (Windows)

### 1. Automated Setup (Recommended)

Open PowerShell and run:

```powershell
cd C:\Development_Folder\viral-video-processor
.\setup_windows.ps1
```

This script will:
- Check Python & FFmpeg
- Create virtual environment
- Install all dependencies
- Set up configuration
- Create directories

### 2. Configure API Key

Edit `.env` file:
```env
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

Get your key from: [console.anthropic.com](https://console.anthropic.com/)

### 3. Test Installation

```cmd
python test_installation.py
```

### 4. Run Your First Command

```cmd
python app_windows.py search "tutorial" --limit 5
```

---

## 📖 Complete Installation Guide

See **[WINDOWS_GUIDE.md](WINDOWS_GUIDE.md)** for:
- Step-by-step Windows setup
- FFmpeg installation
- Troubleshooting
- Performance tips

---

## 💻 Usage Examples

### Basic Downloads

#### Single Video
```cmd
python app_windows.py download "https://youtube.com/watch?v=VIDEO_ID"
```

#### Playlist
```cmd
python app_windows.py download --playlist "https://youtube.com/playlist?list=PLAYLIST_ID"
```

Limit to first 10 videos:
```cmd
python app_windows.py download --playlist "URL" --max-videos 10
```

#### Multiple URLs
```cmd
python app_windows.py download -u "URL1" -u "URL2" -u "URL3"
```

#### From Text File

Create `urls.txt`:
```
https://youtube.com/watch?v=VIDEO1
https://youtube.com/watch?v=VIDEO2
https://youtube.com/watch?v=VIDEO3
```

Download:
```cmd
python app_windows.py download --file urls.txt
```

Parallel download:
```cmd
python app_windows.py download --file urls.txt --parallel
```

---

### Analysis Commands

#### Basic Analysis
```cmd
python app_windows.py analyze video.mp4
```

#### With Audio Spike Detection
```cmd
python app_windows.py analyze video.mp4 --enable-audio-analysis
```

#### With Scene Change Detection
```cmd
python app_windows.py analyze video.mp4 --enable-scene-analysis
```

#### Full Analysis (Everything!)
```cmd
python app_windows.py analyze video.mp4 --enable-audio-analysis --enable-scene-analysis --model medium
```

---

### Search Commands

#### Basic Search
```cmd
python app_windows.py search "python tutorial"
```

#### With Filters
```cmd
python app_windows.py search "gaming" --limit 20 --min-views 500000
```

#### Interactive Download
```cmd
python app_windows.py search "cooking" --download
```

---

## 🎬 Complete Workflow Example

### Download Playlist → Analyze All → Get Clips

```cmd
# 1. Download playlist (first 5 videos)
python app_windows.py download --playlist "PLAYLIST_URL" --max-videos 5 --skip-review

# 2. Analyze all downloaded videos with full detection
FOR %F IN (downloads\*.mp4) DO (
    python app_windows.py analyze "%F" --enable-audio-analysis --enable-scene-analysis
)

# 3. Review analysis results
# Check downloads\*.analysis.json files
```

---

## ⚙️ Configuration

### View Current Config
```cmd
python app_windows.py config
```

### Edit Settings

Edit `.env` file:

```env
# Paths (use Windows paths or relative)
DOWNLOAD_PATH=D:\Videos\Downloads
VIDEO_PATH=D:\Videos\Processed
CLIPS_PATH=D:\Videos\Clips
TEMP_PATH=C:\Temp\VideoProcessing

# Clip Settings
MAX_CLIP_DURATION=60
MIN_CLIP_DURATION=15
TOP_CLIPS_TO_SHOW=10

# Audio Analysis
AUDIO_SPIKE_THRESHOLD=0.7      # 0-1 (higher = fewer spikes)
SCENE_CHANGE_THRESHOLD=30.0    # Higher = fewer scene changes

# Batch Processing
MAX_PLAYLIST_VIDEOS=50         # Max videos from playlist
BATCH_DOWNLOAD_THREADS=3       # Parallel download threads
```

---

## 📊 Understanding the Output

### Analysis Results

After analysis, you'll see a table like this:

```
┏━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━━━━━┓
┃ #  ┃ Time          ┃ Duration ┃ Score  ┃ Reason           ┃
┡━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━━━━━┩
│ 1  │ 02:15-02:45   │ 30.0s    │ 9.2/10 │ Strong hook with │
│    │               │          │        │ audio spike      │
│ 2  │ 05:30-06:00   │ 30.0s    │ 8.8/10 │ High energy with │
│    │               │          │        │ scene change     │
│ 3  │ 08:45-09:15   │ 30.0s    │ 8.5/10 │ Emotional moment │
└────┴───────────────┴──────────┴────────┴──────────────────┘
```

**Score Breakdown:**
- **9.0-10.0** = Extremely viral-worthy
- **8.0-8.9** = Very good potential
- **7.0-7.9** = Good potential
- **6.0-6.9** = Moderate potential
- **< 6.0** = Lower potential

**Boosts Applied:**
- `[+X from A/V analysis]` = Score boosted by audio/visual features

---

## 🔍 What Gets Analyzed

### Transcript Analysis (Claude AI)
- Hook quality - Does it grab attention?
- Emotional triggers - Excitement, curiosity, humor?
- Information density - Valuable content?
- Pacing - Does it maintain energy?

### Audio Analysis (Optional)
- **Spikes** - Sudden volume increases
- **Beat drops** - Musical highlights
- **Energy levels** - High/low energy segments
- **Spectral features** - Tonal characteristics

### Visual Analysis (Optional)
- **Scene changes** - Cuts and transitions
- **Motion intensity** - Camera/subject movement
- **Face detection** - Presence of faces
- **Visual variety** - Shot diversity

---

## 📂 File Structure

```
C:\Development_Folder\viral-video-processor\
├── app_windows.py              # Windows-optimized CLI
├── downloads\
│   ├── video1.mp4             # Downloaded video
│   ├── video1.json            # Whisper transcription
│   └── video1.analysis.json   # Full analysis results
├── clips\                     # Future: Generated clips
├── temp\                      # Temporary processing files
└── venv\                      # Virtual environment
```

### Analysis JSON Structure

`video.analysis.json` contains:

```json
{
  "video_info": {...},
  "top_clips": [
    {
      "start_time": 135.3,
      "end_time": 165.5,
      "score": 8.5,
      "reason": "Strong hook...",
      "hook_quality": 9,
      "emotional_impact": 8
    }
  ],
  "audio_moments": [...],  # If enabled
  "scene_moments": [...]   # If enabled
}
```

---

## 🎯 Use Cases

### Content Creators
- Analyze your videos for best moments
- Find optimal clip points for shorts
- Understand what makes content engaging

### Researchers
- Study viral video patterns
- Analyze engagement factors
- Build viral content databases

### Marketers
- Identify shareable moments
- Optimize video content strategy
- Test different content styles

### Educators
- Find best teaching moments
- Create engaging course clips
- Analyze student engagement patterns

---

## 🐛 Windows-Specific Issues

### Long Path Errors
**Error:** `FileNotFoundError: [WinError 206] The filename or extension is too long`

**Fix:**
1. Enable long paths:
   - Run `regedit` as Admin
   - Go to: `HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\FileSystem`
   - Set `LongPathsEnabled` to `1`
   - Restart

2. Or use shorter paths:
   ```env
   DOWNLOAD_PATH=C:\Vid
   ```

### Script Execution Policy
**Error:** `cannot be loaded because running scripts is disabled`

**Fix:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Permission Denied
**Fix:**
- Run as Administrator
- Or use non-protected folder (not Program Files)

See **[WINDOWS_GUIDE.md](WINDOWS_GUIDE.md)** for complete troubleshooting.

---

## 🔧 Requirements

### System
- **OS:** Windows 10/11
- **Python:** 3.8 or higher
- **FFmpeg:** Latest version
- **RAM:** 4GB minimum, 8GB recommended
- **Disk:** 2GB+ for models and videos

### API Keys
- **Anthropic API Key** (required) - $5 credit free for new users
- **Replicate API Token** (optional) - for future features

---

## 📈 Performance

### Processing Times (10-minute video)

| Task | Time | Model Used |
|------|------|------------|
| Download | 30s-2min | - |
| Transcription (tiny) | ~10 min | Whisper tiny |
| Transcription (base) | ~20 min | Whisper base |
| Transcription (medium) | ~40 min | Whisper medium |
| Engagement Analysis | ~30s | Claude Sonnet |
| Audio Analysis | ~2 min | librosa |
| Scene Analysis | ~3 min | OpenCV |
| **Total (base model)** | **~25 min** | - |

### Cost Estimate

**Per 10-minute video:**
- Transcription: Free (local)
- Analysis: ~$0.015 (Claude API)
- Audio/Scene: Free (local)

**Very affordable!**

---

## 🔄 Updating

### Update Dependencies
```cmd
venv\Scripts\activate
pip install --upgrade -r requirements.txt
```

### Update yt-dlp (for new site support)
```cmd
pip install --upgrade yt-dlp
```

---

## 📚 Documentation

| File | Purpose |
|------|---------|
| `WINDOWS_GUIDE.md` | Complete Windows setup & troubleshooting |
| `QUICKSTART.md` | 5-minute quick start |
| `EXAMPLES.md` | Usage examples |
| `PROJECT_SUMMARY.md` | Technical details |
| `START_HERE.md` | Overview & first steps |

---

## 🆘 Getting Help

### Quick Checks
```cmd
# Test installation
python test_installation.py

# Check configuration
python app_windows.py config

# Get command help
python app_windows.py --help
python app_windows.py download --help
```

### Common Commands

```cmd
# Activate environment
venv\Scripts\activate

# Update packages
pip install --upgrade yt-dlp anthropic

# Check Python version
python --version

# Check FFmpeg
ffmpeg -version
```

---

## 🎓 Tutorial: First Video Analysis

### Complete Beginner Workflow

```cmd
# 1. Setup (one-time)
.\setup_windows.ps1

# 2. Activate environment
venv\Scripts\activate

# 3. Add API key to .env
notepad .env
# Add: ANTHROPIC_API_KEY=sk-ant-...

# 4. Test
python test_installation.py

# 5. Search for a video
python app_windows.py search "tutorial" --limit 3

# 6. Download and analyze
python app_windows.py download "https://youtube.com/watch?v=..." --enable-audio-analysis

# 7. View results
# Check: downloads\VIDEO_NAME.analysis.json
```

---

## 🌟 Future Features

- [ ] Automatic clip extraction
- [ ] Video style transfer (Replicate API)
- [ ] GPU acceleration support
- [ ] Subtitle generation
- [ ] Multi-language support
- [ ] Batch export to editing software
- [ ] Web UI

---

## 📝 License

MIT License - See LICENSE file

---

## 🤝 Contributing

Contributions welcome! Areas of interest:
- Windows-specific optimizations
- Performance improvements
- Additional analysis features
- Documentation improvements

---

## 🏆 Credits

Built with:
- **yt-dlp** - Video downloading
- **OpenAI Whisper** - Transcription
- **Anthropic Claude** - AI analysis
- **librosa** - Audio processing
- **OpenCV** - Video processing
- **Rich** - Terminal UI
- **Click** - CLI framework

---

## 📞 Support

- **Issues:** Create GitHub issue
- **Documentation:** Check `WINDOWS_GUIDE.md`
- **Updates:** `git pull` + `pip install -r requirements.txt`

---

**Made with ❤️ for Windows users**

Happy video processing! 🎬✨
