"""Analysis module."""

from .engagement_analyzer import EngagementAnalyzer
from .audio_analyzer import AudioAnalyzer

# SceneAnalyzer requires OpenCV which may not work in all environments
try:
    from .scene_analyzer import SceneAnalyzer
    __all__ = ['EngagementAnalyzer', 'AudioAnalyzer', 'SceneAnalyzer']
except ImportError:
    # OpenCV not available (e.g., server environment without GUI libraries)
    SceneAnalyzer = None
    __all__ = ['EngagementAnalyzer', 'AudioAnalyzer']
