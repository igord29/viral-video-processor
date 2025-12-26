# Installation Guide

Complete step-by-step installation instructions for Viral Video Processor.

## System Requirements

- **Python**: 3.8 or higher
- **FFmpeg**: Latest version
- **Disk Space**: 2GB+ (for Whisper models and videos)
- **RAM**: 4GB+ recommended (8GB+ for large Whisper models)
- **OS**: Windows, macOS, or Linux

## Step 1: Install Python

### Check if Python is Installed
```bash
python --version
# or
python3 --version
```

You should see Python 3.8 or higher.

### If Not Installed

**Windows:**
- Download from [python.org](https://www.python.org/downloads/)
- Run installer and check "Add Python to PATH"

**macOS:**
```bash
brew install python3
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

---

## Step 2: Install FFmpeg

FFmpeg is required for video processing.

### Check if FFmpeg is Installed
```bash
ffmpeg -version
```

### If Not Installed

**Windows:**

Option 1 - Using Chocolatey (recommended):
```bash
choco install ffmpeg
```

Option 2 - Manual installation:
1. Download from [ffmpeg.org](https://ffmpeg.org/download.html)
2. Extract to `C:\ffmpeg`
3. Add `C:\ffmpeg\bin` to PATH:
   - Open System Properties → Environment Variables
   - Edit PATH variable
   - Add `C:\ffmpeg\bin`
   - Restart terminal

**macOS:**
```bash
brew install ffmpeg
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install ffmpeg
```

**Verify Installation:**
```bash
ffmpeg -version
```

---

## Step 3: Get Anthropic API Key

1. Go to [console.anthropic.com](https://console.anthropic.com/)
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key (starts with `sk-ant-`)

**Keep this key safe - you'll need it in Step 6!**

---

## Step 4: Download the Project

If you have this folder already, you're done! Otherwise:

```bash
# Clone if it's a git repository
git clone <repository-url>
cd viral-video-processor

# Or download and extract the ZIP file
```

---

## Step 5: Set Up Python Environment

### Windows

```bash
# Navigate to project folder
cd C:\Development_Folder\viral-video-processor

# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# You should see (venv) in your prompt
```

### macOS/Linux

```bash
# Navigate to project folder
cd /path/to/viral-video-processor

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# You should see (venv) in your prompt
```

---

## Step 6: Install Python Dependencies

With your virtual environment activated:

```bash
# Upgrade pip first
pip install --upgrade pip

# Install all dependencies
pip install -r requirements.txt
```

This will install:
- yt-dlp (video downloading)
- openai-whisper (transcription)
- anthropic (AI analysis)
- moviepy (video processing)
- opencv-python (video analysis)
- click, rich (CLI interface)
- And other dependencies

**This may take 5-10 minutes depending on your internet speed.**

---

## Step 7: Configure Environment

### Create .env File

**Windows:**
```bash
copy .env.template .env
notepad .env
```

**macOS/Linux:**
```bash
cp .env.template .env
nano .env
# or use your preferred editor
```

### Edit .env File

Add your Anthropic API key:

```env
# API Keys
ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
REPLICATE_API_TOKEN=your_replicate_token_here  # Optional

# Download settings (defaults are fine)
DOWNLOAD_PATH=./downloads
VIDEO_PATH=./videos
CLIPS_PATH=./clips

# Processing settings (defaults are fine)
MAX_CLIP_DURATION=60
MIN_CLIP_DURATION=15
TOP_CLIPS_TO_SHOW=10
```

**Save the file!**

---

## Step 8: Create Directories

```bash
# Windows
mkdir downloads videos clips

# macOS/Linux
mkdir -p downloads videos clips
```

Or let the app create them automatically on first run.

---

## Step 9: Test Installation

Run the installation test script:

```bash
python test_installation.py
```

You should see:
```
============================================================
Viral Video Processor - Installation Test
============================================================
Testing Python version... ✓ Python 3.x.x
Testing package imports...
  ✓ Click
  ✓ Rich
  ✓ Anthropic
  ✓ yt-dlp
  ✓ OpenAI Whisper
  ✓ MoviePy
  ✓ OpenCV
  ✓ python-dotenv
  ✓ NumPy
  ✓ Pandas
Testing ffmpeg installation... ✓ ffmpeg version ...
Testing .env configuration... ✓ .env file exists with API key configured
Testing directories... ✓ All directories exist
Testing source modules...
  ✓ Video Downloader
  ✓ Whisper Transcriber
  ✓ Engagement Analyzer
  ✓ Utilities
Testing Anthropic API connection... ✓ API connection successful
============================================================
Results: 7/7 tests passed

🎉 All tests passed! You're ready to use Viral Video Processor.
```

---

## Step 10: Verify CLI Works

```bash
python app.py --help
```

You should see:
```
Usage: app.py [OPTIONS] COMMAND [ARGS]...

  Viral Video Processor - AI-powered video analysis and clip generation.

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  analyze   Analyze a video file for viral clip potential.
  config    Show current configuration.
  download  Download and analyze a video from URL.
  search    Search for viral videos on YouTube.
```

---

## Step 11: First Test Run

Try the config command:

```bash
python app.py config
```

You should see your configuration displayed.

---

## Troubleshooting

### Problem: "python: command not found"

**Solution:** Use `python3` instead:
```bash
python3 --version
python3 -m venv venv
python3 app.py --help
```

---

### Problem: "pip: command not found"

**Solution:** Use `python -m pip`:
```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

---

### Problem: "ffmpeg: command not found"

**Solution:**
1. Install ffmpeg (see Step 2)
2. Verify installation: `ffmpeg -version`
3. Make sure it's in your PATH
4. Restart your terminal after installation

---

### Problem: "ModuleNotFoundError: No module named 'xyz'"

**Solution:**
1. Make sure virtual environment is activated (you should see `(venv)`)
2. Reinstall dependencies:
```bash
pip install -r requirements.txt
```

---

### Problem: "ANTHROPIC_API_KEY not set"

**Solution:**
1. Make sure `.env` file exists (copy from `.env.template`)
2. Open `.env` and add your API key
3. Key should start with `sk-ant-`
4. No quotes needed around the key

---

### Problem: Virtual environment won't activate

**Windows:**
If you get an execution policy error:
```bash
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
venv\Scripts\activate
```

**macOS/Linux:**
Make sure you're using `source`:
```bash
source venv/bin/activate
```

---

### Problem: Installation takes too long

**Solution:**
Some packages (especially Whisper and PyTorch) are large. This is normal.
- Whisper: ~3GB
- PyTorch: ~2GB
- Total download: ~5GB

On slow internet, this can take 15-30 minutes.

---

### Problem: "Permission denied" errors

**Windows:**
Run terminal as Administrator.

**macOS/Linux:**
Don't use `sudo` with pip in a virtual environment.
If files have wrong permissions:
```bash
chmod +x setup.sh
```

---

## Quick Setup Scripts

For convenience, you can use the provided setup scripts:

**Windows:**
```bash
setup.bat
```

**macOS/Linux:**
```bash
chmod +x setup.sh
./setup.sh
```

These scripts will:
1. Create virtual environment
2. Install dependencies
3. Create .env file
4. Create directories

**You still need to:**
1. Edit .env to add your API key
2. Install ffmpeg separately

---

## Verification Checklist

Before using the app, verify:

- [ ] Python 3.8+ installed (`python --version`)
- [ ] FFmpeg installed (`ffmpeg -version`)
- [ ] Virtual environment created and activated (`(venv)` in prompt)
- [ ] Dependencies installed (`pip list` shows anthropic, whisper, etc.)
- [ ] .env file created with ANTHROPIC_API_KEY
- [ ] Directories created (downloads, videos, clips)
- [ ] Test installation passes (`python test_installation.py`)
- [ ] CLI works (`python app.py --help`)

---

## Next Steps

Once installation is complete:

1. **Read QUICKSTART.md** for your first video analysis
2. **Try the search command**: `python app.py search "tutorial"`
3. **Download a short test video** (5-10 minutes)
4. **Review EXAMPLES.md** for more usage patterns

---

## Updating

To update dependencies:

```bash
# Activate virtual environment first
pip install --upgrade -r requirements.txt

# Or update specific package
pip install --upgrade yt-dlp
```

---

## Uninstalling

To completely remove:

```bash
# Deactivate virtual environment
deactivate

# Remove virtual environment
rm -rf venv  # macOS/Linux
rmdir /s venv  # Windows

# Remove downloaded content (optional)
rm -rf downloads videos clips

# Remove the project folder
cd ..
rm -rf viral-video-processor
```

---

## Getting Help

If you're still having issues:

1. Check the troubleshooting section above
2. Review error messages carefully
3. Verify each step was completed
4. Run `python test_installation.py` to identify issues

---

## Success!

If you've completed all steps and tests pass, you're ready to go!

**First command to try:**
```bash
python app.py search "python tutorial" --limit 3
```

Happy video processing! 🎬✨
