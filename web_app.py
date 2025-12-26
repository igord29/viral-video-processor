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
from src.analysis import EngagementAnalyzer, AudioAnalyzer, SceneAnalyzer
from src.utils import Config, console

app = Flask(__name__, 
            template_folder='web/templates',
            static_folder='web/static')

app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max file size
app.config['SECRET_KEY'] = os.urandom(24)

# Store processing status
processing_status = {}
analysis_results = {}


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
        'top_n_clips': Config.TOP_N_CLIPS,
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
        url = data.get('url')
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400
        
        downloader = VideoDownloader()
        info = downloader.get_video_info(url)
        
        if not info:
            return jsonify({'error': 'Failed to fetch video info'}), 400
        
        return jsonify({
            'success': True,
            'info': {
                'title': info.get('title', 'Unknown'),
                'duration': info.get('duration', 0),
                'views': info.get('view_count', 0),
                'likes': info.get('like_count', 0),
                'channel': info.get('uploader', 'Unknown'),
                'thumbnail': info.get('thumbnail', ''),
                'description': info.get('description', '')[:500],
                'upload_date': info.get('upload_date', ''),
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


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
                result = transcriber.transcribe(video_path)
                
                if not result:
                    raise Exception("Transcription failed")
                
                processing_status[task_id]['progress'] = 40
                
                # Step 2: Engagement Analysis
                processing_status[task_id]['message'] = 'Analyzing engagement...'
                
                analyzer = EngagementAnalyzer()
                clips = analyzer.analyze_transcript(result)
                
                processing_status[task_id]['progress'] = 70
                
                # Step 3: Audio Analysis (optional)
                processing_status[task_id]['message'] = 'Analyzing audio spikes...'
                
                audio_analyzer = AudioAnalyzer()
                audio_spikes = audio_analyzer.detect_spikes_from_video(video_path)
                
                processing_status[task_id]['progress'] = 90
                
                # Combine results
                analysis_results[task_id] = {
                    'video_path': video_path,
                    'clips': clips,
                    'audio_spikes': audio_spikes or [],
                    'transcript': result.get('text', ''),
                    'segments': result.get('segments', [])
                }
                
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
    
    if not results:
        return jsonify({'error': 'Results not found'}), 404
    
    return jsonify({
        'success': True,
        'results': results
    })


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
        results = downloader.search_videos(query, max_results=max_results)
        
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
                            'modified': video_file.stat().st_mtime
                        })
        
        return jsonify({
            'success': True,
            'videos': sorted(videos, key=lambda x: x['modified'], reverse=True)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print("\n" + "="*60)
    print("🎬 Viral Video Processor - Web Interface")
    print("="*60)
    print(f"\n✨ Server starting at: http://localhost:5000")
    print("\n📁 Folders:")
    print(f"   Downloads: {Config.DOWNLOAD_PATH}")
    print(f"   Videos: {Config.VIDEO_PATH}")
    print(f"   Clips: {Config.CLIPS_PATH}")
    print("\n🔑 API Status:")
    print(f"   Anthropic API: {'✓ Configured' if Config.ANTHROPIC_API_KEY else '✗ Not set'}")
    print("\n" + "="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
