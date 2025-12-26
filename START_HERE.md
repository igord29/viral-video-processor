# 🎬 START HERE - Viral Video Processor

Welcome! This is your complete guide to getting started.

## 📋 What You've Got

A fully-functional Python CLI app that:

✅ Downloads videos from YouTube/TikTok/Twitch
✅ Transcribes audio using AI (Whisper)
✅ Analyzes engagement potential (Claude API)
✅ Identifies viral-worthy clips
✅ Scores clips based on hooks, emotion, pacing
✅ Interactive review workflow

## 🚀 Quick Start (5 Minutes)

### 1. Prerequisites Check

You need:
- [ ] Python 3.8+ installed
- [ ] FFmpeg installed
- [ ] Anthropic API key (from console.anthropic.com)

**Check Python:**
```bash
python --version  # Should show 3.8 or higher
```

**Check FFmpeg:**
```bash
ffmpeg -version  # Should show version info
```

**Don't have them?** → See INSTALL.md

---

### 2. Setup (First Time Only)

**Windows:**
```bash
# Run setup script
setup.bat

# Or manual:
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.template .env
```

**macOS/Linux:**
```bash
# Run setup script
chmod +x setup.sh
./setup.sh

# Or manual:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.template .env
```

---

### 3. Configure API Key

Edit `.env` file:
```env
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

Get your key: https://console.anthropic.com/

---

### 4. Test Installation

```bash
# Activate environment if not already active
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate

# Run test
python test_installation.py
```

Should show: ✓ All tests passed!

---

### 5. Your First Video

```bash
python app.py search "tutorial" --limit 3
```

Then download one:
```bash
python app.py download "https://youtube.com/watch?v=..."
```

**Follow the interactive prompts!**

---

## 📚 Documentation Map

Different guides for different needs:

### New User?
1. **START_HERE.md** ← You are here!
2. **INSTALL.md** - Detailed installation
3. **QUICKSTART.md** - First steps guide

### Ready to Use?
1. **README.md** - Full documentation
2. **EXAMPLES.md** - Usage examples
3. **PROJECT_SUMMARY.md** - Technical overview

---

## 🎯 Common Commands

### Search for viral videos
```bash
python app.py search "python tutorial" --limit 5
```

### Download and analyze
```bash
python app.py download "https://youtube.com/watch?v=..."
```

### Analyze existing video
```bash
python app.py analyze path/to/video.mp4
```

### View configuration
```bash
python app.py config
```

### Get help
```bash
python app.py --help
python app.py download --help
```

---

## 🔧 How It Works

```
1. Download Video
   ↓
2. Transcribe with Whisper
   ↓
3. Analyze with Claude AI
   ↓
4. Score Clips
   ↓
5. Show Top Candidates
```

**Scoring Criteria:**
- Hook Quality (30%) - Attention-grabbing?
- Emotional Impact (30%) - Emotions triggered?
- Information Density (20%) - Valuable content?
- Pacing (20%) - Energy maintained?

**Score Guide:**
- 8.0-10.0 = Excellent viral potential
- 6.0-7.9 = Good potential
- 4.0-5.9 = Moderate potential
- 0.0-3.9 = Low potential

---

## 📊 Example Output

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

---

## ⚡ Tips for Success

1. **Start Small** - Try 5-10 minute videos first
2. **Use Base Model** - Good balance of speed/accuracy
3. **Check Viral Criteria** - 100k+ views recommended
4. **Save Results** - Always save when prompted
5. **Review Patterns** - Learn what makes content viral

---

## 🔍 Troubleshooting

### Command not found
→ Activate virtual environment first

### Missing API key
→ Edit .env and add ANTHROPIC_API_KEY

### FFmpeg error
→ Install ffmpeg (see INSTALL.md)

### Slow processing
→ Use smaller Whisper model: `--model tiny`

**More help:** See INSTALL.md troubleshooting section

---

## 📁 Project Structure

```
viral-video-processor/
├── app.py                    # Main CLI app ← Run this!
├── requirements.txt          # Python packages
├── .env.template            # Config template
├── .env                     # Your config (create this!)
│
├── Documentation/
│   ├── START_HERE.md       # You are here
│   ├── INSTALL.md          # Installation guide
│   ├── QUICKSTART.md       # Quick start
│   ├── README.md           # Full docs
│   ├── EXAMPLES.md         # Usage examples
│   └── PROJECT_SUMMARY.md  # Technical details
│
├── src/                     # Source code
│   ├── downloader/         # Video downloading
│   ├── transcription/      # Whisper transcription
│   ├── analysis/           # Claude API analysis
│   └── utils/              # Helper functions
│
└── Output Folders/
    ├── downloads/          # Downloaded videos
    ├── videos/             # Processed videos
    └── clips/              # Generated clips
```

---

## ⏱️ Processing Times

For a 10-minute video:
- **Download:** 30s - 1 min
- **Transcription:**
  - tiny: ~10 min
  - base: ~20 min (recommended)
  - medium: ~40 min
- **Analysis:** ~30 seconds
- **Total:** ~22 minutes (with base model)

---

## 💰 Cost Estimate

**Anthropic API (Claude):**
- ~$0.015 per 10 clips analyzed
- Very affordable for typical use!

**Whisper:**
- Free (runs locally)

---

## ✅ Ready to Go Checklist

Before your first run:
- [ ] Python 3.8+ installed
- [ ] FFmpeg installed
- [ ] Virtual environment created
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] .env file created with API key
- [ ] Installation test passes (`python test_installation.py`)
- [ ] CLI works (`python app.py --help`)

---

## 🎓 Learning Path

### Beginner (Day 1)
1. Install and configure
2. Run `python app.py config`
3. Search for videos: `python app.py search "tutorial"`
4. Download and analyze one short video

### Intermediate (Week 1)
1. Try different Whisper models
2. Analyze multiple videos
3. Compare scores across videos
4. Identify patterns in high-scoring clips

### Advanced (Month 1)
1. Batch process videos
2. Customize configuration
3. Build viral pattern database
4. Apply insights to your content

---

## 🚦 Next Steps

Choose your path:

**Just want to try it?**
→ Run: `python app.py search "tutorial"`

**Want detailed setup?**
→ Read: INSTALL.md

**Want to understand everything?**
→ Read: README.md

**Want examples?**
→ Read: EXAMPLES.md

**Want technical details?**
→ Read: PROJECT_SUMMARY.md

---

## 🎉 You're Ready!

Everything is set up and documented. Time to find some viral moments!

**First command:**
```bash
python app.py search "your interest here" --limit 5
```

Then follow the interactive prompts.

---

## 📞 Need Help?

1. Check relevant documentation file
2. Run `python test_installation.py`
3. Review error messages
4. See troubleshooting sections

---

## 🌟 Features Coming Soon

- Automatic clip creation and export
- Video animation styles
- Audio spike detection
- Scene change detection
- Batch processing mode
- Custom scoring criteria

---

Happy creating! 🎬✨

**Questions?** Check the docs in this folder.
**Ready?** Run `python app.py --help`
