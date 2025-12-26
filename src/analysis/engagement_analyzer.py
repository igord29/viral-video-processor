"""Engagement analysis using Claude API."""

import anthropic
from typing import Dict, List, Optional
import json

from ..utils import Config, print_info, print_success, print_error, print_warning


class EngagementAnalyzer:
    """Analyze video transcripts for engagement potential using Claude."""

    def __init__(self):
        """Initialize the engagement analyzer."""
        self.client = anthropic.Anthropic(api_key=Config.ANTHROPIC_API_KEY)

    def analyze_segments(self, segments: List[Dict], context: str = "") -> List[Dict]:
        """
        Analyze transcript segments for engagement potential.

        Args:
            segments: List of transcript segments with start/end times and text
            context: Optional video context (title, description)

        Returns:
            List of scored clip candidates
        """
        print_info("Analyzing segments for engagement potential...")

        # Group segments into potential clips (15-60 seconds)
        potential_clips = self._create_potential_clips(segments)

        print_info(f"Found {len(potential_clips)} potential clips to analyze")

        # Analyze each potential clip
        scored_clips = []

        for i, clip in enumerate(potential_clips):
            if i % 5 == 0:  # Progress update every 5 clips
                print_info(f"Analyzing clip {i+1}/{len(potential_clips)}...")

            score_data = self._score_clip(clip, context)

            if score_data:
                scored_clips.append({
                    'start_time': clip['start_time'],
                    'end_time': clip['end_time'],
                    'duration': clip['duration'],
                    'text': clip['text'],
                    'score': score_data['score'],
                    'reason': score_data['reason'],
                    'hook_quality': score_data.get('hook_quality', 0),
                    'emotional_impact': score_data.get('emotional_impact', 0),
                    'information_density': score_data.get('information_density', 0),
                    'pacing': score_data.get('pacing', 0),
                })

        # Sort by score
        scored_clips.sort(key=lambda x: x['score'], reverse=True)

        print_success(f"Analysis complete: {len(scored_clips)} clips scored")

        return scored_clips

    def _create_potential_clips(self, segments: List[Dict]) -> List[Dict]:
        """
        Create potential clips from segments.

        Combines consecutive segments into clips between MIN and MAX duration.
        """
        min_duration = Config.MIN_CLIP_DURATION
        max_duration = Config.MAX_CLIP_DURATION

        potential_clips = []
        current_clip_segments = []
        current_start = None

        for segment in segments:
            if not current_clip_segments:
                current_clip_segments = [segment]
                current_start = segment['start']
            else:
                # Check if adding this segment would exceed max duration
                current_duration = segment['end'] - current_start

                if current_duration <= max_duration:
                    current_clip_segments.append(segment)
                else:
                    # Save current clip if it meets min duration
                    clip_duration = current_clip_segments[-1]['end'] - current_start
                    if clip_duration >= min_duration:
                        potential_clips.append({
                            'start_time': current_start,
                            'end_time': current_clip_segments[-1]['end'],
                            'duration': clip_duration,
                            'text': ' '.join(s['text'] for s in current_clip_segments)
                        })

                    # Start new clip
                    current_clip_segments = [segment]
                    current_start = segment['start']

        # Add final clip if valid
        if current_clip_segments:
            clip_duration = current_clip_segments[-1]['end'] - current_start
            if clip_duration >= min_duration:
                potential_clips.append({
                    'start_time': current_start,
                    'end_time': current_clip_segments[-1]['end'],
                    'duration': clip_duration,
                    'text': ' '.join(s['text'] for s in current_clip_segments)
                })

        return potential_clips

    def _score_clip(self, clip: Dict, context: str) -> Optional[Dict]:
        """
        Score a single clip using Claude API.

        Returns:
            Dictionary with score and breakdown, or None if failed
        """
        try:
            prompt = self._create_scoring_prompt(clip, context)

            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=500,
                temperature=0.3,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            # Parse response
            result_text = response.content[0].text

            # Try to extract JSON from response
            try:
                # Look for JSON in the response
                if '{' in result_text and '}' in result_text:
                    start_idx = result_text.index('{')
                    end_idx = result_text.rindex('}') + 1
                    json_str = result_text[start_idx:end_idx]
                    result = json.loads(json_str)
                else:
                    # Fallback: parse from structured text
                    result = self._parse_text_score(result_text)

                return result

            except json.JSONDecodeError:
                # Fallback parsing
                return self._parse_text_score(result_text)

        except Exception as e:
            print_warning(f"Failed to score clip: {str(e)}")
            return None

    def _create_scoring_prompt(self, clip: Dict, context: str) -> str:
        """Create the prompt for Claude to score a clip."""
        prompt = f"""Analyze this video transcript segment for viral engagement potential.

Context: {context if context else 'No context provided'}

Clip Duration: {clip['duration']:.1f} seconds
Transcript:
{clip['text']}

Score this clip on a scale of 1-10 for viral potential based on:

1. Hook Quality (1-10): Does it grab attention immediately? Is there a compelling opening?
2. Emotional Impact (1-10): Does it trigger emotions (excitement, curiosity, surprise, humor)?
3. Information Density (1-10): Is there valuable, interesting information packed in?
4. Pacing (1-10): Does it maintain energy and momentum throughout?

Provide your response in this JSON format:
{{
  "score": 7.5,
  "hook_quality": 8,
  "emotional_impact": 7,
  "information_density": 8,
  "pacing": 7,
  "reason": "Brief explanation of why this clip has viral potential or not"
}}

The overall score should be the weighted average:
- Hook Quality: 30%
- Emotional Impact: 30%
- Information Density: 20%
- Pacing: 20%

Be critical - only truly engaging content should score above 7."""

        return prompt

    def _parse_text_score(self, text: str) -> Dict:
        """
        Fallback parser for text-based scores.

        Attempts to extract scores from text if JSON parsing fails.
        """
        result = {
            'score': 5.0,
            'hook_quality': 5,
            'emotional_impact': 5,
            'information_density': 5,
            'pacing': 5,
            'reason': 'Unable to parse detailed analysis'
        }

        # Try to find numbers in the text
        lines = text.lower().split('\n')
        for line in lines:
            if 'score' in line and ':' in line:
                try:
                    score_str = line.split(':')[1].strip().split()[0]
                    result['score'] = float(score_str)
                except:
                    pass
            elif 'hook' in line and ':' in line:
                try:
                    score_str = line.split(':')[1].strip().split()[0]
                    result['hook_quality'] = int(float(score_str))
                except:
                    pass
            elif 'emotional' in line and ':' in line:
                try:
                    score_str = line.split(':')[1].strip().split()[0]
                    result['emotional_impact'] = int(float(score_str))
                except:
                    pass
            elif 'information' in line and ':' in line:
                try:
                    score_str = line.split(':')[1].strip().split()[0]
                    result['information_density'] = int(float(score_str))
                except:
                    pass
            elif 'pacing' in line and ':' in line:
                try:
                    score_str = line.split(':')[1].strip().split()[0]
                    result['pacing'] = int(float(score_str))
                except:
                    pass
            elif 'reason' in line and ':' in line:
                result['reason'] = line.split(':', 1)[1].strip()

        return result

    def get_top_clips(self, scored_clips: List[Dict], n: int = None) -> List[Dict]:
        """
        Get top N clips by score.

        Args:
            scored_clips: List of scored clips
            n: Number of clips to return (defaults to Config.TOP_CLIPS_TO_SHOW)

        Returns:
            Top N clips
        """
        if n is None:
            n = Config.TOP_CLIPS_TO_SHOW

        return scored_clips[:n]
