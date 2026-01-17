#!/usr/bin/env python3
"""
Viral Video Processor CLI App

A tool for downloading, analyzing, and processing viral videos with AI-powered
engagement analysis and clip generation.
"""

import sys
import click
from pathlib import Path

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
from src.downloader import VideoDownloader
from src.transcription import WhisperTranscriber
from src.analysis import EngagementAnalyzer


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """Viral Video Processor - AI-powered video analysis and clip generation."""
    pass


@cli.command()
@click.argument('url')
@click.option('--model', default='base', type=click.Choice(['tiny', 'base', 'small', 'medium', 'large']),
              help='Whisper model size (default: base)')
@click.option('--skip-review', is_flag=True, help='Skip video review confirmation')
@click.option('--auto-analyze', is_flag=True, help='Automatically analyze after download')
def download(url, model, skip_review, auto_analyze):
    """
    Download and analyze a video from URL.

    Supports YouTube, TikTok, Twitch, and other platforms supported by yt-dlp.
    """
    try:
        # Validate configuration
        Config.validate()

        print_header("Viral Video Processor")

        # Initialize downloader
        downloader = VideoDownloader()

        # Step 1: Get video information
        print_header("Step 1: Fetching Video Information")
        video_info = downloader.get_video_info(url)

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

        # Step 2: Confirmation
        if not skip_review:
            print_header("Step 2: Review & Confirmation")

            if not confirm_action("Do you want to download this video?"):
                print_info("Download cancelled")
                sys.exit(0)

        # Step 3: Download video
        print_header("Step 3: Downloading Video")
        video_path = downloader.download_video(url)

        if not video_path:
            print_error("Failed to download video")
            sys.exit(1)

        print_success(f"Video saved to: {video_path}")

        # Step 4: Ask about analysis
        should_analyze = auto_analyze
        if not auto_analyze and not skip_review:
            print_header("Step 4: Analysis Options")
            should_analyze = confirm_action("Do you want to analyze this video for viral clips?")

        if should_analyze:
            analyze_video(video_path, video_info, model)
        else:
            print_info("Analysis skipped. You can analyze later with: app.py analyze <video_path>")

    except ValueError as e:
        print_error(str(e))
        print_info("Please create a .env file with your ANTHROPIC_API_KEY")
        sys.exit(1)
    except Exception as e:
        print_error(f"An error occurred: {str(e)}")
        sys.exit(1)


@cli.command()
@click.argument('video_path', type=click.Path(exists=True))
@click.option('--model', default='base', type=click.Choice(['tiny', 'base', 'small', 'medium', 'large']),
              help='Whisper model size (default: base)')
@click.option('--skip-review', is_flag=True, help='Skip clip review confirmation')
def analyze(video_path, model, skip_review):
    """
    Analyze a video file for viral clip potential.

    Transcribes the video and uses AI to identify the most engaging segments.
    """
    try:
        # Validate configuration
        Config.validate()

        print_header("Video Analysis")

        # Get video info if available
        video_info = {'title': Path(video_path).stem}

        analyze_video(video_path, video_info, model, skip_review)

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
def search(query, limit, min_views):
    """
    Search for viral videos on YouTube.

    Returns top videos sorted by view count and engagement.
    """
    try:
        print_header("Searching for Viral Videos")

        downloader = VideoDownloader()
        videos = downloader.search_viral_videos(query, limit, min_views=min_views)

        if not videos:
            print_warning("No videos found")
            sys.exit(0)

        # Filter by view count
        viral_videos = [v for v in videos if v['view_count'] >= min_views]

        print_header(f"Found {len(viral_videos)} viral videos")

        for i, video in enumerate(viral_videos, 1):
            console.print(f"\n[bold cyan]{i}. {video['title']}[/bold cyan]")
            console.print(f"   Views: {video['view_count']:,}")
            console.print(f"   Likes: {video['like_count']:,}")
            console.print(f"   URL: {video['webpage_url']}")

        # Ask if user wants to download one
        if viral_videos and confirm_action("\nDo you want to download one of these videos?"):
            choice = get_user_input(f"Enter video number (1-{len(viral_videos)})", "1")
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(viral_videos):
                    selected_video = viral_videos[idx]
                    # Call download command
                    from click.testing import CliRunner
                    runner = CliRunner()
                    runner.invoke(download, [selected_video['webpage_url']])
                else:
                    print_error("Invalid selection")
            except ValueError:
                print_error("Invalid input")

    except Exception as e:
        print_error(f"Search failed: {str(e)}")
        sys.exit(1)


def analyze_video(video_path: str, video_info: dict, model: str = 'base', skip_review: bool = False):
    """
    Analyze a video for viral clip potential.

    Args:
        video_path: Path to video file
        video_info: Video metadata dictionary
        model: Whisper model size
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

    # Step 2: Analyze engagement
    print_header("Step 2: Analyzing Engagement Potential")

    analyzer = EngagementAnalyzer()
    context = f"Video Title: {video_info.get('title', 'Unknown')}"

    scored_clips = analyzer.analyze_segments(
        transcription['segments'],
        context=context
    )

    if not scored_clips:
        print_warning("No viable clips found")
        sys.exit(0)

    # Step 3: Display top clips
    print_header("Step 3: Top Clip Candidates")

    top_clips = analyzer.get_top_clips(scored_clips)
    display_clip_candidates(top_clips)

    # Step 4: Review and selection
    if not skip_review:
        print_header("Step 4: Clip Selection")

        if confirm_action("Do you want to create clips from these candidates?"):
            print_info("\nClip creation feature coming soon!")
            print_info("For now, you can manually extract clips using the timestamps above.")

            # Ask if user wants to save the analysis
            if confirm_action("\nDo you want to save the analysis results?"):
                analysis_path = Path(video_path).with_suffix('.analysis.json')
                import json
                with open(analysis_path, 'w') as f:
                    json.dump({
                        'video_info': video_info,
                        'top_clips': top_clips,
                        'all_clips': scored_clips
                    }, f, indent=2)
                print_success(f"Analysis saved to: {analysis_path}")
        else:
            print_info("Clip creation skipped")


@cli.command()
def config():
    """Show current configuration."""
    print_header("Configuration")

    console.print(f"[cyan]API Keys:[/cyan]")
    console.print(f"  Anthropic API Key: {'✓ Set' if Config.ANTHROPIC_API_KEY else '✗ Not set'}")
    console.print(f"  Replicate API Token: {'✓ Set' if Config.REPLICATE_API_TOKEN else '✗ Not set'}")

    console.print(f"\n[cyan]Paths:[/cyan]")
    console.print(f"  Download Path: {Config.DOWNLOAD_PATH}")
    console.print(f"  Video Path: {Config.VIDEO_PATH}")
    console.print(f"  Clips Path: {Config.CLIPS_PATH}")

    console.print(f"\n[cyan]Processing Settings:[/cyan]")
    console.print(f"  Max Clip Duration: {Config.MAX_CLIP_DURATION}s")
    console.print(f"  Min Clip Duration: {Config.MIN_CLIP_DURATION}s")
    console.print(f"  Top Clips to Show: {Config.TOP_CLIPS_TO_SHOW}")


if __name__ == '__main__':
    cli()
