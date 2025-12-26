"""Video downloader using yt-dlp."""

import os
from pathlib import Path
from typing import Dict, Optional
import yt_dlp

from ..utils import Config, print_info, print_success, print_error


class VideoDownloader:
    """Download videos from various platforms using yt-dlp."""

    def __init__(self):
        self.download_path = Config.DOWNLOAD_PATH
        self.download_path.mkdir(parents=True, exist_ok=True)

    def get_video_info(self, url: str) -> Optional[Dict]:
        """
        Get video metadata without downloading.

        Args:
            url: Video URL (YouTube, TikTok, Twitch, etc.)

        Returns:
            Dictionary with video information or None if failed
        """
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                print_info(f"Fetching video information from {url}...")
                info = ydl.extract_info(url, download=False)

                return {
                    'title': info.get('title', 'Unknown'),
                    'channel': info.get('uploader', info.get('channel', 'Unknown')),
                    'duration': info.get('duration', 0),
                    'view_count': info.get('view_count', 0),
                    'like_count': info.get('like_count', 0),
                    'upload_date': info.get('upload_date', 'Unknown'),
                    'webpage_url': info.get('webpage_url', url),
                    'id': info.get('id', 'unknown'),
                    'ext': info.get('ext', 'mp4'),
                    'description': info.get('description', ''),
                    'thumbnail': info.get('thumbnail', ''),
                }

        except Exception as e:
            print_error(f"Failed to fetch video info: {str(e)}")
            return None

    def download_video(self, url: str, output_filename: Optional[str] = None) -> Optional[str]:
        """
        Download video from URL.

        Args:
            url: Video URL
            output_filename: Optional custom filename (without extension)

        Returns:
            Path to downloaded video file or None if failed
        """
        try:
            # Get video info first
            info = self.get_video_info(url)
            if not info:
                return None

            # Create filename
            if output_filename:
                filename = f"{output_filename}.%(ext)s"
            else:
                # Sanitize title for filename
                safe_title = "".join(c for c in info['title'] if c.isalnum() or c in (' ', '-', '_')).strip()
                filename = f"{safe_title[:100]}.%(ext)s"

            output_path = self.download_path / filename

            # Download options
            ydl_opts = {
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                'outtmpl': str(output_path),
                'quiet': False,
                'no_warnings': False,
                'merge_output_format': 'mp4',
            }

            print_info(f"Downloading video: {info['title']}")

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            # Find the actual downloaded file
            # yt-dlp might add .mp4 extension
            downloaded_file = None
            for file in self.download_path.glob(f"{safe_title[:100]}.*"):
                if file.suffix in ['.mp4', '.webm', '.mkv']:
                    downloaded_file = file
                    break

            if downloaded_file and downloaded_file.exists():
                print_success(f"Downloaded to: {downloaded_file}")
                return str(downloaded_file)
            else:
                print_error("Download completed but file not found")
                return None

        except Exception as e:
            print_error(f"Failed to download video: {str(e)}")
            return None

    def is_viral(self, info: Dict, min_views: int = 100000) -> bool:
        """
        Check if video meets viral criteria based on engagement.

        Args:
            info: Video information dictionary
            min_views: Minimum view count threshold

        Returns:
            True if video is considered viral
        """
        views = info.get('view_count', 0)
        likes = info.get('like_count', 0)

        # Calculate engagement rate
        engagement_rate = (likes / views * 100) if views > 0 else 0

        # Check criteria
        is_viral = (
            views >= min_views and
            engagement_rate >= 1.0  # At least 1% engagement rate
        )

        return is_viral

    def search_viral_videos(self, query: str, max_results: int = 10) -> list:
        """
        Search for viral videos on YouTube.

        Args:
            query: Search query
            max_results: Maximum number of results to return

        Returns:
            List of video information dictionaries
        """
        search_url = f"ytsearch{max_results}:{query}"

        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
        }

        try:
            print_info(f"Searching for: {query}")

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                result = ydl.extract_info(search_url, download=False)

                videos = []
                if 'entries' in result:
                    for entry in result['entries']:
                        if entry:
                            # Get full info for each video
                            video_url = f"https://www.youtube.com/watch?v={entry['id']}"
                            info = self.get_video_info(video_url)
                            if info:
                                videos.append(info)

                # Sort by view count
                videos.sort(key=lambda x: x.get('view_count', 0), reverse=True)

                print_success(f"Found {len(videos)} videos")
                return videos

        except Exception as e:
            print_error(f"Search failed: {str(e)}")
            return []
