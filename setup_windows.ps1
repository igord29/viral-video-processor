# Viral Video Processor - Windows Setup Script
# PowerShell script for automated installation on Windows

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Viral Video Processor - Windows Setup " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "[WARNING] Not running as Administrator" -ForegroundColor Yellow
    Write-Host "Some features may require administrator privileges" -ForegroundColor Yellow
    Write-Host ""
}

# Check Python installation
Write-Host "[1/8] Checking Python installation..." -ForegroundColor Green

try {
    $pythonVersion = python --version 2>&1
    Write-Host "  Found: $pythonVersion" -ForegroundColor White

    # Check version
    $versionNumber = [regex]::Match($pythonVersion, '\d+\.\d+').Value
    $version = [version]$versionNumber

    if ($version -lt [version]"3.8") {
        Write-Host "  [ERROR] Python 3.8 or higher required" -ForegroundColor Red
        Write-Host "  Download from: https://www.python.org/downloads/" -ForegroundColor Yellow
        exit 1
    }
}
catch {
    Write-Host "  [ERROR] Python not found" -ForegroundColor Red
    Write-Host "  Download from: https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host "  Make sure to check 'Add Python to PATH' during installation" -ForegroundColor Yellow
    exit 1
}

# Check FFmpeg installation
Write-Host "[2/8] Checking FFmpeg installation..." -ForegroundColor Green

try {
    $ffmpegVersion = ffmpeg -version 2>&1 | Select-Object -First 1
    Write-Host "  Found: FFmpeg" -ForegroundColor White
}
catch {
    Write-Host "  [WARNING] FFmpeg not found" -ForegroundColor Yellow
    Write-Host "  FFmpeg is required for video processing" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  Installation options:" -ForegroundColor Cyan
    Write-Host "  1. Install via Chocolatey: choco install ffmpeg" -ForegroundColor White
    Write-Host "  2. Install via Scoop: scoop install ffmpeg" -ForegroundColor White
    Write-Host "  3. Download from: https://ffmpeg.org/download.html" -ForegroundColor White
    Write-Host ""

    $install = Read-Host "Would you like to download FFmpeg now? (y/n)"

    if ($install -eq "y" -or $install -eq "Y") {
        Write-Host "  Opening FFmpeg download page..." -ForegroundColor Yellow
        Start-Process "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
        Write-Host ""
        Write-Host "  Manual installation steps:" -ForegroundColor Cyan
        Write-Host "  1. Download and extract FFmpeg" -ForegroundColor White
        Write-Host "  2. Add FFmpeg bin folder to PATH" -ForegroundColor White
        Write-Host "  3. Restart this script" -ForegroundColor White
        exit 0
    }
    else {
        Write-Host "  Continuing without FFmpeg (required for video processing)" -ForegroundColor Yellow
    }
}

# Create virtual environment
Write-Host "[3/8] Creating virtual environment..." -ForegroundColor Green

if (Test-Path "venv") {
    Write-Host "  Virtual environment already exists" -ForegroundColor Yellow
}
else {
    python -m venv venv
    Write-Host "  Created virtual environment: venv" -ForegroundColor White
}

# Activate virtual environment
Write-Host "[4/8] Activating virtual environment..." -ForegroundColor Green

$activateScript = "venv\Scripts\Activate.ps1"

if (Test-Path $activateScript) {
    # Check execution policy
    $policy = Get-ExecutionPolicy -Scope CurrentUser

    if ($policy -eq "Restricted") {
        Write-Host "  [WARNING] Execution policy is Restricted" -ForegroundColor Yellow
        Write-Host "  Setting execution policy to RemoteSigned for current user..." -ForegroundColor Yellow

        try {
            Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
            Write-Host "  Execution policy updated" -ForegroundColor White
        }
        catch {
            Write-Host "  [ERROR] Failed to update execution policy" -ForegroundColor Red
            Write-Host "  Run as Administrator or manually run:" -ForegroundColor Yellow
            Write-Host "  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser" -ForegroundColor White
        }
    }

    & $activateScript
    Write-Host "  Virtual environment activated" -ForegroundColor White
}
else {
    Write-Host "  [ERROR] Activation script not found" -ForegroundColor Red
    exit 1
}

# Upgrade pip
Write-Host "[5/8] Upgrading pip..." -ForegroundColor Green

python -m pip install --upgrade pip --quiet
Write-Host "  Pip upgraded" -ForegroundColor White

# Install dependencies
Write-Host "[6/8] Installing Python dependencies..." -ForegroundColor Green
Write-Host "  This may take 10-15 minutes depending on your internet speed..." -ForegroundColor Yellow

python -m pip install -r requirements.txt

if ($LASTEXITCODE -eq 0) {
    Write-Host "  All dependencies installed successfully" -ForegroundColor White
}
else {
    Write-Host "  [ERROR] Failed to install dependencies" -ForegroundColor Red
    Write-Host "  Check the error messages above" -ForegroundColor Yellow
    exit 1
}

# Create .env file
Write-Host "[7/8] Setting up configuration..." -ForegroundColor Green

if (Test-Path ".env") {
    Write-Host "  .env file already exists" -ForegroundColor Yellow
}
else {
    Copy-Item ".env.template" ".env"
    Write-Host "  Created .env file from template" -ForegroundColor White
    Write-Host "  [ACTION REQUIRED] Edit .env and add your ANTHROPIC_API_KEY" -ForegroundColor Yellow
}

# Create directories
Write-Host "[8/8] Creating directories..." -ForegroundColor Green

$directories = @("downloads", "videos", "clips", "temp")

foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir | Out-Null
        Write-Host "  Created: $dir" -ForegroundColor White
    }
    else {
        Write-Host "  Already exists: $dir" -ForegroundColor Gray
    }
}

# Final instructions
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host ""

if (-not (Select-String -Path ".env" -Pattern "sk-ant-" -Quiet)) {
    Write-Host "1. Edit .env file and add your ANTHROPIC_API_KEY" -ForegroundColor Yellow
    Write-Host "   Get your key from: https://console.anthropic.com/" -ForegroundColor Gray
    Write-Host ""
}

Write-Host "2. Activate the virtual environment (if not already active):" -ForegroundColor White
Write-Host "   .\venv\Scripts\Activate.ps1" -ForegroundColor Gray
Write-Host ""

Write-Host "3. Test the installation:" -ForegroundColor White
Write-Host "   python test_installation.py" -ForegroundColor Gray
Write-Host ""

Write-Host "4. Try your first command:" -ForegroundColor White
Write-Host "   python app_windows.py --help" -ForegroundColor Gray
Write-Host "   python app_windows.py config" -ForegroundColor Gray
Write-Host "   python app_windows.py search `"tutorial`"" -ForegroundColor Gray
Write-Host ""

Write-Host "Documentation:" -ForegroundColor Cyan
Write-Host "  START_HERE.md      - Quick start guide" -ForegroundColor Gray
Write-Host "  INSTALL.md         - Installation guide" -ForegroundColor Gray
Write-Host "  WINDOWS_GUIDE.md   - Windows-specific guide" -ForegroundColor Gray
Write-Host "  EXAMPLES.md        - Usage examples" -ForegroundColor Gray
Write-Host ""

Write-Host "Happy video processing! " -NoNewline
Write-Host "🎬✨" -ForegroundColor Yellow
Write-Host ""
