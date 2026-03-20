"""Video downloader using yt-dlp."""

import os
import shutil
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
import yt_dlp

from ..utils import Config, print_info, print_success, print_error, print_warning


class VideoDownloader:
    """Download videos from various platforms using yt-dlp."""

    def __init__(self):
        self.download_path = Config.DOWNLOAD_PATH
        self.download_path.mkdir(parents=True, exist_ok=True)
        self._has_ffmpeg = shutil.which('ffmpeg') is not None
        self._has_node = shutil.which('node') is not None

    def _base_ydl_opts(self) -> dict:
        """Return base yt-dlp options with SSL and JS runtime fixes."""
        opts = {
            'nocheckcertificate': True,
        }
        # Enable Node.js runtime for YouTube signature solving if available
        if self._has_node:
            opts['js_runtimes'] = {'node': {}}
        return opts

    def get_video_info(self, url: str) -> Optional[Dict]:
        """
        Get video metadata without downloading.

        Args:
            url: Video URL (YouTube, TikTok, Twitch, etc.)

        Returns:
            Dictionary with video information or None if failed
        """
        ydl_opts = {
            **self._base_ydl_opts(),
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

    def download_video(self, url: str, output_filename: Optional[str] = None, max_retries: int = 3) -> Optional[str]:
        """
        Download video from URL.

        Args:
            url: Video URL
            output_filename: Optional custom filename (without extension)
            max_retries: Number of retry attempts on failure

        Returns:
            Path to downloaded video file or None if failed
        """
        # Get video info first
        info = self.get_video_info(url)
        if not info:
            return None

        # Create filename
        if output_filename:
            safe_name = output_filename
        else:
            # Sanitize title for filename
            safe_name = "".join(c for c in info['title'] if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_name = safe_name[:100]

        # Handle empty safe_name (e.g. emoji-only or non-latin titles)
        if not safe_name:
            safe_name = info.get('id', 'video')

        output_template = str(self.download_path / f"{safe_name}.%(ext)s")

        # Choose format based on ffmpeg availability
        # Without ffmpeg, we can't merge separate video+audio streams
        if self._has_ffmpeg:
            fmt = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
        else:
            print_warning("ffmpeg not found - downloading best single-stream format")
            fmt = 'best[ext=mp4]/best'

        ydl_opts = {
            **self._base_ydl_opts(),
            'format': fmt,
            'outtmpl': output_template,
            'quiet': False,
            'no_warnings': False,
        }
        if self._has_ffmpeg:
            ydl_opts['merge_output_format'] = 'mp4'

        last_error = None
        for attempt in range(1, max_retries + 1):
            try:
                if attempt > 1:
                    wait_time = 2 ** attempt
                    print_warning(f"Retry attempt {attempt}/{max_retries} (waiting {wait_time}s)...")
                    time.sleep(wait_time)

                print_info(f"Downloading video: {info['title']}")

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    # extract_info with download=True returns info dict with filepath
                    result_info = ydl.extract_info(url, download=True)

                    if not result_info:
                        print_error("yt-dlp returned no info after download")
                        continue

                    # Method 1: Get the exact filepath yt-dlp used
                    filepath = None

                    # Check requested_downloads for the final filepath
                    requested = result_info.get('requested_downloads')
                    if requested and len(requested) > 0:
                        filepath = requested[0].get('filepath')

                    # Method 2: Use prepare_filename to compute expected path
                    if not filepath or not Path(filepath).exists():
                        prepared = ydl.prepare_filename(result_info)
                        # With merge_output_format='mp4', final file has .mp4 extension
                        for candidate in [prepared, str(Path(prepared).with_suffix('.mp4'))]:
                            if Path(candidate).exists():
                                filepath = candidate
                                break

                    # Method 3: Glob for the safe_name (fallback)
                    if not filepath or not Path(filepath).exists():
                        for ext in ['.mp4', '.webm', '.mkv', '.avi']:
                            candidate = self.download_path / f"{safe_name}{ext}"
                            if candidate.exists():
                                filepath = str(candidate)
                                break

                    # Method 4: Find most recently modified video file in download dir
                    if not filepath or not Path(filepath).exists():
                        video_extensions = {'.mp4', '.webm', '.mkv', '.avi'}
                        recent_file = None
                        recent_time = 0
                        for f in self.download_path.iterdir():
                            if f.suffix in video_extensions and f.is_file():
                                mtime = f.stat().st_mtime
                                if mtime > recent_time:
                                    recent_time = mtime
                                    recent_file = f
                        # Only use if modified in the last 60 seconds
                        if recent_file and (time.time() - recent_time) < 60:
                            filepath = str(recent_file)
                            print_warning(f"Found recently downloaded file: {recent_file.name}")

                    if filepath and Path(filepath).exists():
                        print_success(f"Downloaded to: {filepath}")
                        return filepath

                    print_error("Download completed but file not found in expected location")
                    last_error = "File not found after download"

            except Exception as e:
                last_error = str(e)
                print_error(f"Download attempt {attempt} failed: {last_error}")

        print_error(f"Failed to download video after {max_retries} attempts: {last_error}")
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

    def _normalize_thumbnail(self, thumbnail) -> str:
        """Normalize thumbnail field to a URL string."""
        if isinstance(thumbnail, str):
            return thumbnail
        if isinstance(thumbnail, dict):
            return thumbnail.get('url', '')
        if isinstance(thumbnail, list) and thumbnail:
            first = thumbnail[0]
            if isinstance(first, str):
                return first
            if isinstance(first, dict):
                return first.get('url', '')
        return ''

    def search_viral_videos(
        self,
        query: str,
        max_results: int = 10,
        platform: str = 'youtube',
        content_type: str = 'all',
        min_views: int = 50000,
        date_filter: str = 'month',
        sort_by: str = 'viral_score'
    ) -> list:
        """
        Search for viral/trending videos on various platforms.

        Args:
            query: Search query
            max_results: Maximum number of results to return
            platform: Platform to search ('youtube', 'youtube_shorts', 'tiktok', 'twitch')
            content_type: Type of content ('all', 'shorts', 'long')
            min_views: View count threshold to mark a result as viral (default 50k)
            date_filter: Time range ('day', 'week', 'month', 'year', 'all')
            sort_by: Sort method ('viral_score', 'velocity', 'views', 'engagement')

        Returns:
            List of video information dictionaries sorted by virality
        """
        # Build search query based on platform without forcing "viral/trending" keywords
        if platform == 'youtube_shorts':
            search_query = f"{query} #shorts"
        elif platform == 'tiktok':
            # TikTok-style content on YouTube (TikTok has no public search API)
            search_query = f"{query} tiktok"
        elif platform == 'twitch':
            search_query = f"{query} twitch clip"
        else:
            search_query = query

        # Fetch more results to allow better ranking and avoid sparse output
        fetch_count = min(max_results * 8, 80)
        search_url = f"ytsearch{fetch_count}:{search_query}"

        ydl_opts = {
            **self._base_ydl_opts(),
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
            'ignoreerrors': True,
        }

        try:
            print_info(f"Searching {platform} for viral content: {query}")

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                result = ydl.extract_info(search_url, download=False)

                videos = []
                if 'entries' in result:
                    for entry in result['entries']:
                        if not entry:
                            continue
                        
                        try:
                            video_id = entry.get('id')
                            if not video_id:
                                continue
                            video_url = f"https://www.youtube.com/watch?v={video_id}"

                            # Use flat entry data when available; fallback to full info when needed
                            info = {
                                'title': entry.get('title', 'Unknown'),
                                'channel': entry.get('uploader', entry.get('channel', 'Unknown')),
                                'duration': entry.get('duration', 0),
                                'view_count': entry.get('view_count', 0),
                                'like_count': entry.get('like_count', 0),
                                'upload_date': entry.get('upload_date', ''),
                                'webpage_url': entry.get('url', video_url),
                                'id': video_id,
                                'thumbnail': self._normalize_thumbnail(entry.get('thumbnail', '')),
                            }

                            if not info.get('view_count') or not info.get('duration'):
                                full_info = self.get_video_info(video_url)
                                if full_info:
                                    info.update(full_info)

                            # Get metrics
                            views = info.get('view_count', 0) or 0
                            likes = info.get('like_count', 0) or 0
                            duration = info.get('duration', 0) or 0
                            upload_date_str = info.get('upload_date', '')

                            # Filter by content type
                            if content_type == 'shorts' and duration > 60:
                                continue
                            if content_type == 'long' and duration < 60:
                                continue

                            # Filter by date if specified
                            if date_filter != 'all' and upload_date_str:
                                try:
                                    upload_date = datetime.strptime(upload_date_str, '%Y%m%d')
                                    now = datetime.now()

                                    if date_filter == 'day' and (now - upload_date).days > 1:
                                        continue
                                    elif date_filter == 'week' and (now - upload_date).days > 7:
                                        continue
                                    elif date_filter == 'month' and (now - upload_date).days > 30:
                                        continue
                                    elif date_filter == 'year' and (now - upload_date).days > 365:
                                        continue
                                except Exception:
                                    pass  # If date parsing fails, include the video

                            # Calculate viral score for ranking
                            engagement_rate = (likes / views * 100) if views > 0 else 0

                            # Calculate views per day (velocity indicator)
                            days_since_upload = None
                            views_per_day = 0
                            if upload_date_str:
                                try:
                                    upload_date = datetime.strptime(upload_date_str, '%Y%m%d')
                                    days_since_upload = max((datetime.now() - upload_date).days, 1)
                                    views_per_day = views / days_since_upload
                                except Exception:
                                    days_since_upload = None

                            # Viral score combines views, engagement, and velocity
                            viral_score = (
                                (views / 1000) * 0.3 +  # Base view weight
                                (engagement_rate * 100) * 0.3 +  # Engagement weight
                                (views_per_day / 1000) * 0.4  # Velocity weight (trending factor)
                            )

                            info['platform'] = platform
                            info['search_query'] = query
                            info['viral_score'] = round(viral_score, 2)
                            info['engagement_rate'] = round(engagement_rate, 2)
                            info['views_per_day'] = int(views_per_day) if views_per_day else 0
                            info['is_viral'] = self.is_viral(info, min_views=min_views)
                            info['is_trending'] = days_since_upload is not None and views_per_day >= 10000
                            info['url'] = video_url

                            videos.append(info)
                                
                        except Exception as e:
                            print_error(f"Error processing video: {str(e)}")
                            continue

                # Sort videos based on selected criteria
                if sort_by == 'views':
                    videos.sort(key=lambda x: x.get('view_count', 0), reverse=True)
                elif sort_by == 'engagement':
                    videos.sort(key=lambda x: x.get('engagement_rate', 0), reverse=True)
                elif sort_by == 'velocity':
                    videos.sort(key=lambda x: x.get('views_per_day', 0), reverse=True)
                else:  # Default: sort by viral_score (combines views, engagement, velocity)
                    videos.sort(key=lambda x: x.get('viral_score', 0), reverse=True)

                # Limit to requested number
                videos = videos[:max_results]

                print_success(f"Found {len(videos)} viral videos on {platform}")
                return videos

        except Exception as e:
            print_error(f"Search failed: {str(e)}")
            return []
    
    def search_trending_topics(self, category: str = 'all', max_results: int = 10) -> list:
        """
        Search for currently trending videos without a specific query.
        Finds what's hot right now on YouTube.
        
        Args:
            category: Category filter ('all', 'music', 'gaming', 'entertainment', 'news')
            max_results: Maximum number of results
            
        Returns:
            List of trending video information
        """
        # Trending search queries by category
        trending_searches = {
            'all': ['viral today', 'trending now', 'going viral 2024'],
            'music': ['viral music', 'trending song', 'new hit song'],
            'gaming': ['viral gaming clip', 'gaming highlights', 'epic gaming moment'],
            'entertainment': ['viral video', 'trending entertainment', 'must watch'],
            'news': ['breaking news viral', 'trending news today'],
        }
        
        search_terms = trending_searches.get(category, trending_searches['all'])
        all_videos = []
        
        for term in search_terms:
            videos = self.search_viral_videos(
                query=term,
                max_results=max_results // len(search_terms) + 1,
                min_views=100000,  # Higher threshold for trending
                date_filter='week',  # Recent content only
                sort_by='viral_score'
            )
            all_videos.extend(videos)
        
        # Deduplicate by video ID
        seen_ids = set()
        unique_videos = []
        for video in all_videos:
            vid_id = video.get('id')
            if vid_id and vid_id not in seen_ids:
                seen_ids.add(vid_id)
                unique_videos.append(video)
        
        # Sort by viral score and limit
        unique_videos.sort(key=lambda x: x.get('viral_score', 0), reverse=True)
        return unique_videos[:max_results]