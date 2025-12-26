"""Scene change detection and visual analysis."""

import cv2
import numpy as np
from pathlib import Path
from typing import List, Dict, Optional

from ..utils import Config, print_info, print_success, print_error


class SceneAnalyzer:
    """Detect scene changes and visual patterns in videos."""

    def __init__(self, threshold: float = None):
        """
        Initialize scene analyzer.

        Args:
            threshold: Threshold for scene change detection (default from config)
        """
        self.threshold = threshold or Config.SCENE_CHANGE_THRESHOLD

    def detect_scene_changes(self, video_path: str, sample_rate: int = 5) -> List[Dict]:
        """
        Detect scene changes using frame difference analysis.

        Args:
            video_path: Path to video file
            sample_rate: Process every Nth frame (higher = faster but less accurate)

        Returns:
            List of scene change information
        """
        try:
            print_info("Detecting scene changes...")

            video_path = Path(video_path)

            if not video_path.exists():
                print_error(f"Video file not found: {video_path}")
                return []

            # Open video
            cap = cv2.VideoCapture(str(video_path))

            if not cap.isOpened():
                print_error("Failed to open video file")
                return []

            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

            print_info(f"Analyzing {total_frames} frames at {fps} FPS...")

            scene_changes = []
            prev_frame = None
            frame_count = 0

            while True:
                ret, frame = cap.read()

                if not ret:
                    break

                # Sample frames
                if frame_count % sample_rate != 0:
                    frame_count += 1
                    continue

                # Convert to grayscale
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                # Resize for faster processing
                gray = cv2.resize(gray, (320, 240))

                if prev_frame is not None:
                    # Calculate frame difference
                    diff = cv2.absdiff(prev_frame, gray)
                    diff_score = np.mean(diff)

                    # Detect scene change
                    if diff_score > self.threshold:
                        time_seconds = frame_count / fps

                        scene_changes.append({
                            'frame': frame_count,
                            'time': float(time_seconds),
                            'diff_score': float(diff_score),
                            'type': 'cut' if diff_score > self.threshold * 1.5 else 'transition'
                        })

                prev_frame = gray.copy()
                frame_count += 1

                # Progress indicator
                if frame_count % 100 == 0:
                    progress = (frame_count / total_frames) * 100
                    print_info(f"Progress: {progress:.1f}%", end='\r')

            cap.release()

            print_success(f"\nDetected {len(scene_changes)} scene changes")

            return scene_changes

        except Exception as e:
            print_error(f"Failed to detect scene changes: {str(e)}")
            return []

    def detect_motion_intensity(self, video_path: str, segment_duration: float = 30.0) -> List[Dict]:
        """
        Analyze motion intensity in video segments.

        Args:
            video_path: Path to video file
            segment_duration: Duration of each segment in seconds

        Returns:
            List of motion analysis for each segment
        """
        try:
            print_info("Analyzing motion intensity...")

            video_path = Path(video_path)

            if not video_path.exists():
                print_error(f"Video file not found: {video_path}")
                return []

            cap = cv2.VideoCapture(str(video_path))

            if not cap.isOpened():
                print_error("Failed to open video file")
                return []

            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = total_frames / fps

            frames_per_segment = int(segment_duration * fps)
            num_segments = int(np.ceil(duration / segment_duration))

            segments = []
            prev_frame = None
            frame_count = 0
            segment_motion = []

            while True:
                ret, frame = cap.read()

                if not ret:
                    break

                # Convert to grayscale and resize
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                gray = cv2.resize(gray, (320, 240))

                if prev_frame is not None:
                    # Calculate optical flow
                    flow = cv2.calcOpticalFlowFarneback(
                        prev_frame, gray,
                        None, 0.5, 3, 15, 3, 5, 1.2, 0
                    )

                    # Calculate magnitude
                    mag, _ = cv2.cartToPolar(flow[..., 0], flow[..., 1])
                    motion_score = np.mean(mag)

                    segment_motion.append(motion_score)

                # Check if segment is complete
                if len(segment_motion) >= frames_per_segment or frame_count == total_frames - 1:
                    if segment_motion:
                        segment_idx = len(segments)
                        start_time = segment_idx * segment_duration
                        end_time = min((segment_idx + 1) * segment_duration, duration)

                        segments.append({
                            'start_time': start_time,
                            'end_time': end_time,
                            'duration': end_time - start_time,
                            'avg_motion': float(np.mean(segment_motion)),
                            'max_motion': float(np.max(segment_motion)),
                            'motion_variance': float(np.var(segment_motion)),
                            'is_high_motion': float(np.mean(segment_motion)) > 1.0
                        })

                        segment_motion = []

                prev_frame = gray.copy()
                frame_count += 1

            cap.release()

            print_success(f"Analyzed {len(segments)} motion segments")

            return segments

        except Exception as e:
            print_error(f"Failed to analyze motion: {str(e)}")
            return []

    def detect_face_moments(self, video_path: str, sample_rate: int = 10) -> List[Dict]:
        """
        Detect moments with faces (often correlate with viral content).

        Args:
            video_path: Path to video file
            sample_rate: Process every Nth frame

        Returns:
            List of face detection moments
        """
        try:
            print_info("Detecting faces in video...")

            video_path = Path(video_path)

            if not video_path.exists():
                print_error(f"Video file not found: {video_path}")
                return []

            # Load face cascade
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            face_cascade = cv2.CascadeClassifier(cascade_path)

            cap = cv2.VideoCapture(str(video_path))

            if not cap.isOpened():
                print_error("Failed to open video file")
                return []

            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = 0
            face_moments = []

            while True:
                ret, frame = cap.read()

                if not ret:
                    break

                if frame_count % sample_rate != 0:
                    frame_count += 1
                    continue

                # Convert to grayscale
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                # Detect faces
                faces = face_cascade.detectMultiScale(
                    gray,
                    scaleFactor=1.1,
                    minNeighbors=5,
                    minSize=(30, 30)
                )

                if len(faces) > 0:
                    time_seconds = frame_count / fps

                    # Calculate average face size (can indicate close-up vs wide shot)
                    avg_face_size = np.mean([w * h for (x, y, w, h) in faces])

                    face_moments.append({
                        'time': float(time_seconds),
                        'num_faces': len(faces),
                        'avg_face_size': float(avg_face_size),
                        'is_closeup': avg_face_size > 10000  # Arbitrary threshold
                    })

                frame_count += 1

            cap.release()

            print_success(f"Detected {len(face_moments)} frames with faces")

            return face_moments

        except Exception as e:
            print_error(f"Failed to detect faces: {str(e)}")
            return []

    def get_viral_visual_moments(self, video_path: str) -> List[Dict]:
        """
        Identify viral-worthy visual moments.

        Args:
            video_path: Path to video file

        Returns:
            List of viral visual moments with scores
        """
        viral_moments = []

        # Detect scene changes
        scene_changes = self.detect_scene_changes(video_path)

        for change in scene_changes:
            score = min(change['diff_score'] / self.threshold * 5, 10)

            viral_moments.append({
                'time': change['time'],
                'type': 'scene_change',
                'score': score,
                'description': f"Scene {change['type']}"
            })

        # Analyze motion
        motion_segments = self.detect_motion_intensity(video_path)

        for segment in motion_segments:
            if segment['is_high_motion']:
                score = min(segment['avg_motion'] * 3, 10)

                viral_moments.append({
                    'time': segment['start_time'],
                    'type': 'high_motion',
                    'score': score,
                    'description': f"High motion segment"
                })

        # Sort by score
        viral_moments.sort(key=lambda x: x['score'], reverse=True)

        print_success(f"Identified {len(viral_moments)} viral visual moments")

        return viral_moments
