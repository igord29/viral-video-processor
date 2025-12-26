#!/usr/bin/env python3
"""
Viral Video Processor CLI App - Windows Optimized

A tool for downloading, analyzing, and processing viral videos with AI-powered
engagement analysis and clip generation. Optimized for Windows with enhanced
features including playlist support, batch processing, and audio/visual analysis.
"""

import sys
import click
from pathlib import Path
import colorama

# Initialize colorama for Windows color support
if sys.platform == 'win32':
    colorama.init()

from src.utils import (
    Config,
    print_header,
    print_success,
    print_error,
    print_info,
    print_warning,
    confirm_action,
    get_user_input,
    display_video_info,
    display_clip_candidates,
    console,
)
from src.downloader import BatchVideoDownloader
from src.transcription import WhisperTranscriber
from src.analysis import EngagementAnalyzer, AudioAnalyzer, SceneAnalyzer


@click.group()
@click.version_option(version="0.2.0-windows")
def cli():
    """
    Viral Video Processor - AI-powered video analysis and clip generation.

    Windows-optimized with support for:
    - Playlist downloads
    - Batch processing from files
    - Audio spike detection
    - Scene change detection
    - Multiple URL inputs
    """
    pass


@cli.command()
@click.argument('input', required=False)
@click.option('--urls', '-u', multiple=True, help='Multiple video URLs')
@click.option('--file', '-f', type=click.Path(exists=True), help='File with URLs (one per line)')
@click.option('--playlist', '-p', is_flag=True, help='Treat input as playlist URL')
@click.option('--max-videos', type=int, help='Max videos to download from playlist')
@click.option('--model', default='base', type=click.Choice(['tiny', 'base', 'small', 'medium', 'large']),
              help='Whisper model size (default: base)')
@click.option('--skip-review', is_flag=True, help='Skip video review confirmation')
@click.option('--auto-analyze', is_flag=True, help='Automatically analyze after download')
@click.option('--enable-audio-analysis', is_flag=True, help='Enable audio spike detection')
@click.option('--enable-scene-analysis', is_flag=True, help='Enable scene change detection')
@click.option('--parallel', is_flag=True, help='Download multiple videos in parallel')
def download(input, urls, file, playlist, max_videos, model, skip_review, auto_analyze,
            enable_audio_analysis, enable_scene_analysis, parallel):
    """
    Download and analyze videos with multiple input methods.

    USAGE EXAMPLES:

    \b
    # Single video
    python app_windows.py download "https://youtube.com/watch?v=..."

    \b
    # Multiple URLs
    python app_windows.py download -u "URL1" -u "URL2" -u "URL3"

    \b
    # From file
    python app_windows.py download --file urls.txt

    \b
    # Playlist
    python app_windows.py download --playlist "https://youtube.com/playlist?list=..."

    \b
    # With advanced analysis
    python app_windows.py download "URL" --enable-audio-analysis --enable-scene-analysis
    """
    try:
        # Validate configuration
        Config.validate()

        print_header("Viral Video Processor - Windows Edition")
        print_info(f"Platform: {sys.platform}")
        print_info(f"Working Directory: {Config.BASE_DIR}\n")

        # Initialize downloader
        downloader = BatchVideoDownloader()

        downloaded_files = []

        # Handle different input methods
        if file:
            # Download from file
            print_header("Downloading from File")
            downloaded_files = downloader.download_from_file(file)

        elif urls:
            # Download multiple URLs
            print_header(f"Downloading {len(urls)} Videos")
            downloaded_files = downloader.download_from_urls(list(urls), use_threads=parallel)

        elif input:
            # Check if it's a playlist
            if playlist or downloader.is_playlist(input):
                print_header("Downloading Playlist")

                if not skip_review:
                    playlist_info = downloader.get_playlist_info(input)

                    if playlist_info:
                        print_success(f"Playlist: {playlist_info['title']}")
                        print_info(f"Videos: {playlist_info['video_count']}")
                        print_info(f"Uploader: {playlist_info['uploader']}\n")

                        if not confirm_action("Download all videos from this playlist?"):
                            print_info("Download cancelled")
                            sys.exit(0)

                downloaded_files = downloader.download_playlist(input, max_videos)

            else:
                # Single video download
                print_header("Step 1: Fetching Video Information")
                video_info = downloader.get_video_info(input)

                if not video_info:
                    print_error("Failed to fetch video information")
                    sys.exit(1)

                # Display video information
                display_video_info(video_info)

                # Check if viral
                is_viral = downloader.is_viral(video_info)
                if is_viral:
                    print_success("This video meets viral criteria!")
                else:
                    print_warning("This video may not meet typical viral criteria")

                # Confirmation
                if not skip_review:
                    print_header("Step 2: Review & Confirmation")

                    if not confirm_action("Do you want to download this video?"):
                        print_info("Download cancelled")
                        sys.exit(0)

                # Download video
                print_header("Step 3: Downloading Video")
                video_path = downloader.download_video(input)

                if video_path:
                    downloaded_files = [video_path]
                else:
                    print_error("Failed to download video")
                    sys.exit(1)

        else:
            print_error("No input provided. Use --help for usage examples.")
            sys.exit(1)

        # Process downloaded videos
        if not downloaded_files:
            print_warning("No videos were downloaded")
            sys.exit(0)

        print_success(f"\nSuccessfully downloaded {len(downloaded_files)} video(s)")

        # Ask about analysis
        should_analyze = auto_analyze
        if not auto_analyze and not skip_review:
            print_header("Step 4: Analysis Options")
            should_analyze = confirm_action("Do you want to analyze these videos for viral clips?")

        if should_analyze:
            for i, video_path in enumerate(downloaded_files, 1):
                print_header(f"Analyzing Video {i}/{len(downloaded_files)}")
                video_info = {'title': Path(video_path).stem}

                analyze_video_complete(
                    video_path,
                    video_info,
                    model,
                    enable_audio_analysis,
                    enable_scene_analysis,
                    skip_review
                )
        else:
            print_info("Analysis skipped. You can analyze later with: app_windows.py analyze <video_path>")

    except ValueError as e:
        print_error(str(e))
        print_info("Please create a .env file with your ANTHROPIC_API_KEY")
        sys.exit(1)
    except Exception as e:
        print_error(f"An error occurred: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


@cli.command()
@click.argument('video_path', type=click.Path(exists=True))
@click.option('--model', default='base', type=click.Choice(['tiny', 'base', 'small', 'medium', 'large']),
              help='Whisper model size (default: base)')
@click.option('--skip-review', is_flag=True, help='Skip clip review confirmation')
@click.option('--enable-audio-analysis', is_flag=True, help='Enable audio spike detection')
@click.option('--enable-scene-analysis', is_flag=True, help='Enable scene change detection')
def analyze(video_path, model, skip_review, enable_audio_analysis, enable_scene_analysis):
    """
    Analyze a video file for viral clip potential.

    Includes transcription and AI-powered engagement analysis.
    Optionally enables audio spike and scene change detection.

    \b
    EXAMPLES:
    python app_windows.py analyze video.mp4
    python app_windows.py analyze video.mp4 --enable-audio-analysis --enable-scene-analysis
    """
    try:
        # Validate configuration
        Config.validate()

        print_header("Video Analysis - Windows Edition")

        video_info = {'title': Path(video_path).stem}

        analyze_video_complete(
            video_path,
            video_info,
            model,
            enable_audio_analysis,
            enable_scene_analysis,
            skip_review
        )

    except ValueError as e:
        print_error(str(e))
        print_info("Please create a .env file with your ANTHROPIC_API_KEY")
        sys.exit(1)
    except Exception as e:
        print_error(f"An error occurred: {str(e)}")
        sys.exit(1)


@cli.command()
@click.argument('query')
@click.option('--limit', default=10, help='Maximum number of results (default: 10)')
@click.option('--min-views', default=100000, help='Minimum view count (default: 100k)')
@click.option('--download', is_flag=True, help='Interactively download selected video')
def search(query, limit, min_views, download):
    """
    Search for viral videos on YouTube.

    Returns top videos sorted by view count and engagement.
    """
    try:
        print_header("Searching for Viral Videos")

        downloader = BatchVideoDownloader()
        videos = downloader.search_viral_videos(query, limit)

        if not videos:
            print_warning("No videos found")
            sys.exit(0)

        # Filter by view count
        viral_videos = [v for v in videos if v['view_count'] >= min_views]

        print_header(f"Found {len(viral_videos)} viral videos")

        for i, video in enumerate(viral_videos, 1):
            console.print(f"\n[bold cyan]{i}. {video['title']}[/bold cyan]")
            console.print(f"   Channel: {video['channel']}")
            console.print(f"   Views: {video['view_count']:,}")
            console.print(f"   Likes: {video['like_count']:,}")
            console.print(f"   Duration: {video['duration']//60}:{video['duration']%60:02d}")
            console.print(f"   URL: {video['webpage_url']}")

        # Ask if user wants to download one
        if download and viral_videos:
            if confirm_action("\nDo you want to download one of these videos?"):
                choice = get_user_input(f"Enter video number (1-{len(viral_videos)})", "1")
                try:
                    idx = int(choice) - 1
                    if 0 <= idx < len(viral_videos):
                        selected_video = viral_videos[idx]
                        print_header("\nDownloading Selected Video")

                        downloader_instance = BatchVideoDownloader()
                        video_path = downloader_instance.download_video(selected_video['webpage_url'])

                        if video_path:
                            print_success(f"\nDownloaded to: {video_path}")
                    else:
                        print_error("Invalid selection")
                except ValueError:
                    print_error("Invalid input")

    except Exception as e:
        print_error(f"Search failed: {str(e)}")
        sys.exit(1)


@cli.command()
def config():
    """Show current configuration and system information."""
    print_header("Configuration - Windows Edition")

    console.print(f"[cyan]System Information:[/cyan]")
    console.print(f"  Platform: {sys.platform}")
    console.print(f"  Python: {sys.version.split()[0]}")
    console.print(f"  Base Directory: {Config.BASE_DIR}")

    console.print(f"\n[cyan]API Keys:[/cyan]")
    console.print(f"  Anthropic API Key: {'✓ Set' if Config.ANTHROPIC_API_KEY else '✗ Not set'}")
    console.print(f"  Replicate API Token: {'✓ Set' if Config.REPLICATE_API_TOKEN else '✗ Not set'}")

    console.print(f"\n[cyan]Paths:[/cyan]")
    console.print(f"  Download Path: {Config.DOWNLOAD_PATH}")
    console.print(f"  Video Path: {Config.VIDEO_PATH}")
    console.print(f"  Clips Path: {Config.CLIPS_PATH}")
    console.print(f"  Temp Path: {Config.TEMP_PATH}")

    console.print(f"\n[cyan]Processing Settings:[/cyan]")
    console.print(f"  Max Clip Duration: {Config.MAX_CLIP_DURATION}s")
    console.print(f"  Min Clip Duration: {Config.MIN_CLIP_DURATION}s")
    console.print(f"  Top Clips to Show: {Config.TOP_CLIPS_TO_SHOW}")

    console.print(f"\n[cyan]Analysis Settings:[/cyan]")
    console.print(f"  Audio Spike Threshold: {Config.AUDIO_SPIKE_THRESHOLD}")
    console.print(f"  Scene Change Threshold: {Config.SCENE_CHANGE_THRESHOLD}")

    console.print(f"\n[cyan]Batch Settings:[/cyan]")
    console.print(f"  Max Playlist Videos: {Config.MAX_PLAYLIST_VIDEOS}")
    console.print(f"  Download Threads: {Config.BATCH_DOWNLOAD_THREADS}")


def analyze_video_complete(video_path: str, video_info: dict, model: str = 'base',
                           enable_audio: bool = False, enable_scene: bool = False,
                           skip_review: bool = False):
    """
    Complete video analysis with all features.

    Args:
        video_path: Path to video file
        video_info: Video metadata dictionary
        model: Whisper model size
        enable_audio: Enable audio spike detection
        enable_scene: Enable scene change detection
        skip_review: Skip confirmation prompts
    """
    # Step 1: Transcribe
    print_header("Step 1: Transcribing Video")
    transcriber = WhisperTranscriber(model_size=model)
    transcription = transcriber.transcribe_video(video_path)

    if not transcription:
        print_error("Transcription failed")
        sys.exit(1)

    # Save transcription
    transcript_path = Path(video_path).with_suffix('.json')
    transcriber.save_transcription(transcription, str(transcript_path))

    # Step 2: Audio Analysis (if enabled)
    audio_moments = []
    if enable_audio:
        print_header("Step 2: Analyzing Audio (Spikes & Beats)")
        audio_analyzer = AudioAnalyzer()
        audio_moments = audio_analyzer.get_viral_audio_moments(video_path)

        if audio_moments:
            print_success(f"Found {len(audio_moments[:10])} top audio moments")
            for i, moment in enumerate(audio_moments[:5], 1):
                print_info(f"  {i}. {moment['description']} at {moment['time']:.1f}s (score: {moment['score']:.1f})")

    # Step 3: Scene Analysis (if enabled)
    scene_moments = []
    if enable_scene:
        print_header("Step 3: Analyzing Scenes (Changes & Motion)")
        scene_analyzer = SceneAnalyzer()
        scene_moments = scene_analyzer.get_viral_visual_moments(video_path)

        if scene_moments:
            print_success(f"Found {len(scene_moments[:10])} top visual moments")
            for i, moment in enumerate(scene_moments[:5], 1):
                print_info(f"  {i}. {moment['description']} at {moment['time']:.1f}s (score: {moment['score']:.1f})")

    # Step 4: Engagement Analysis
    step_num = 4 if enable_audio or enable_scene else 2
    print_header(f"Step {step_num}: Analyzing Engagement Potential")

    analyzer = EngagementAnalyzer()
    context = f"Video Title: {video_info.get('title', 'Unknown')}"

    scored_clips = analyzer.analyze_segments(
        transcription['segments'],
        context=context
    )

    if not scored_clips:
        print_warning("No viable clips found")
        sys.exit(0)

    # Step 5: Combine all analyses
    step_num += 1
    print_header(f"Step {step_num}: Top Clip Candidates (Combined Analysis)")

    # Boost scores based on audio/scene moments
    for clip in scored_clips:
        clip_start = clip['start_time']
        clip_end = clip['end_time']

        # Check for audio moments in this clip
        audio_boost = 0
        for moment in audio_moments:
            if clip_start <= moment['time'] <= clip_end:
                audio_boost = max(audio_boost, moment['score'] * 0.1)

        # Check for scene moments in this clip
        scene_boost = 0
        for moment in scene_moments:
            if clip_start <= moment['time'] <= clip_end:
                scene_boost = max(scene_boost, moment['score'] * 0.1)

        # Apply boosts
        original_score = clip['score']
        clip['score'] = min(clip['score'] + audio_boost + scene_boost, 10.0)

        if audio_boost > 0 or scene_boost > 0:
            clip['reason'] += f" [+{audio_boost + scene_boost:.1f} from A/V analysis]"

    # Re-sort by updated scores
    scored_clips.sort(key=lambda x: x['score'], reverse=True)

    top_clips = analyzer.get_top_clips(scored_clips)
    display_clip_candidates(top_clips)

    # Step 6: Review and save
    if not skip_review:
        step_num += 1
        print_header(f"Step {step_num}: Save Results")

        if confirm_action("Do you want to save the analysis results?"):
            analysis_path = Path(video_path).with_suffix('.analysis.json')
            import json
            with open(analysis_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'video_info': video_info,
                    'top_clips': top_clips,
                    'all_clips': scored_clips,
                    'audio_moments': audio_moments[:20] if enable_audio else [],
                    'scene_moments': scene_moments[:20] if enable_scene else [],
                }, f, indent=2)
            print_success(f"Analysis saved to: {analysis_path}")


if __name__ == '__main__':
    cli()
