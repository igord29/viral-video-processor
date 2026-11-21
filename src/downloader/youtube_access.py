"""Helpers for YouTube's "confirm you're not a bot" check and for explaining download failures."""

import base64
import binascii
import importlib.util
import os
import re
import shutil
import subprocess
import tempfile
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Iterator, List, Optional

from ..utils import Config

NETSCAPE_HEADER = '# Netscape HTTP Cookie File'

_BASE64_ONLY = re.compile(r'[A-Za-z0-9+/=\s]+')
_ANSI_CODES = re.compile(r'\x1b\[[0-9;]*m')
_ERROR_PREFIX = re.compile(r'^(?:ERROR:\s*)?(?:\[[\w:]+\]\s*)?[\w-]{6,}:\s*')


def normalize_cookies(raw: str) -> str:
    """
    Turn pasted cookie text into a Netscape cookies.txt that yt-dlp can read.

    Accepts the file contents as-is, base64 of it, or text whose tabs were turned into spaces
    on the way in (which web forms sometimes do). Returns '' when no cookie lines are found.
    """
    text = (raw or '').strip()
    if not text:
        return ''

    # A block made only of base64 characters (cookie lines always contain '.' and tabs/spaces)
    if _BASE64_ONLY.fullmatch(text):
        try:
            text = base64.b64decode(''.join(text.split()), validate=True).decode('utf-8')
        except (binascii.Error, UnicodeDecodeError, ValueError):
            pass

    lines = []
    for line in text.splitlines():
        line = line.strip('\r\n')
        stripped = line.strip()
        if not stripped:
            continue
        # Comments are dropped (the header is added below); #HttpOnly_ marks a real cookie
        if stripped.startswith('#') and not stripped.startswith('#HttpOnly_'):
            continue
        if len(stripped.split('\t')) == 7:
            lines.append(stripped)
            continue
        # Tabs were lost: fields are domain, flag, path, secure, expiry, name, value
        parts = stripped.split()
        if len(parts) >= 6:
            lines.append('\t'.join(parts[:6] + [' '.join(parts[6:])]))

    if not lines:
        return ''
    return '\n'.join([NETSCAPE_HEADER] + lines) + '\n'


def _configured_cookies() -> str:
    """Cookie text from YOUTUBE_COOKIES_FILE if set and readable, else from YOUTUBE_COOKIES."""
    if Config.YOUTUBE_COOKIES_FILE:
        try:
            with open(Config.YOUTUBE_COOKIES_FILE, encoding='utf-8') as f:
                return normalize_cookies(f.read())
        except OSError:
            return ''
    return normalize_cookies(Config.YOUTUBE_COOKIES)


def cookies_configured() -> bool:
    """True when usable YouTube cookies have been provided."""
    return bool(_configured_cookies())


@contextmanager
def youtube_cookie_file(enabled: bool = True) -> Iterator[Optional[str]]:
    """
    Yield the path of a private, throwaway copy of the configured cookies (None if there are none,
    or if enabled is False).

    yt-dlp writes back to the cookie file it is given, so every use gets its own copy, which is
    removed afterwards. That avoids concurrent downloads clobbering one shared file.
    """
    cookies = _configured_cookies() if enabled else ''
    if not cookies:
        yield None
        return

    fd, path = tempfile.mkstemp(prefix='ytcookies_', suffix='.txt')  # created readable by us only
    try:
        with os.fdopen(fd, 'w', encoding='utf-8', newline='\n') as f:
            f.write(cookies)
        yield path
    finally:
        try:
            os.remove(path)
        except OSError:
            pass


_UNAVAILABLE = ('video unavailable', 'this video is not available', 'no longer available',
                'has been removed', 'this video is private', 'private video')
_NO_FORMATS = ('requested format is not available', 'no video formats found')


@dataclass(frozen=True)
class Strategy:
    """One way of asking YouTube for a video."""
    name: str
    use_cookies: bool
    extractor_args: Optional[dict] = None


def download_strategies() -> List[Strategy]:
    """
    The ways to ask YouTube for a video, in the order to try them.

    With cookies, YouTube can answer the signed-in web clients with streaming-only formats that
    have no direct download link, so if those fail we fall back to the TV/Safari clients and
    then to signed-out clients that need no proof-of-origin token.
    """
    if not cookies_configured():
        return [Strategy('default clients', use_cookies=False)]
    return [
        Strategy('signed in, default clients', use_cookies=True),
        Strategy('signed in, TV and Safari clients', use_cookies=True,
                 extractor_args={'youtube': {'player_client': ['tv', 'web_safari']}}),
        Strategy('signed out, clients that need no token', use_cookies=False,
                 extractor_args={'youtube': {'player_client': ['android_vr', 'tv_simply', 'mweb', 'web_embedded']}}),
    ]


def is_video_gone(raw: Optional[str]) -> bool:
    """True when the video itself is private/removed, so trying other ways of asking cannot help."""
    lowered = _ANSI_CODES.sub('', raw or '').lower()
    return any(marker in lowered for marker in _UNAVAILABLE)


class DiagnosticLogger:
    """
    A yt-dlp logger that keeps its messages instead of printing them, so that when every way of
    asking YouTube fails the server log can say why (yt-dlp's own explanation of what it tried).
    """

    _USEFUL = re.compile(r'\[youtube\]|\[jsc|\[pot\]|js runtimes|client|format|signature|challenge|sabr|po token|cookies',
                         re.IGNORECASE)
    _SKIP = re.compile(r'params:|Proxy map|videoplayback|Command-line|Encodings|Python |Extractor Plugins',
                       re.IGNORECASE)

    def __init__(self):
        self.lines: List[str] = []

    def debug(self, msg):
        self.lines.append(str(msg))

    def info(self, msg):
        pass

    def warning(self, msg):
        self.lines.append(str(msg))

    def error(self, msg):
        self.lines.append(str(msg))

    def summary(self, limit: int = 30) -> List[str]:
        """The lines worth putting in a log: the useful ones, trimmed, with no repeats."""
        seen, kept = set(), []
        for line in self.lines:
            line = _ANSI_CODES.sub('', line).strip()
            line = line.splitlines()[0] if line else ''  # first line only: the rest is often a traceback
            if not line or self._SKIP.search(line) or not self._USEFUL.search(line) or line in seen:
                continue
            seen.add(line)
            kept.append(line[:260])
        return kept[-limit:]


def find_js_runtime() -> Optional[str]:
    """Path of the Node.js binary yt-dlp uses to solve YouTube's challenges (None if absent)."""
    return shutil.which('node') or shutil.which('nodejs')


def js_runtime_status() -> str:
    """Say whether the Node.js found is one yt-dlp will actually use (it rejects old versions)."""
    path = find_js_runtime()
    if not path:
        return 'MISSING'
    try:
        # Ask yt-dlp itself, so the answer follows whatever minimum version it currently requires
        from yt_dlp.utils._jsruntime import NodeJsRuntime
        info = NodeJsRuntime(path).info
        if info is None:
            return f'{path} UNUSABLE (could not run it)'
        version, supported = info.version, info.supported
    except Exception:
        try:
            out = subprocess.run([path, '--version'], capture_output=True, text=True, timeout=10).stdout
            version = out.strip().lstrip('v') or 'unknown'
            supported = version.split('.')[0].isdigit() and int(version.split('.')[0]) >= 22
        except (OSError, subprocess.SubprocessError):
            return f'{path} UNUSABLE (could not run it)'
    if supported:
        return f'{path} v{version} (accepted by yt-dlp)'
    return f'{path} v{version} UNSUPPORTED (yt-dlp needs a newer Node.js, so YouTube formats will be missing)'


def tooling_summary() -> str:
    """One line saying which downloader tools were found, for the startup log."""
    solver = importlib.util.find_spec('yt_dlp_ejs') is not None
    return (f"ffmpeg: {'found' if shutil.which('ffmpeg') else 'MISSING'} | "
            f"JS runtime: {js_runtime_status()} | "
            f"YouTube challenge solver (yt-dlp-ejs): {'installed' if solver else 'MISSING'}")


def is_retryable(raw: Optional[str]) -> bool:
    """False for failures a retry cannot fix (bot check, private, unavailable, no formats, age check)."""
    lowered = _ANSI_CODES.sub('', raw or '').lower()
    permanent = ('not a bot', 'confirm your age', 'age-restricted') + _UNAVAILABLE + _NO_FORMATS
    return not any(marker in lowered for marker in permanent)


def describe_download_error(raw: Optional[str]) -> str:
    """Turn a raw yt-dlp error into a short message that says what to do about it."""
    text = _ANSI_CODES.sub('', raw or '').strip()
    lowered = text.lower()

    if 'not a bot' in lowered:  # not "sign in to confirm": the age check starts the same way
        if cookies_configured():
            return ("YouTube is still asking this server to prove it isn't a bot, even with the saved "
                    "cookies. They have probably expired: export fresh YouTube cookies and update the "
                    "YOUTUBE_COOKIES variable (see \"YouTube bot check\" in the README).")
        return ("YouTube is blocking downloads from this server (\"Sign in to confirm you're not a bot\"). "
                "Add YouTube cookies to fix it: set the YOUTUBE_COOKIES variable "
                "(see \"YouTube bot check\" in the README).")
    if 'private video' in lowered or 'this video is private' in lowered:
        return 'This video is private, so it cannot be downloaded.'
    if 'confirm your age' in lowered or 'age-restricted' in lowered:
        return ('This video is age-restricted. YouTube only allows it for a signed-in account, so '
                'YouTube cookies are needed (see "YouTube bot check" in the README).')
    if any(marker in lowered for marker in _NO_FORMATS):
        return ("YouTube did not offer any downloadable formats for this video. This is usually a "
                "problem with the downloader's YouTube support on this server, not with the video: "
                "check the startup log's 'Downloader' line for anything MISSING.")
    if any(marker in lowered for marker in _UNAVAILABLE):
        return 'This video is unavailable (removed, region-locked, or not public).'

    if not text:
        return 'Failed to fetch video info. Please check the URL and try again.'
    cleaned = _ERROR_PREFIX.sub('', text).strip() or text
    return cleaned[:300]
