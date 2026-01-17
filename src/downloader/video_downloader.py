"""Video downloader using yt-dlp."""

import os
from datetime import datetime
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