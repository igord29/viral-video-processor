@echo off
REM Quick setup script for Viral Video Processor (Windows)

echo Setting up Viral Video Processor...

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Copy environment template
if not exist .env (
    echo Creating .env file...
    copy .env.template .env
    echo Please edit .env and add your ANTHROPIC_API_KEY
)

REM Create directories
echo Creating directories...
if not exist downloads mkdir downloads
if not exist videos mkdir videos
if not exist clips mkdir clips

echo.
echo Setup complete!
echo.
echo Next steps:
echo 1. Edit .env and add your ANTHROPIC_API_KEY
echo 2. Run: venv\Scripts\activate.bat
echo 3. Run: python app.py --help
echo.
pause
