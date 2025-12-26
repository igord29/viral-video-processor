#!/usr/bin/env python3
"""
Installation test script for Viral Video Processor.

Run this to verify your installation is working correctly.
"""

import sys
from pathlib import Path

def test_python_version():
    """Test Python version."""
    print("Testing Python version...", end=" ")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✓ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"✗ Python {version.major}.{version.minor}.{version.micro} (need 3.8+)")
        return False


def test_imports():
    """Test if all required packages are installed."""
    print("\nTesting package imports...")

    packages = {
        'click': 'Click',
        'rich': 'Rich',
        'anthropic': 'Anthropic',
        'yt_dlp': 'yt-dlp',
        'whisper': 'OpenAI Whisper',
        'moviepy.editor': 'MoviePy',
        'cv2': 'OpenCV',
        'dotenv': 'python-dotenv',
        'numpy': 'NumPy',
        'pandas': 'Pandas',
    }

    all_ok = True
    for module, name in packages.items():
        try:
            __import__(module)
            print(f"  ✓ {name}")
        except ImportError:
            print(f"  ✗ {name} - NOT INSTALLED")
            all_ok = False

    return all_ok


def test_ffmpeg():
    """Test if ffmpeg is installed."""
    print("\nTesting ffmpeg installation...", end=" ")
    import subprocess

    try:
        result = subprocess.run(
            ['ffmpeg', '-version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            version = result.stdout.split('\n')[0]
            print(f"✓ {version}")
            return True
        else:
            print("✗ ffmpeg found but returned error")
            return False
    except FileNotFoundError:
        print("✗ ffmpeg not found in PATH")
        print("  Install ffmpeg: https://ffmpeg.org/download.html")
        return False
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False


def test_env_file():
    """Test if .env file exists and has required keys."""
    print("\nTesting .env configuration...", end=" ")

    env_path = Path('.env')
    if not env_path.exists():
        print("✗ .env file not found")
        print("  Create .env from .env.template and add your API keys")
        return False

    # Load .env
    from dotenv import load_dotenv
    import os
    load_dotenv()

    api_key = os.getenv('ANTHROPIC_API_KEY')
    if api_key:
        print(f"✓ .env file exists with API key configured")
        return True
    else:
        print("⚠ .env file exists but ANTHROPIC_API_KEY not set")
        print("  Add your Anthropic API key to .env file")
        return False


def test_directories():
    """Test if required directories exist."""
    print("\nTesting directories...", end=" ")

    from src.utils import Config
    Config.ensure_directories()

    dirs = [
        Config.DOWNLOAD_PATH,
        Config.VIDEO_PATH,
        Config.CLIPS_PATH,
    ]

    all_exist = True
    for dir_path in dirs:
        if not dir_path.exists():
            print(f"✗ {dir_path} does not exist")
            all_exist = False

    if all_exist:
        print("✓ All directories exist")

    return all_exist


def test_modules():
    """Test if source modules can be imported."""
    print("\nTesting source modules...")

    modules = {
        'src.downloader': 'Video Downloader',
        'src.transcription': 'Whisper Transcriber',
        'src.analysis': 'Engagement Analyzer',
        'src.utils': 'Utilities',
    }

    all_ok = True
    for module, name in modules.items():
        try:
            __import__(module)
            print(f"  ✓ {name}")
        except ImportError as e:
            print(f"  ✗ {name} - {str(e)}")
            all_ok = False

    return all_ok


def test_anthropic_api():
    """Test if Anthropic API is accessible."""
    print("\nTesting Anthropic API connection...", end=" ")

    try:
        from src.utils import Config
        import anthropic

        if not Config.ANTHROPIC_API_KEY:
            print("⚠ API key not configured")
            return False

        client = anthropic.Anthropic(api_key=Config.ANTHROPIC_API_KEY)

        # Try a minimal API call
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=10,
            messages=[{"role": "user", "content": "Hi"}]
        )

        print("✓ API connection successful")
        return True

    except Exception as e:
        print(f"✗ API test failed: {str(e)}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("Viral Video Processor - Installation Test")
    print("=" * 60)

    results = {}

    # Run tests
    results['Python Version'] = test_python_version()
    results['Package Imports'] = test_imports()
    results['FFmpeg'] = test_ffmpeg()
    results['Environment File'] = test_env_file()
    results['Directories'] = test_directories()
    results['Source Modules'] = test_modules()
    results['Anthropic API'] = test_anthropic_api()

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test:.<40} {status}")

    print("=" * 60)
    print(f"Results: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! You're ready to use Viral Video Processor.")
        print("\nTry running:")
        print("  python app.py --help")
        print("  python app.py config")
        return 0
    else:
        print("\n⚠ Some tests failed. Please fix the issues above.")
        print("\nCommon fixes:")
        print("  - Install missing packages: pip install -r requirements.txt")
        print("  - Install ffmpeg: https://ffmpeg.org/download.html")
        print("  - Create .env from .env.template")
        print("  - Add ANTHROPIC_API_KEY to .env")
        return 1


if __name__ == '__main__':
    sys.exit(main())
