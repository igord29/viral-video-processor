## Complete Windows Installation & Usage Guide

This guide is specifically for Windows users and covers everything you need to know about setting up and using the Viral Video Processor on Windows.

---

## Quick Setup (Automated)

### Option 1: PowerShell Script (Recommended)

1. **Open PowerShell** (Right-click Start → Windows PowerShell)

2. **Navigate to project folder:**
   ```powershell
   cd C:\Development_Folder\viral-video-processor
   ```

3. **Run setup script:**
   ```powershell
   .\setup_windows.ps1
   ```

4. **Follow the prompts** - the script will:
   - Check Python installation
   - Check FFmpeg installation
   - Create virtual environment
   - Install all dependencies
   - Create configuration files
   - Set up directories

---

### Option 2: Batch Script

1. **Open Command Prompt** (cmd)

2. **Navigate to project folder:**
   ```cmd
   cd C:\Development_Folder\viral-video-processor
   ```

3. **Run setup:**
   ```cmd
   setup.bat
   ```

---

## Manual Setup (Step-by-Step)

### Step 1: Install Python

1. **Download Python 3.8+** from [python.org](https://www.python.org/downloads/)

2. **Run installer** and **IMPORTANT**: Check "Add Python to PATH"

   ![Add to PATH](https://i.imgur.com/example.png)

3. **Verify installation:**
   ```cmd
   python --version
   ```

   Should show: `Python 3.8.x` or higher

---

### Step 2: Install FFmpeg

FFmpeg is required for video processing. Choose one method:

#### Method A: Chocolatey (Easiest)

1. **Install Chocolatey** (if not installed):
   - Open PowerShell as Administrator
   - Run:
     ```powershell
     Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
     ```

2. **Install FFmpeg:**
   ```powershell
   choco install ffmpeg
   ```

#### Method B: Scoop

1. **Install Scoop** (if not installed):
   ```powershell
   irm get.scoop.sh | iex
   ```

2. **Install FFmpeg:**
   ```powershell
   scoop install ffmpeg
   ```

#### Method C: Manual Installation

1. **Download FFmpeg:**
   - Go to: https://www.gyan.dev/ffmpeg/builds/
   - Download: `ffmpeg-release-essentials.zip`

2. **Extract to:**
   ```
   C:\ffmpeg
   ```

3. **Add to PATH:**
   - Open Start → Search "Environment Variables"
   - Click "Environment Variables"
   - Under "System Variables", find "Path"
   - Click "Edit" → "New"
   - Add: `C:\ffmpeg\bin`
   - Click OK

4. **Verify:**
   ```cmd
   ffmpeg -version
   ```

---

### Step 3: Set Up Project

1. **Create virtual environment:**
   ```cmd
   python -m venv venv
   ```

2. **Activate virtual environment:**
   ```cmd
   venv\Scripts\activate
   ```

   You should see `(venv)` in your prompt

3. **Upgrade pip:**
   ```cmd
   python -m pip install --upgrade pip
   ```

4. **Install dependencies:**
   ```cmd
   pip install -r requirements.txt
   ```

   This will take 10-15 minutes

---

### Step 4: Configure API Key

1. **Copy template:**
   ```cmd
   copy .env.template .env
   ```

2. **Edit .env file:**
   - Open `.env` in Notepad
   - Add your Anthropic API key:
     ```
     ANTHROPIC_API_KEY=sk-ant-your-key-here
     ```

3. **Get API key:**
   - Go to: https://console.anthropic.com/
   - Create account / Log in
   - Go to API Keys
   - Create new key

---

### Step 5: Test Installation

```cmd
python test_installation.py
```

Should show all tests passing ✓

---

## Usage Guide

### Basic Commands

#### 1. Single Video Download

```cmd
python app_windows.py download "https://youtube.com/watch?v=VIDEO_ID"
```

#### 2. Playlist Download

```cmd
python app_windows.py download --playlist "https://youtube.com/playlist?list=PLAYLIST_ID"
```

Limit videos:
```cmd
python app_windows.py download --playlist "URL" --max-videos 10
```

#### 3. Multiple URLs

```cmd
python app_windows.py download -u "URL1" -u "URL2" -u "URL3"
```

#### 4. From Text File

Create `urls.txt`:
```
https://youtube.com/watch?v=VIDEO1
https://youtube.com/watch?v=VIDEO2
https://youtube.com/watch?v=VIDEO3
```

Run:
```cmd
python app_windows.py download --file urls.txt
```

#### 5. Parallel Downloads

```cmd
python app_windows.py download --file urls.txt --parallel
```

#### 6. With Advanced Analysis

```cmd
python app_windows.py download "URL" --enable-audio-analysis --enable-scene-analysis
```

---

### Analysis Commands

#### Analyze Existing Video

```cmd
python app_windows.py analyze video.mp4
```

#### With Audio & Scene Detection

```cmd
python app_windows.py analyze video.mp4 --enable-audio-analysis --enable-scene-analysis
```

#### Different Whisper Models

```cmd
# Faster (less accurate)
python app_windows.py analyze video.mp4 --model tiny

# Slower (more accurate)
python app_windows.py analyze video.mp4 --model medium
```

---

### Search Command

```cmd
# Search for viral videos
python app_windows.py search "python tutorial" --limit 10

# With minimum views filter
python app_windows.py search "gaming" --limit 20 --min-views 500000

# Search and download interactively
python app_windows.py search "cooking" --download
```

---

### Configuration

```cmd
# View current configuration
python app_windows.py config
```

---

## Windows-Specific Features

### 1. Long Path Support

Windows has a 260-character path limit. This app handles it automatically:

- Uses `\\?\` prefix for long paths
- Truncates filenames when needed
- Resolves paths properly

### 2. Windows-Safe Filenames

Automatically removes invalid characters:
- `< > : " / \ | ? *`
- Trailing dots and spaces
- Control characters

### 3. Parallel Downloads

Use multiple threads for faster batch downloads:

```cmd
python app_windows.py download --file urls.txt --parallel
```

---

## Common Windows Issues & Solutions

### Issue 1: "python: command not found"

**Solution:**
- Python not in PATH
- Reinstall Python with "Add to PATH" checked
- Or use full path: `C:\Users\YourName\AppData\Local\Programs\Python\Python39\python.exe`

---

### Issue 2: "ffmpeg: command not found"

**Solution:**
- FFmpeg not installed or not in PATH
- See Step 2 above
- Verify with: `ffmpeg -version`

---

### Issue 3: "cannot be loaded because running scripts is disabled"

**Error:**
```
.\venv\Scripts\Activate.ps1 cannot be loaded because running scripts is disabled on this system
```

**Solution:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then activate again:
```powershell
.\venv\Scripts\Activate.ps1
```

---

### Issue 4: "Access Denied" or Permission Errors

**Solution:**
- Run PowerShell/CMD as Administrator
- Or choose a different download location (not in Program Files)

---

### Issue 5: Long Path Errors

**Error:**
```
FileNotFoundError: [WinError 206] The filename or extension is too long
```

**Solution:**
1. Enable long paths in Windows 10/11:
   - Run `regedit` as Administrator
   - Go to: `HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\FileSystem`
   - Set `LongPathsEnabled` to `1`
   - Restart computer

2. Or use shorter download path in `.env`:
   ```
   DOWNLOAD_PATH=C:\Videos
   ```

---

### Issue 6: Slow Installation

**Cause:** Large packages (Whisper, PyTorch)

**Solution:**
- Be patient (10-15 minutes normal)
- Use faster internet connection
- Or install core packages separately:
  ```cmd
  pip install torch --index-url https://download.pytorch.org/whl/cpu
  pip install -r requirements.txt
  ```

---

### Issue 7: CUDA/GPU Errors (if using GPU)

**Solution:**
- This app works fine on CPU
- GPU is optional and faster
- To use GPU, install PyTorch with CUDA:
  ```cmd
  pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
  ```

---

## Performance Tips for Windows

### 1. Use SSD for Downloads

Store videos on SSD for faster processing:

```env
# In .env file
DOWNLOAD_PATH=D:\FastSSD\Videos
```

### 2. Adjust Thread Count

For better performance:

```env
# In .env file
BATCH_DOWNLOAD_THREADS=5  # More threads = faster downloads
```

### 3. Use Faster Whisper Model

```cmd
python app_windows.py analyze video.mp4 --model tiny
```

### 4. Close Other Programs

- Close browser tabs
- Close video players
- Free up RAM

---

## Windows File Organization

### Recommended Structure

```
C:\Development_Folder\viral-video-processor\
├── venv\                          # Virtual environment
├── downloads\                     # Downloaded videos
│   ├── video1.mp4
│   ├── video1.json               # Transcription
│   └── video1.analysis.json      # Analysis results
├── clips\                        # Generated clips
├── temp\                         # Temporary files
└── [source files]
```

### Managing Disk Space

Videos take up space. To clean up:

```cmd
# Delete all downloads (keep analysis)
del /S downloads\*.mp4

# Delete temp files
del /S temp\*

# Keep only analysis files
# Downloads only contain .json files
```

---

## Advanced Windows Configuration

### Custom Paths

Edit `.env`:

```env
# Use different drives
DOWNLOAD_PATH=D:\Videos\Downloads
VIDEO_PATH=E:\Videos\Processed
CLIPS_PATH=E:\Videos\Clips
TEMP_PATH=C:\Temp\VideoProcessing
```

### Windows Terminal Integration

Add to Windows Terminal for quick access:

1. Open Windows Terminal Settings
2. Add new profile:
   ```json
   {
     "name": "Viral Video Processor",
     "commandline": "powershell.exe -NoExit -Command \"cd C:\\Development_Folder\\viral-video-processor; .\\venv\\Scripts\\Activate.ps1\"",
     "startingDirectory": "C:\\Development_Folder\\viral-video-processor"
   }
   ```

---

## Batch Processing Examples

### Process Entire Playlist

```cmd
python app_windows.py download --playlist "PLAYLIST_URL" --auto-analyze --skip-review
```

### Process Multiple URLs with Full Analysis

Create `process_all.bat`:
```batch
@echo off
python app_windows.py download --file urls.txt ^
  --auto-analyze ^
  --enable-audio-analysis ^
  --enable-scene-analysis ^
  --skip-review ^
  --parallel
```

Run:
```cmd
process_all.bat
```

---

## Scheduled Tasks (Windows Task Scheduler)

### Auto-Process Videos Daily

1. Open Task Scheduler
2. Create Basic Task
3. Set trigger (daily)
4. Action: Start a program
5. Program: `C:\Development_Folder\viral-video-processor\venv\Scripts\python.exe`
6. Arguments: `app_windows.py download --file daily_urls.txt --auto-analyze`
7. Start in: `C:\Development_Folder\viral-video-processor`

---

## Network Configuration

### Behind Corporate Proxy

Set proxy for pip:

```cmd
set HTTP_PROXY=http://proxy.company.com:8080
set HTTPS_PROXY=http://proxy.company.com:8080
pip install -r requirements.txt
```

### Firewall Issues

Add Python to Windows Firewall:
- Settings → Update & Security → Windows Security
→ Firewall & network protection → Allow an app
- Add `python.exe` from your venv

---

## Backup & Restore

### Backup Analysis Results

```cmd
# Backup all analysis files
xcopy downloads\*.json D:\Backup\Analysis\ /S /Y
xcopy downloads\*.analysis.json D:\Backup\Analysis\ /S /Y
```

### Restore Configuration

```cmd
# Backup .env
copy .env .env.backup

# Restore
copy .env.backup .env
```

---

## Updating

### Update Dependencies

```cmd
# Activate venv
venv\Scripts\activate

# Update all packages
pip install --upgrade -r requirements.txt

# Or update specific package
pip install --upgrade yt-dlp
```

### Update App

```cmd
git pull
pip install -r requirements.txt
```

---

## Complete Workflow Example

### From Setup to First Analysis

```cmd
# 1. Setup (one-time)
.\setup_windows.ps1

# 2. Activate environment
venv\Scripts\activate

# 3. Edit .env with API key
notepad .env

# 4. Test installation
python test_installation.py

# 5. Search for videos
python app_windows.py search "viral tutorials" --limit 5

# 6. Download and analyze
python app_windows.py download "https://youtube.com/watch?v=..." --enable-audio-analysis --enable-scene-analysis

# 7. Check results
# Analysis saved in: downloads\VIDEO_NAME.analysis.json
```

---

## Getting Help

### Check System Status

```cmd
python app_windows.py config
```

### Test Components

```cmd
python test_installation.py
```

### Enable Verbose Output

```cmd
# Set environment variable for debugging
set PYTHONVERBOSE=1
python app_windows.py download "URL"
```

---

## Next Steps

1. ✅ Complete setup using `setup_windows.ps1`
2. ✅ Configure API key in `.env`
3. ✅ Test with `python test_installation.py`
4. ✅ Try first download: `python app_windows.py search "tutorial"`
5. ✅ Read `EXAMPLES.md` for more usage patterns
6. ✅ Customize settings in `.env`

---

## Resources

- **Documentation:** `README.md`, `EXAMPLES.md`
- **Quick Start:** `QUICKSTART.md`
- **Python Download:** https://www.python.org/downloads/
- **FFmpeg Download:** https://www.gyan.dev/ffmpeg/builds/
- **Anthropic API:** https://console.anthropic.com/
- **Windows PowerShell Help:** `Get-Help about_Execution_Policies`

---

Happy video processing on Windows! 🎬✨
