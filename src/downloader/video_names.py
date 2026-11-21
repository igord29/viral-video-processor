"""Chooses the file name for a downloaded video, so two videos with the same title never share a file."""

import json
import os
import threading
from itertools import count
from pathlib import Path
from typing import Dict, Iterator, Optional

VIDEO_EXTENSIONS = ('.mp4', '.webm', '.mkv', '.avi')

# Kept next to the videos: which video (site and ID) each downloaded file holds
INDEX_FILENAME = '.video_index.json'

_lock = threading.Lock()
# Names taken by downloads that are still running: full path without extension -> video
_in_flight: Dict[str, str] = {}


def safe_stem(text: Optional[str], max_length: int = 100) -> str:
    """A title reduced to characters that are safe in a file name on every platform."""
    cleaned = "".join(c for c in (text or '') if c.isalnum() or c in (' ', '-', '_')).strip()
    return cleaned[:max_length].strip()


def video_key(info: dict) -> Optional[str]:
    """Identify a video by site and ID (None when the ID is not known)."""
    video_id = str(info.get('id') or '')
    if not video_id or video_id == 'unknown':
        return None
    extractor = str(info.get('extractor') or 'unknown')
    if extractor.lower() == 'generic':
        # For a plain file link the "ID" is only the file's name, which other links can share
        return f"generic:{info.get('webpage_url') or video_id}"
    return f"{extractor}:{video_id}"


def _read_index(folder: Path) -> Dict[str, str]:
    try:
        with open(folder / INDEX_FILENAME, encoding='utf-8') as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def _write_index(folder: Path, index: Dict[str, str]) -> None:
    # Forget files that have since been deleted, then replace the index in one step
    index = {name: key for name, key in index.items() if (folder / name).exists()}
    tmp_path = folder / f"{INDEX_FILENAME}.tmp"
    try:
        with open(tmp_path, 'w', encoding='utf-8') as f:
            json.dump(index, f, indent=2, ensure_ascii=False)
        os.replace(tmp_path, folder / INDEX_FILENAME)
    except OSError:
        pass  # the index is a convenience; a download must not fail because of it


def _existing_video(folder: Path, stem: str) -> Optional[Path]:
    for ext in VIDEO_EXTENSIONS:
        candidate = folder / f"{stem}{ext}"
        if candidate.exists():
            return candidate
    return None


def _is_free(folder: Path, stem: str, key: str) -> bool:
    running = _in_flight.get(str(folder / stem))
    if running is not None:
        return running == key
    # Any existing file counts as taken, including one we have no record of: reusing its name
    # would make yt-dlp skip this download as "already downloaded"
    return _existing_video(folder, stem) is None


def _candidate_names(title_stem: str, id_stem: str) -> Iterator[str]:
    yield title_stem
    if id_stem and id_stem != title_stem:
        yield f"{title_stem} - {id_stem}"
    for number in count(2):
        yield f"{title_stem} - {number}"


def claim_name(folder: Path, title: Optional[str], key: Optional[str], video_id: Optional[str]) -> str:
    """
    Return the file name (without extension) to save a video under, and hold it until
    release_name() is called.

    A video that is already in the folder keeps its name, so it is not downloaded twice.
    Otherwise the name is the title; if a different video already uses that, the video's ID
    (or failing that a number) is added, so that one download can never stand in for another.
    """
    id_stem = safe_stem(str(video_id or ''))
    title_stem = safe_stem(title) or id_stem or 'video'
    if not key:
        return title_stem  # cannot tell videos apart without an ID: keep the plain title

    with _lock:
        known = [name for name, owner in _read_index(folder).items()
                 if owner == key and Path(name).suffix in VIDEO_EXTENSIONS and (folder / name).exists()]
        if known:
            stem = Path(known[0]).stem
        else:
            stem = next(name for name in _candidate_names(title_stem, id_stem) if _is_free(folder, name, key))
        _in_flight[str(folder / stem)] = key
        return stem


def release_name(folder: Path, stem: str, key: Optional[str], saved_file: Optional[Path] = None) -> None:
    """Stop holding a name. When the download succeeded, remember which video the file holds."""
    if not key:
        return
    with _lock:
        _in_flight.pop(str(folder / stem), None)
        if saved_file is not None:
            index = _read_index(folder)
            index[Path(saved_file).name] = key
            _write_index(folder, index)
