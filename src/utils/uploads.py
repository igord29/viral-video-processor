"""
Video uploads from the browser, sent in pieces so that large files work.

A large video cannot go up in one request: hosts such as Railway end any request whose body takes
longer than a few minutes to arrive. So the browser sends the file in pieces ("chunks"), each one
appended to a partial file here, and the upload can carry on from where it stopped after a dropped
connection, a closed page or a server restart.

How far an upload has got is always the size of its partial file on disk, so a piece that was cut
off half-way is never counted twice: the browser asks where to carry on and resends from there.
"""

import json
import os
import re
import shutil
import subprocess
import threading
import time
import uuid
from pathlib import Path
from typing import Dict, Optional

from .config import Config
from ..downloader.video_names import safe_stem

# Video types accepted for upload (the same ones the Videos library lists)
VIDEO_EXTENSIONS = ('.mp4', '.mov', '.m4v', '.mkv', '.avi', '.webm')

# Size of each piece the browser sends. Small enough to arrive within Railway's 5-minute limit
# per request even on a slow home connection (8 MB at 1 Mbit/s takes about a minute).
CHUNK_SIZE = 8 * 1024 * 1024

# Room kept free on the disk beyond the video itself, for clips, analyses and temporary files
SPACE_MARGIN = 200 * 1024 * 1024

# Unfinished uploads left alone this long are deleted to free their space
ABANDONED_AFTER_SECONDS = 3 * 24 * 3600

_UPLOAD_ID = re.compile(r'[0-9a-f]{32}')
_BLOCK = 1024 * 1024

_locks: Dict[str, threading.Lock] = {}
_locks_guard = threading.Lock()
_finish_guard = threading.Lock()


class UploadError(Exception):
    """A problem to show the person uploading, with the HTTP status to answer with."""

    def __init__(self, message: str, status: int = 400, **details):
        super().__init__(message)
        self.status = status
        self.details = details


def uploads_folder() -> Path:
    """Where unfinished uploads are kept (on the volume when one is attached, so they survive restarts)."""
    folder = Config.TEMP_PATH / 'uploads'
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def destination_folder() -> Path:
    """Finished uploads go into the Videos folder of the library (downloads from links go to Downloads)."""
    Config.VIDEO_PATH.mkdir(parents=True, exist_ok=True)
    return Config.VIDEO_PATH


def free_space() -> int:
    """Bytes free on the disk that holds the library."""
    return shutil.disk_usage(destination_folder()).free


def format_size(num_bytes: float) -> str:
    for unit in ('bytes', 'KB', 'MB', 'GB'):
        if num_bytes < 1024 or unit == 'GB':
            return f"{num_bytes:.0f} {unit}" if unit == 'bytes' else f"{num_bytes:.1f} {unit}"
        num_bytes /= 1024
    return f"{num_bytes:.1f} GB"


def _split_name(name: str):
    """Name and extension (lower case), with the extension after the last dot ("....mp4" counts as an MP4)."""
    stem, dot, extension = name.rpartition('.')
    return (stem, '.' + extension.lower()) if dot else (name, '')


def _lock_for(upload_id: str) -> threading.Lock:
    with _locks_guard:
        return _locks.setdefault(upload_id, threading.Lock())


def _paths(upload_id: str):
    if not isinstance(upload_id, str) or not _UPLOAD_ID.fullmatch(upload_id):
        raise UploadError('Upload not found', 404)
    folder = uploads_folder()
    return folder / f'{upload_id}.part', folder / f'{upload_id}.json'


def _read_info(upload_id: str) -> Dict:
    part, meta = _paths(upload_id)
    try:
        with open(meta, encoding='utf-8') as f:
            info = json.load(f)
    except (OSError, ValueError):
        raise UploadError('Upload not found', 404)
    if not part.exists():
        raise UploadError('Upload not found', 404)
    return info


def status(upload_id: str) -> Dict:
    """Name, total size and bytes received so far."""
    info = _read_info(upload_id)
    part, _ = _paths(upload_id)
    return {'upload_id': upload_id, 'name': info['name'], 'size': info['size'], 'received': part.stat().st_size}


def remove_abandoned() -> None:
    """Delete unfinished uploads nobody has touched for days, so they do not fill the disk."""
    now = time.time()
    for path in uploads_folder().glob('*.part'):
        try:
            if now - path.stat().st_mtime > ABANDONED_AFTER_SECONDS:
                path.unlink()
                path.with_suffix('.json').unlink(missing_ok=True)
        except OSError:
            pass


def reserved_by_others(except_id: Optional[str] = None) -> int:
    """Bytes still to arrive for the other unfinished uploads, which need space too."""
    total = 0
    for meta in uploads_folder().glob('*.json'):
        if meta.stem == except_id:
            continue
        try:
            with open(meta, encoding='utf-8') as f:
                size = int(json.load(f)['size'])
            total += max(0, size - meta.with_suffix('.part').stat().st_size)
        except (OSError, ValueError, KeyError, TypeError):
            pass
    return total


def start(name, size) -> Dict:
    """Begin an upload. Checks the file type and that the video will fit on the disk."""
    if not isinstance(name, str) or not name.strip():
        raise UploadError('The file has no name')
    extension = _split_name(name)[1]
    if extension not in VIDEO_EXTENSIONS:
        raise UploadError(f'"{name}" is not a video file this app can use. '
                          f'Supported types: {", ".join(ext.lstrip(".").upper() for ext in VIDEO_EXTENSIONS)}.')
    if isinstance(size, bool) or not isinstance(size, int) or size <= 0:
        raise UploadError(f'"{name}" is empty or its size is unknown')

    remove_abandoned()
    available = free_space() - reserved_by_others() - SPACE_MARGIN
    if size > available:
        raise UploadError(
            f'There is not enough space on the server for "{name}" ({format_size(size)}; '
            f'{format_size(max(0, available))} available). Delete videos or clips you no longer need, '
            'or make the storage volume bigger.', 507)

    upload_id = uuid.uuid4().hex
    part, meta = _paths(upload_id)
    part.touch()
    with open(meta, 'w', encoding='utf-8') as f:
        json.dump({'name': name, 'size': size, 'started': time.time()}, f)
    return {'upload_id': upload_id, 'name': name, 'size': size, 'received': 0, 'chunk_size': CHUNK_SIZE}


def receive_chunk(upload_id: str, offset, stream) -> Dict:
    """
    Append one piece, which must start where the partial file ends. A piece sent from the wrong
    place (for example a retry of one that did arrive) is refused with the right place to resume.
    """
    with _lock_for(upload_id):
        info = _read_info(upload_id)
        part, _ = _paths(upload_id)
        received = part.stat().st_size

        if offset != received:
            raise UploadError('Resume from the server\'s position', 409, received=received)

        with open(part, 'ab') as f:
            while True:
                block = stream.read(_BLOCK)
                if not block:
                    break
                if received + len(block) > info['size']:
                    f.truncate(received)
                    raise UploadError('More data was sent than the file\'s size', 400, received=received)
                f.write(block)
                received += len(block)
        return {'received': received, 'size': info['size']}


def _looks_like_video(path: Path) -> Optional[bool]:
    """True if ffprobe finds a video stream, False if it finds none, None if ffprobe is unavailable."""
    ffprobe = shutil.which('ffprobe')
    if not ffprobe:
        return None
    try:
        result = subprocess.run(
            [ffprobe, '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=codec_type',
             '-of', 'csv=p=0', str(path)],
            capture_output=True, text=True, timeout=120)
    except (OSError, subprocess.SubprocessError):
        return None
    return 'video' in result.stdout


def _free_name(folder: Path, name: str) -> Path:
    """A file name in the folder based on the uploaded one, adding (2), (3)... if it is taken."""
    stem, extension = _split_name(name)
    stem = safe_stem(stem) or 'upload'
    candidate = folder / f'{stem}{extension}'
    number = 2
    while candidate.exists():
        candidate = folder / f'{stem} ({number}){extension}'
        number += 1
    return candidate


def finish(upload_id: str) -> Dict:
    """Check the complete file is a video and move it into the library."""
    with _lock_for(upload_id):
        info = _read_info(upload_id)
        part, meta = _paths(upload_id)
        received = part.stat().st_size
        if received != info['size']:
            raise UploadError('The upload is not complete yet', 409, received=received)

        if _looks_like_video(part) is False:
            discard(upload_id)
            raise UploadError(f'"{info["name"]}" could not be read as a video. The file may be damaged; '
                              'try uploading it again.', 422)

        with _finish_guard:  # two uploads of the same name must not pick the same file name
            final = _free_name(destination_folder(), info['name'])
            shutil.move(str(part), str(final))
        meta.unlink(missing_ok=True)

    with _locks_guard:
        _locks.pop(upload_id, None)
    return {'filename': final.name, 'path': str(final), 'size': final.stat().st_size}


def discard(upload_id: str) -> None:
    """Cancel an upload and delete what had arrived."""
    part, meta = _paths(upload_id)
    part.unlink(missing_ok=True)
    meta.unlink(missing_ok=True)
