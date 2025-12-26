"""Audio spike detection and analysis."""

import numpy as np
import librosa
import soundfile as sf
from pathlib import Path
from typing import List, Dict, Optional
try:
    from moviepy.editor import VideoFileClip
except ImportError:
    from moviepy import VideoFileClip

from ..utils import Config, print_info, print_success, print_error, print_warning


class AudioAnalyzer:
    """Analyze audio for spikes, energy changes, and viral patterns."""

    def __init__(self, spike_threshold: float = None):
        """
        Initialize audio analyzer.

        Args:
            spike_threshold: Threshold for spike detection (0-1), default from config
        """
        self.spike_threshold = spike_threshold or Config.AUDIO_SPIKE_THRESHOLD

    def extract_audio_from_video(self, video_path: str) -> Optional[str]:
        """
        Extract audio from video file.

        Args:
            video_path: Path to video file

        Returns:
            Path to extracted audio file or None if failed
        """
        try:
            video_path = Path(video_path)
            audio_path = Config.TEMP_PATH / f"{video_path.stem}_audio.wav"

            print_info("Extracting audio from video...")

            # Use moviepy to extract audio
            video = VideoFileClip(str(video_path))

            if video.audio is None:
                print_warning("Video has no audio track")
                return None

            video.audio.write_audiofile(
                str(audio_path),
                codec='pcm_s16le',
                verbose=False,
                logger=None
            )

            video.close()

            print_success(f"Audio extracted to: {audio_path.name}")

            return str(audio_path)

        except Exception as e:
            print_error(f"Failed to extract audio: {str(e)}")
            return None

    def detect_audio_spikes(self, audio_path: str, min_spike_duration: float = 0.5) -> List[Dict]:
        """
        Detect audio spikes (sudden volume increases).

        Args:
            audio_path: Path to audio file
            min_spike_duration: Minimum spike duration in seconds

        Returns:
            List of spike information dictionaries
        """
        try:
            print_info("Analyzing audio for spikes...")

            # Load audio
            y, sr = librosa.load(audio_path, sr=None)

            # Calculate short-time energy
            frame_length = int(sr * 0.05)  # 50ms frames
            hop_length = int(sr * 0.025)   # 25ms hop

            # RMS energy
            rms = librosa.feature.rms(y=y, frame_length=frame_length, hop_length=hop_length)[0]

            # Normalize RMS
            rms_normalized = rms / (np.max(rms) + 1e-6)

            # Find spikes (energy above threshold)
            spike_frames = np.where(rms_normalized > self.spike_threshold)[0]

            if len(spike_frames) == 0:
                print_info("No audio spikes detected")
                return []

            # Convert frames to time
            times = librosa.frames_to_time(spike_frames, sr=sr, hop_length=hop_length)

            # Group consecutive spikes
            spikes = []
            current_spike_start = times[0]
            current_spike_end = times[0]

            for i in range(1, len(times)):
                if times[i] - times[i-1] < 0.1:  # Within 100ms
                    current_spike_end = times[i]
                else:
                    # Save current spike if it meets duration requirement
                    duration = current_spike_end - current_spike_start
                    if duration >= min_spike_duration:
                        spikes.append({
                            'start_time': float(current_spike_start),
                            'end_time': float(current_spike_end),
                            'duration': float(duration),
                            'peak_energy': float(np.max(rms_normalized[
                                int(current_spike_start * sr / hop_length):
                                int(current_spike_end * sr / hop_length)
                            ]))
                        })

                    # Start new spike
                    current_spike_start = times[i]
                    current_spike_end = times[i]

            # Add final spike
            duration = current_spike_end - current_spike_start
            if duration >= min_spike_duration:
                spikes.append({
                    'start_time': float(current_spike_start),
                    'end_time': float(current_spike_end),
                    'duration': float(duration),
                    'peak_energy': float(np.max(rms_normalized[
                        int(current_spike_start * sr / hop_length):
                        int(current_spike_end * sr / hop_length)
                    ]))
                })

            print_success(f"Detected {len(spikes)} audio spikes")

            return spikes

        except Exception as e:
            print_error(f"Failed to detect audio spikes: {str(e)}")
            return []

    def detect_beat_drops(self, audio_path: str) -> List[Dict]:
        """
        Detect beat drops and significant tempo changes.

        Args:
            audio_path: Path to audio file

        Returns:
            List of beat drop information
        """
        try:
            print_info("Detecting beat drops...")

            # Load audio
            y, sr = librosa.load(audio_path, sr=None)

            # Onset detection (sudden changes in energy)
            onset_env = librosa.onset.onset_strength(y=y, sr=sr)
            onsets = librosa.onset.onset_detect(
                onset_envelope=onset_env,
                sr=sr,
                units='time',
                backtrack=True
            )

            # Get onset strengths
            onset_frames = librosa.onset.onset_detect(
                onset_envelope=onset_env,
                sr=sr,
                backtrack=True
            )

            beat_drops = []

            for i, onset_time in enumerate(onsets):
                if i < len(onset_frames):
                    strength = onset_env[onset_frames[i]]

                    # Consider significant beats (above median)
                    if strength > np.median(onset_env) * 1.5:
                        beat_drops.append({
                            'time': float(onset_time),
                            'strength': float(strength)
                        })

            print_success(f"Detected {len(beat_drops)} beat drops")

            return beat_drops

        except Exception as e:
            print_error(f"Failed to detect beat drops: {str(e)}")
            return []

    def analyze_audio_segments(self, audio_path: str, segment_duration: float = 30.0) -> List[Dict]:
        """
        Analyze audio in segments for energy and engagement patterns.

        Args:
            audio_path: Path to audio file
            segment_duration: Duration of each segment in seconds

        Returns:
            List of segment analysis results
        """
        try:
            print_info("Analyzing audio segments...")

            # Load audio
            y, sr = librosa.load(audio_path, sr=None)

            duration = len(y) / sr
            num_segments = int(np.ceil(duration / segment_duration))

            segments = []

            for i in range(num_segments):
                start_time = i * segment_duration
                end_time = min((i + 1) * segment_duration, duration)

                start_sample = int(start_time * sr)
                end_sample = int(end_time * sr)

                segment_audio = y[start_sample:end_sample]

                # Calculate features
                rms = librosa.feature.rms(y=segment_audio)[0]
                zcr = librosa.feature.zero_crossing_rate(segment_audio)[0]
                spectral_centroid = librosa.feature.spectral_centroid(y=segment_audio, sr=sr)[0]

                segments.append({
                    'start_time': start_time,
                    'end_time': end_time,
                    'duration': end_time - start_time,
                    'energy': float(np.mean(rms)),
                    'energy_variance': float(np.var(rms)),
                    'zero_crossing_rate': float(np.mean(zcr)),
                    'spectral_centroid': float(np.mean(spectral_centroid)),
                    'is_high_energy': float(np.mean(rms)) > np.mean(librosa.feature.rms(y=y)[0])
                })

            print_success(f"Analyzed {len(segments)} audio segments")

            return segments

        except Exception as e:
            print_error(f"Failed to analyze audio segments: {str(e)}")
            return []

    def get_viral_audio_moments(self, video_path: str) -> List[Dict]:
        """
        Identify viral-worthy audio moments (spikes, drops, high energy).

        Args:
            video_path: Path to video file

        Returns:
            List of viral audio moments with timestamps
        """
        # Extract audio
        audio_path = self.extract_audio_from_video(video_path)

        if not audio_path:
            return []

        # Detect features
        spikes = self.detect_audio_spikes(audio_path)
        beat_drops = self.detect_beat_drops(audio_path)
        segments = self.analyze_audio_segments(audio_path)

        # Combine and rank moments
        viral_moments = []

        # Add spikes
        for spike in spikes:
            viral_moments.append({
                'time': spike['start_time'],
                'type': 'audio_spike',
                'score': spike['peak_energy'] * 10,  # 0-10 scale
                'description': f"Audio spike (energy: {spike['peak_energy']:.2f})"
            })

        # Add beat drops
        for drop in beat_drops:
            viral_moments.append({
                'time': drop['time'],
                'type': 'beat_drop',
                'score': min(drop['strength'] / np.max([d['strength'] for d in beat_drops]) * 10, 10),
                'description': f"Beat drop (strength: {drop['strength']:.1f})"
            })

        # Add high energy segments
        for segment in segments:
            if segment['is_high_energy'] and segment['energy_variance'] > 0.01:
                viral_moments.append({
                    'time': segment['start_time'],
                    'type': 'high_energy_segment',
                    'score': min(segment['energy'] * 50, 10),
                    'description': f"High energy segment"
                })

        # Sort by score
        viral_moments.sort(key=lambda x: x['score'], reverse=True)

        print_success(f"Identified {len(viral_moments)} viral audio moments")

        return viral_moments
