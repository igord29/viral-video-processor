"""Enhanced video downloader with playlist and batch support for Windows."""

import os
from pathlib import Path
from typing import Dict, List, Optional
import yt_dlp
from concurrent.futures import ThreadPoolExecutor, as_completed

from ..utils import Config, print_info, print_success, print_error, print_warning


class BatchVideoDownloader:
    """Download videos with support for playlists, batches, and multiple input methods."""

    def __init__(self):
        self.download_path = Config.DOWNLOAD_PATH
        Config.ensure_directories()

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

    def is_playlist(self, url: str) -> bool:
        """
        Check if URL is a playlist.

        Args:
            url: URL to check

        Returns:
            True if URL is a playlist
        """
        playlist_indicators = [
            'playlist?list=',
            '/playlists/',
            'watch?v=.*&list=',
        ]

        url_lower = url.lower()
        return any(indicator in url_lower for indicator in playlist_indicators)

    def get_playlist_info(self, url: str) -> Optional[Dict]:
        """
        Get playlist metadata.

        Args:
            url: Playlist URL

        Returns:
            Dictionary with playlist information
        """
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,  # Don't download, just get info
        }

        try:
            print_info("Fetching playlist information...")

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                playlist_info = ydl.extract_info(url, download=False)

                if '_type' not in playlist_info or playlist_info['_type'] != 'playlist':
                    print_warning("URL does not appear to be a playlist")
                    return None

                entries = playlist_info.get('entries', [])

                return {
                    'title': playlist_info.get('title', 'Unknown Playlist'),
                    'uploader': playlist_info.get('uploader', 'Unknown'),
                    'video_count': len(entries),
                    'videos': [
                        {
                            'id': entry.get('id'),
                            'title': entry.get('title', 'Unknown'),
                            'url': entry.get('url') or f"https://www.youtube.com/watch?v={entry.get('id')}",
                            'duration': entry.get('duration', 0),
                        }
                        for entry in entries if entry
                    ]
                }

        except Exception as e:
            print_error(f"Failed to fetch playlist info: {str(e)}")
            return None

    def download_video(self, url: str, output_filename: Optional[str] = None,
                      video_index: Optional[int] = None) -> Optional[str]:
        """
        Download video from URL with Windows-safe filename handling.

        Args:
            url: Video URL
            output_filename: Optional custom filename (without extension)
            video_index: Optional index for batch downloads

        Returns:
            Path to downloaded video file or None if failed
        """
        try:
            # Get video info first
            info = self.get_video_info(url)
            if not info:
                return None

            # Create Windows-safe filename
            if output_filename:
                safe_filename = Config.get_safe_filename(output_filename)
            else:
                title = info['title']
                if video_index is not None:
                    title = f"{video_index:03d}_{title}"
                safe_filename = Config.get_safe_filename(title, max_length=180)

            # Full output path
            output_template = str(self.download_path / f"{safe_filename}.%(ext)s")

            # Download options
            ydl_opts = {
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                'outtmpl': output_template,
                'quiet': False,
                'no_warnings': False,
                'merge_output_format': 'mp4',
                'windowsfilenames': True,  # Windows-safe filenames
            }

            print_info(f"Downloading: {info['title'][:60]}...")

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            # Find the downloaded file
            expected_path = self.download_path / f"{safe_filename}.mp4"

            if expected_path.exists():
                print_success(f"Downloaded: {expected_path.name}")
                return str(expected_path)

            # Search for file with different extension
            for ext in ['.mp4', '.webm', '.mkv', '.avi']:
                alt_path = self.download_path / f"{safe_filename}{ext}"
                if alt_path.exists():
                    print_success(f"Downloaded: {alt_path.name}")
                    return str(alt_path)

            print_error("Download completed but file not found")
            return None

        except Exception as e:
            print_error(f"Failed to download video: {str(e)}")
            return None

    def download_playlist(self, url: str, max_videos: Optional[int] = None) -> List[str]:
        """
        Download all videos from a playlist.

        Args:
            url: Playlist URL
            max_videos: Maximum number of videos to download

        Returns:
            List of paths to downloaded videos
        """
        playlist_info = self.get_playlist_info(url)

        if not playlist_info:
            return []

        print_success(f"Found playlist: {playlist_info['title']}")
        print_info(f"Total videos: {playlist_info['video_count']}")

        videos = playlist_info['videos']

        # Limit number of videos
        if max_videos:
            max_videos = min(max_videos, Config.MAX_PLAYLIST_VIDEOS)
            videos = videos[:max_videos]
            print_info(f"Downloading first {len(videos)} videos")

        downloaded_files = []

        # Download videos
        for i, video in enumerate(videos, 1):
            print_info(f"\n[{i}/{len(videos)}] {video['title'][:60]}")

            video_path = self.download_video(
                video['url'],
                video_index=i
            )

            if video_path:
                downloaded_files.append(video_path)

        print_success(f"\nDownloaded {len(downloaded_files)}/{len(videos)} videos")

        return downloaded_files

    def download_from_urls(self, urls: List[str], use_threads: bool = True) -> List[str]:
        """
        Download multiple videos from a list of URLs.

        Args:
            urls: List of video URLs
            use_threads: Use multi-threading for parallel downloads

        Returns:
            List of paths to downloaded videos
        """
        print_info(f"Downloading {len(urls)} videos...")

        downloaded_files = []

        if use_threads and len(urls) > 1:
            # Parallel downloads
            max_workers = min(Config.BATCH_DOWNLOAD_THREADS, len(urls))

            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_url = {
                    executor.submit(self.download_video, url, video_index=i): (i, url)
                    for i, url in enumerate(urls, 1)
                }

                for future in as_completed(future_to_url):
                    i, url = future_to_url[future]
                    try:
                        video_path = future.result()
                        if video_path:
                            downloaded_files.append(video_path)
                            print_success(f"[{i}/{len(urls)}] Complete")
                    except Exception as e:
                        print_error(f"[{i}/{len(urls)}] Failed: {str(e)}")
        else:
            # Sequential downloads
            for i, url in enumerate(urls, 1):
                print_info(f"\n[{i}/{len(urls)}]")
                video_path = self.download_video(url, video_index=i)
                if video_path:
                    downloaded_files.append(video_path)

        print_success(f"\nDownloaded {len(downloaded_files)}/{len(urls)} videos")

        return downloaded_files

    def download_from_file(self, file_path: str) -> List[str]:
        """
        Download videos from a text file containing URLs (one per line).

        Args:
            file_path: Path to text file with URLs

        Returns:
            List of paths to downloaded videos
        """
        try:
            file_path = Path(file_path)

            if not file_path.exists():
                print_error(f"File not found: {file_path}")
                return []

            # Read URLs from file
            with open(file_path, 'r', encoding='utf-8') as f:
                urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]

            if not urls:
                print_error("No URLs found in file")
                return []

            print_info(f"Found {len(urls)} URLs in {file_path.name}")

            return self.download_from_urls(urls)

        except Exception as e:
            print_error(f"Failed to read file: {str(e)}")
            return []

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
