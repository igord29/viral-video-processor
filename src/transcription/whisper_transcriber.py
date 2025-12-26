"""Audio transcription using OpenAI Whisper."""

import whisper
from pathlib import Path
from typing import Dict, List, Optional
import json

from ..utils import print_info, print_success, print_error, get_progress_context


class WhisperTranscriber:
    """Transcribe audio using Whisper."""

    def __init__(self, model_size: str = "base"):
        """
        Initialize Whisper transcriber.

        Args:
            model_size: Whisper model size (tiny, base, small, medium, large)
                       - tiny: fastest, least accurate
                       - base: good balance for most use cases
                       - small: better accuracy
                       - medium/large: best accuracy, slowest
        """
        self.model_size = model_size
        self.model = None

    def load_model(self):
        """Load Whisper model."""
        if self.model is None:
            print_info(f"Loading Whisper {self.model_size} model...")
            self.model = whisper.load_model(self.model_size)
            print_success(f"Whisper {self.model_size} model loaded")

    def transcribe_video(self, video_path: str, language: str = None) -> Optional[Dict]:
        """
        Transcribe video file.

        Args:
            video_path: Path to video file
            language: Optional language code (e.g., 'en', 'es')

        Returns:
            Transcription result with segments and full text
        """
        try:
            self.load_model()

            print_info(f"Transcribing video: {Path(video_path).name}")

            # Transcribe with word-level timestamps
            result = self.model.transcribe(
                video_path,
                language=language,
                word_timestamps=True,
                verbose=False
            )

            # Process segments
            segments = []
            for segment in result['segments']:
                segments.append({
                    'id': segment['id'],
                    'start': segment['start'],
                    'end': segment['end'],
                    'text': segment['text'].strip(),
                    'words': segment.get('words', [])
                })

            transcription = {
                'text': result['text'],
                'segments': segments,
                'language': result.get('language', 'unknown')
            }

            print_success(f"Transcription complete: {len(segments)} segments")

            return transcription

        except Exception as e:
            print_error(f"Transcription failed: {str(e)}")
            return None

    def save_transcription(self, transcription: Dict, output_path: str):
        """
        Save transcription to JSON file.

        Args:
            transcription: Transcription dictionary
            output_path: Output file path
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(transcription, f, indent=2, ensure_ascii=False)

            print_success(f"Transcription saved to: {output_path}")

        except Exception as e:
            print_error(f"Failed to save transcription: {str(e)}")

    def load_transcription(self, input_path: str) -> Optional[Dict]:
        """
        Load transcription from JSON file.

        Args:
            input_path: Input file path

        Returns:
            Transcription dictionary or None if failed
        """
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                transcription = json.load(f)

            print_success(f"Transcription loaded from: {input_path}")
            return transcription

        except Exception as e:
            print_error(f"Failed to load transcription: {str(e)}")
            return None

    def get_segment_text(self, transcription: Dict, start_time: float, end_time: float) -> str:
        """
        Get text for a specific time range.

        Args:
            transcription: Transcription dictionary
            start_time: Start time in seconds
            end_time: End time in seconds

        Returns:
            Concatenated text for the time range
        """
        segments = transcription.get('segments', [])
        text_parts = []

        for segment in segments:
            seg_start = segment['start']
            seg_end = segment['end']

            # Check if segment overlaps with requested range
            if seg_start < end_time and seg_end > start_time:
                text_parts.append(segment['text'])

        return ' '.join(text_parts).strip()

    def create_srt(self, transcription: Dict, output_path: str):
        """
        Create SRT subtitle file from transcription.

        Args:
            transcription: Transcription dictionary
            output_path: Output SRT file path
        """
        try:
            segments = transcription.get('segments', [])

            with open(output_path, 'w', encoding='utf-8') as f:
                for i, segment in enumerate(segments, 1):
                    start = self._format_srt_time(segment['start'])
                    end = self._format_srt_time(segment['end'])

                    f.write(f"{i}\n")
                    f.write(f"{start} --> {end}\n")
                    f.write(f"{segment['text']}\n\n")

            print_success(f"SRT file saved to: {output_path}")

        except Exception as e:
            print_error(f"Failed to create SRT file: {str(e)}")

    def _format_srt_time(self, seconds: float) -> str:
        """Format time in SRT format (HH:MM:SS,mmm)."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)

        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
