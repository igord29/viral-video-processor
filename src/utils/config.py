"""Configuration management for the viral video processor."""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration with Windows-specific path handling."""

    # System information
    IS_WINDOWS = sys.platform == 'win32'

    # API Keys
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', '')
    REPLICATE_API_TOKEN = os.getenv('REPLICATE_API_TOKEN', '')

    # Paths - using pathlib for cross-platform compatibility
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    DOWNLOAD_PATH = Path(os.getenv('DOWNLOAD_PATH', './downloads')).resolve()
    VIDEO_PATH = Path(os.getenv('VIDEO_PATH', './videos')).resolve()
    CLIPS_PATH = Path(os.getenv('CLIPS_PATH', './clips')).resolve()
    TEMP_PATH = Path(os.getenv('TEMP_PATH', './temp')).resolve()

    # Processing settings
    MAX_CLIP_DURATION = int(os.getenv('MAX_CLIP_DURATION', '60'))
    MIN_CLIP_DURATION = int(os.getenv('MIN_CLIP_DURATION', '15'))
    TOP_CLIPS_TO_SHOW = int(os.getenv('TOP_CLIPS_TO_SHOW', '10'))

    # Audio analysis settings
    AUDIO_SPIKE_THRESHOLD = float(os.getenv('AUDIO_SPIKE_THRESHOLD', '0.7'))
    SCENE_CHANGE_THRESHOLD = float(os.getenv('SCENE_CHANGE_THRESHOLD', '30.0'))

    # Batch processing settings
    MAX_PLAYLIST_VIDEOS = int(os.getenv('MAX_PLAYLIST_VIDEOS', '50'))
    BATCH_DOWNLOAD_THREADS = int(os.getenv('BATCH_DOWNLOAD_THREADS', '3'))

    @classmethod
    def ensure_directories(cls):
        """Create necessary directories if they don't exist."""
        directories = [
            cls.DOWNLOAD_PATH,
            cls.VIDEO_PATH,
            cls.CLIPS_PATH,
            cls.TEMP_PATH,
        ]

        for directory in directories:
            try:
                directory.mkdir(parents=True, exist_ok=True)

                # Windows: Handle long path names
                if cls.IS_WINDOWS:
                    # Enable long path support on Windows 10+
                    abs_path = str(directory.absolute())
                    if len(abs_path) > 260:
                        # Use extended-length path syntax
                        directory = Path(f'\\\\?\\{abs_path}')

            except PermissionError:
                raise PermissionError(f"Cannot create directory {directory}. Run as administrator or choose a different location.")
            except Exception as e:
                raise Exception(f"Failed to create directory {directory}: {str(e)}")

    @classmethod
    def validate(cls):
        """Validate required configuration."""
        if not cls.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY not set in .env file")

        cls.ensure_directories()

    @classmethod
    def get_safe_filename(cls, filename: str, max_length: int = 200) -> str:
        """
        Create a Windows-safe filename.

        Args:
            filename: Original filename
            max_length: Maximum filename length (Windows limit is 255)

        Returns:
            Safe filename string
        """
        # Remove invalid Windows filename characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')

        # Remove control characters
        filename = ''.join(char for char in filename if ord(char) >= 32)

        # Limit length (reserve space for extension)
        if len(filename) > max_length:
            filename = filename[:max_length]

        # Remove trailing dots and spaces (Windows doesn't allow)
        filename = filename.rstrip('. ')

        return filename or 'untitled'

    @classmethod
    def get_short_path(cls, path: Path) -> Path:
        """
        Get short path for Windows long path support.

        Args:
            path: Path object

        Returns:
            Path object with Windows long path support if needed
        """
        if not cls.IS_WINDOWS:
            return path

        abs_path = str(path.absolute())

        # If path is too long, use extended-length path syntax
        if len(abs_path) > 260 and not abs_path.startswith('\\\\?\\'):
            return Path(f'\\\\?\\{abs_path}')

        return path
