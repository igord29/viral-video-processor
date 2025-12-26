#!/usr/bin/env python3
"""
Viral Video Processor Web Application

Beautiful web UI for downloading, analyzing, and processing viral videos.
"""

import os
import json
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_file, url_for
from werkzeug.utils import secure_filename
import threading
from datetime import datetime

from src.downloader import VideoDownloader, BatchVideoDownloader
from src.transcription import WhisperTranscriber
from src.analysis import EngagementAnalyzer, AudioAnalyzer
from src.utils import Config, console

app = Flask(__name__, 
            template_folder='web/templates',
            static_folder='web/static')

app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max file size
app.config['SECRET_KEY'] = os.urandom(24)

# Store processing status
processing_status = {}
analysis_results = {}

# Create analysis results directory
ANALYSIS_RESULTS_PATH = Path('analysis_results')
ANALYSIS_RESULTS_PATH.mkdir(exist_ok=True)


def save_analysis_results(task_id: str, data: dict, video_path: str):
    """Save analysis results to disk."""
    try:
        # Create filename based on video name and task ID
        video_name = Path(video_path).stem
        safe_name = Config.get_safe_filename(video_name)[:50]
        filename = f"{safe_name}_{task_id}.json"
        filepath = ANALYSIS_RESULTS_PATH / filename
        
        # Add filepath to data
        data['results_file'] = str(filepath)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"Analysis saved to: {filepath}")
        return filepath
    except Exception as e:
        print(f"Error saving analysis: {e}")
        return None


def load_saved_analyses():
    """Load all saved analysis results from disk."""
    saved = {}
    try:
        for filepath in ANALYSIS_RESULTS_PATH.glob('*.json'):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    task_id = data.get('task_id', filepath.stem)
                    saved[task_id] = data
            except Exception as e:
                print(f"Error loading {filepath}: {e}")
    except Exception as e:
        print(f"Error scanning analysis folder: {e}")
    return saved


def get_recent_analyses(limit: int = 20):
    """Get list of recent analysis files."""
    analyses = []
    try:
        files = sorted(ANALYSIS_RESULTS_PATH.glob('*.json'), 
                      key=lambda x: x.stat().st_mtime, 
                      reverse=True)[:limit]
        
        for filepath in files:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    analyses.append({
                        'task_id': data.get('task_id', filepath.stem),
                        'video_path': data.get('video_path', 'Unknown'),
                        'clips_count': len(data.get('clips', [])),
                        'analyzed_at': data.get('analyzed_at', 'Unknown'),
                        'filename': filepath.name
                    })
            except:
                pass
    except:
        pass
    return analyses


# Load existing analyses on startup
analysis_results.update(load_saved_analyses())


@app.route('/')
def index():
    """Main dashboard page."""
    return render_template('index.html')


@app.route('/download')
def download_page():
    """Video download page."""
    return render_template('download.html')


@app.route('/analyze')
def analyze_page():
    """Video analysis page."""
    return render_template('analyze.html')


@app.route('/results')
def results_page():
    """Analysis results page."""
    return render_template('results.html')


@app.route('/api/config', methods=['GET'])
def get_config():
    """Get current configuration."""
    config_data = {
        'download_path': str(Config.DOWNLOAD_PATH),
        'video_path': str(Config.VIDEO_PATH),
        'clips_path': str(Config.CLIPS_PATH),
        'max_clip_duration': Config.MAX_CLIP_DURATION,
        'min_clip_duration': Config.MIN_CLIP_DURATION,
        'top_n_clips': Config.TOP_CLIPS_TO_SHOW,
        'has_anthropic_key': bool(Config.ANTHROPIC_API_KEY),
        'audio_spike_threshold': Config.AUDIO_SPIKE_THRESHOLD,
        'scene_change_threshold': Config.SCENE_CHANGE_THRESHOLD,
    }
    return jsonify(config_data)


@app.route('/api/video-info', methods=['POST'])
def get_video_info():
    """Get video metadata without downloading."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON data'}), 400
            
        url = data.get('url')
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400
        
        downloader = VideoDownloader()
        info = downloader.get_video_info(url)
        
        if not info:
            return jsonify({'error': 'Failed to fetch video info. Please check the URL and try again.'}), 400
        
        return jsonify({
            'success': True,
            'info': {
                'title': info.get('title', 'Unknown'),
                'duration': info.get('duration', 0),
                'views': info.get('view_count', 0),
                'likes': info.get('like_count', 0),
                'channel': info.get('channel', 'Unknown'),
                'thumbnail': info.get('thumbnail', ''),
                'description': info.get('description', '')[:500],
                'upload_date': info.get('upload_date', ''),
            }
        })
    except Exception as e:
        import traceback
        error_msg = str(e)
        try:
            print(f"Error in get_video_info: {error_msg}")
            print(traceback.format_exc())
        except UnicodeEncodeError:
            # Handle Windows encoding issues
            print(f"Error in get_video_info: {error_msg.encode('ascii', 'replace').decode()}")
        return jsonify({'error': f'Failed to fetch video info: {error_msg}'}), 500


@app.route('/api/download', methods=['POST'])
def download_video():
    """Download video from URL."""
    try:
        data = request.get_json()
        url = data.get('url')
        task_id = data.get('task_id', datetime.now().strftime('%Y%m%d%H%M%S'))
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400
        
        # Initialize status
        processing_status[task_id] = {
            'status': 'downloading',
            'progress': 0,
            'message': 'Starting download...'
        }
        
        def download_task():
            try:
                downloader = VideoDownloader()
                processing_status[task_id]['message'] = 'Downloading video...'
                
                video_path = downloader.download_video(url)
                
                if video_path:
                    processing_status[task_id] = {
                        'status': 'completed',
                        'progress': 100,
                        'message': 'Download completed!',
                        'video_path': str(video_path),
                        'filename': Path(video_path).name
                    }
                else:
                    processing_status[task_id] = {
                        'status': 'error',
                        'progress': 0,
                        'message': 'Download failed'
                    }
            except Exception as e:
                processing_status[task_id] = {
                    'status': 'error',
                    'progress': 0,
                    'message': f'Error: {str(e)}'
                }
        
        # Start download in background
        thread = threading.Thread(target=download_task)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'task_id': task_id,
            'message': 'Download started'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/analyze', methods=['POST'])
def analyze_video():
    """Analyze video for viral clips."""
    try:
        data = request.get_json()
        video_path = data.get('video_path')
        model_size = data.get('model', 'base')
        task_id = data.get('task_id', datetime.now().strftime('%Y%m%d%H%M%S'))
        min_clip_duration = data.get('min_clip_duration', Config.MIN_CLIP_DURATION)
        max_clip_duration = data.get('max_clip_duration', Config.MAX_CLIP_DURATION)
        
        if not video_path:
            return jsonify({'error': 'Video path is required'}), 400
        
        # Initialize status
        processing_status[task_id] = {
            'status': 'analyzing',
            'progress': 0,
            'message': 'Starting analysis...'
        }
        
        def analyze_task():
            try:
                # Step 1: Transcription
                processing_status[task_id]['message'] = 'Transcribing audio...'
                processing_status[task_id]['progress'] = 10
                
                transcriber = WhisperTranscriber(model_size=model_size)
                result = transcriber.transcribe_video(video_path)
                
                if not result:
                    raise Exception("Transcription failed")
                
                processing_status[task_id]['progress'] = 40
                
                # Step 2: Engagement Analysis
                processing_status[task_id]['message'] = f'Analyzing engagement ({min_clip_duration}s-{max_clip_duration}s clips)...'
                
                analyzer = EngagementAnalyzer()
                clips = analyzer.analyze_segments(
                    result.get('segments', []),
                    min_duration=min_clip_duration,
                    max_duration=max_clip_duration
                )
                
                processing_status[task_id]['progress'] = 70
                
                # Step 3: Audio Analysis (optional)
                processing_status[task_id]['message'] = 'Analyzing audio spikes...'
                
                audio_analyzer = AudioAnalyzer()
                audio_spikes = audio_analyzer.get_viral_audio_moments(video_path)
                
                processing_status[task_id]['progress'] = 90
                
                # Combine results
                analysis_data = {
                    'video_path': video_path,
                    'clips': clips,
                    'audio_spikes': audio_spikes or [],
                    'transcript': result.get('text', ''),
                    'segments': result.get('segments', []),
                    'settings': {
                        'min_clip_duration': min_clip_duration,
                        'max_clip_duration': max_clip_duration
                    },
                    'analyzed_at': datetime.now().isoformat(),
                    'task_id': task_id
                }
                
                # Store in memory
                analysis_results[task_id] = analysis_data
                
                # Save to disk
                save_analysis_results(task_id, analysis_data, video_path)
                
                processing_status[task_id] = {
                    'status': 'completed',
                    'progress': 100,
                    'message': f'Analysis completed! Found {len(clips)} potential clips.',
                    'clips_count': len(clips)
                }
                
            except Exception as e:
                processing_status[task_id] = {
                    'status': 'error',
                    'progress': 0,
                    'message': f'Error: {str(e)}'
                }
        
        # Start analysis in background
        thread = threading.Thread(target=analyze_task)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'task_id': task_id,
            'message': 'Analysis started'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/status/<task_id>', methods=['GET'])
def get_status(task_id):
    """Get processing status for a task."""
    status = processing_status.get(task_id, {
        'status': 'unknown',
        'progress': 0,
        'message': 'Task not found'
    })
    return jsonify(status)


@app.route('/api/results/<task_id>', methods=['GET'])
def get_results(task_id):
    """Get analysis results for a task."""
    results = analysis_results.get(task_id)
    
    # Try loading from disk if not in memory
    if not results:
        for filepath in ANALYSIS_RESULTS_PATH.glob('*.json'):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if data.get('task_id') == task_id:
                        results = data
                        analysis_results[task_id] = data  # Cache it
                        break
            except:
                pass
    
    if not results:
        return jsonify({'error': 'Results not found'}), 404
    
    return jsonify({
        'success': True,
        'results': results
    })


@app.route('/api/saved-analyses', methods=['GET'])
def list_saved_analyses():
    """List all saved analysis results."""
    try:
        analyses = get_recent_analyses(50)
        return jsonify({
            'success': True,
            'analyses': analyses
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/search', methods=['POST'])
def search_videos():
    """Search for viral videos."""
    try:
        data = request.get_json()
        query = data.get('query')
        max_results = data.get('max_results', 10)
        
        if not query:
            return jsonify({'error': 'Search query is required'}), 400
        
        downloader = VideoDownloader()
        results = downloader.search_viral_videos(query, max_results=max_results)
        
        return jsonify({
            'success': True,
            'results': results
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/videos', methods=['GET'])
def list_videos():
    """List downloaded videos."""
    try:
        videos = []
        
        for path in [Config.DOWNLOAD_PATH, Config.VIDEO_PATH]:
            if path.exists():
                for video_file in path.glob('*.*'):
                    if video_file.suffix.lower() in ['.mp4', '.mkv', '.avi', '.mov', '.webm']:
                        videos.append({
                            'name': video_file.name,
                            'path': str(video_file),
                            'size': video_file.stat().st_size,
                            'modified': video_file.stat().st_mtime,
                            'folder': path.name
                        })
        
        return jsonify({
            'success': True,
            'videos': sorted(videos, key=lambda x: x['modified'], reverse=True)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/videos')
def videos_page():
    """Videos library page."""
    return render_template('videos.html')


@app.route('/api/open-folder', methods=['POST'])
def open_folder():
    """Open downloads folder in file explorer."""
    try:
        import subprocess
        import sys
        
        folder_path = str(Config.DOWNLOAD_PATH.absolute())
        
        if sys.platform == 'win32':
            subprocess.Popen(['explorer', folder_path])
        elif sys.platform == 'darwin':  # macOS
            subprocess.Popen(['open', folder_path])
        else:  # Linux
            subprocess.Popen(['xdg-open', folder_path])
        
        return jsonify({'success': True, 'message': 'Folder opened'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/video/<path:filename>')
def serve_video(filename):
    """Serve a video file for playback or download."""
    try:
        # Check in downloads folder first
        video_path = Config.DOWNLOAD_PATH / filename
        if video_path.exists():
            return send_file(video_path, as_attachment=False)
        
        # Check in videos folder
        video_path = Config.VIDEO_PATH / filename
        if video_path.exists():
            return send_file(video_path, as_attachment=False)
        
        return jsonify({'error': 'Video not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/delete-video', methods=['POST'])
def delete_video():
    """Delete a video file."""
    try:
        data = request.get_json()
        video_path = data.get('path')
        
        if not video_path:
            return jsonify({'error': 'Video path is required'}), 400
        
        path = Path(video_path)
        if path.exists():
            path.unlink()
            return jsonify({'success': True, 'message': 'Video deleted'})
        else:
            return jsonify({'error': 'Video not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/generate-clip', methods=['POST'])
def generate_clip():
    """Generate a video clip from start to end time with optional aspect ratio conversion."""
    try:
        data = request.get_json()
        video_path = data.get('video_path')
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        clip_index = data.get('clip_index', 1)
        aspect_ratio = data.get('aspect_ratio', 'original')
        resize_mode = data.get('resize_mode', 'fit')  # 'fit' (black bars) or 'crop' (fill)
        target_duration = data.get('target_duration')  # Optional custom duration
        
        if not all([video_path, start_time is not None, end_time is not None]):
            return jsonify({'error': 'Missing required parameters'}), 400
        
        # Import moviepy
        try:
            from moviepy.editor import VideoFileClip
        except ImportError:
            from moviepy import VideoFileClip
        
        # Ensure clips directory exists
        Config.CLIPS_PATH.mkdir(parents=True, exist_ok=True)
        
        # Calculate actual duration
        actual_duration = end_time - start_time
        
        # Generate output filename with aspect ratio and duration
        source_name = Path(video_path).stem
        safe_name = Config.get_safe_filename(source_name)[:50]  # Limit name length
        
        # Build filename parts
        parts = [safe_name, f"clip{clip_index}"]
        
        # Add aspect ratio and mode if not original
        if aspect_ratio != 'original':
            parts.append(aspect_ratio.replace(':', 'x'))
            parts.append(resize_mode)  # 'fit' or 'crop'
        
        # Add duration
        parts.append(f"{int(actual_duration)}s")
        
        output_filename = "_".join(parts) + ".mp4"
        output_path = Config.CLIPS_PATH / output_filename
        
        # Extract clip - handle both moviepy 1.x and 2.x
        video = VideoFileClip(video_path)
        end_t = min(end_time, video.duration)
        
        # Try moviepy 2.x API first, fall back to 1.x
        if hasattr(video, 'subclipped'):
            clip = video.subclipped(start_time, end_t)
        else:
            clip = video.subclip(start_time, end_t)
        
        # Apply aspect ratio transformation if needed
        if aspect_ratio != 'original':
            clip = apply_aspect_ratio(clip, aspect_ratio, mode=resize_mode)
        
        # Write clip with progress
        clip.write_videofile(
            str(output_path),
            codec='libx264',
            audio_codec='aac',
            logger=None
        )
        
        # Clean up
        try:
            clip.close()
            video.close()
        except:
            pass  # Some versions don't have close()
        
        return jsonify({
            'success': True,
            'message': 'Clip generated successfully',
            'filename': output_filename,
            'clip_path': str(output_path),
            'duration': end_time - start_time,
            'aspect_ratio': aspect_ratio
        })
        
    except Exception as e:
        import traceback
        print(f"Error generating clip: {str(e)}")
        try:
            print(traceback.format_exc())
        except:
            pass
        return jsonify({'error': str(e)}), 500


def apply_aspect_ratio(clip, aspect_ratio, mode='fit'):
    """
    Apply aspect ratio transformation to a video clip.
    
    Args:
        clip: MoviePy VideoFileClip
        aspect_ratio: Target ratio ('9:16', '1:1', '4:5', '4:3')
        mode: 'fit' (black bars, show full video) or 'crop' (fill frame, crop edges)
    
    Returns:
        Transformed clip
    """
    from moviepy import ColorClip, CompositeVideoClip
    
    # Get current dimensions
    w, h = clip.size
    
    # Standard output sizes
    standard_sizes = {
        '9:16': (1080, 1920),  # Vertical HD
        '1:1': (1080, 1080),   # Square
        '4:5': (1080, 1350),   # Instagram portrait
        '4:3': (1440, 1080),   # Classic 4:3
        '16:9': (1920, 1080),  # Full HD
    }
    
    target_w, target_h = standard_sizes.get(aspect_ratio, (w, h))
    target_ratio = target_w / target_h
    current_ratio = w / h
    
    if abs(current_ratio - target_ratio) < 0.01:
        # Already correct ratio, just resize
        return resize_clip(clip, (target_w, target_h))
    
    if mode == 'fit':
        # FIT MODE: Scale video to fit inside frame, add black bars
        # This preserves the full video content
        
        if current_ratio > target_ratio:
            # Video is wider than target - fit to width, add bars top/bottom
            new_w = target_w
            new_h = int(target_w / current_ratio)
        else:
            # Video is taller than target - fit to height, add bars left/right
            new_h = target_h
            new_w = int(target_h * current_ratio)
        
        # Resize video to fit
        resized_clip = resize_clip(clip, (new_w, new_h))
        
        # Create black background
        bg = ColorClip(size=(target_w, target_h), color=(0, 0, 0))
        bg = bg.with_duration(clip.duration)
        
        # Center the video on the background
        x_pos = (target_w - new_w) // 2
        y_pos = (target_h - new_h) // 2
        
        # Composite video on background
        final = CompositeVideoClip([
            bg,
            resized_clip.with_position((x_pos, y_pos))
        ])
        
        return final
        
    else:
        # CROP MODE: Fill frame by cropping edges (center crop)
        
        if target_ratio < current_ratio:
            # Target is taller/narrower - crop width (center crop)
            new_width = int(h * target_ratio)
            x_center = w // 2
            x1 = x_center - new_width // 2
            x2 = x_center + new_width // 2
            
            clip = crop_clip(clip, x1=x1, x2=x2)
            
        else:
            # Target is wider - crop height (center crop)
            new_height = int(w / target_ratio)
            y_center = h // 2
            y1 = y_center - new_height // 2
            y2 = y_center + new_height // 2
            
            clip = crop_clip(clip, y1=y1, y2=y2)
        
        # Resize to target dimensions
        return resize_clip(clip, (target_w, target_h))


def resize_clip(clip, size):
    """Resize clip with moviepy 1.x/2.x compatibility."""
    if hasattr(clip, 'resized'):
        return clip.resized(size)
    else:
        return clip.resize(newsize=size)


def crop_clip(clip, x1=None, y1=None, x2=None, y2=None):
    """Crop clip with moviepy 1.x/2.x compatibility."""
    if hasattr(clip, 'cropped'):
        return clip.cropped(x1=x1, y1=y1, x2=x2, y2=y2)
    else:
        return clip.crop(x1=x1, y1=y1, x2=x2, y2=y2)


@app.route('/api/open-clips-folder', methods=['POST'])
def open_clips_folder():
    """Open clips folder in file explorer."""
    try:
        import subprocess
        import sys
        
        # Ensure clips directory exists
        Config.CLIPS_PATH.mkdir(parents=True, exist_ok=True)
        folder_path = str(Config.CLIPS_PATH.absolute())
        
        if sys.platform == 'win32':
            subprocess.Popen(['explorer', folder_path])
        elif sys.platform == 'darwin':  # macOS
            subprocess.Popen(['open', folder_path])
        else:  # Linux
            subprocess.Popen(['xdg-open', folder_path])
        
        return jsonify({'success': True, 'message': 'Folder opened'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/clips', methods=['GET'])
def list_clips():
    """List all generated clips."""
    try:
        clips = []
        
        if Config.CLIPS_PATH.exists():
            for clip_file in Config.CLIPS_PATH.glob('*.*'):
                if clip_file.suffix.lower() in ['.mp4', '.mkv', '.avi', '.mov', '.webm']:
                    clips.append({
                        'name': clip_file.name,
                        'path': str(clip_file),
                        'size': clip_file.stat().st_size,
                        'modified': clip_file.stat().st_mtime
                    })
        
        return jsonify({
            'success': True,
            'clips': sorted(clips, key=lambda x: x['modified'], reverse=True)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print("\n" + "="*60)
    print("Viral Video Processor - Web Interface")
    print("="*60)
    print(f"\nServer starting at: http://localhost:5000")
    print("\nFolders:")
    print(f"   Downloads: {Config.DOWNLOAD_PATH}")
    print(f"   Videos: {Config.VIDEO_PATH}")
    print(f"   Clips: {Config.CLIPS_PATH}")
    print("\nAPI Status:")
    print(f"   Anthropic API: {'Configured' if Config.ANTHROPIC_API_KEY else 'Not set'}")
    print("\n" + "="*60 + "\n")
    
    # Use PORT from environment (Railway) or default to 5000
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV', 'development') == 'development'
    
    app.run(debug=debug, host='0.0.0.0', port=port, threaded=True)
