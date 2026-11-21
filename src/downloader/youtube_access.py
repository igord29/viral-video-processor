"""Helpers for YouTube's "confirm you're not a bot" check and for explaining download failures."""

import base64
import binascii
import os
import re
import tempfile
from contextlib import contextmanager
from typing import Iterator, Optional

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
def youtube_cookie_file() -> Iterator[Optional[str]]:
    """
    Yield the path of a private, throwaway copy of the configured cookies (None if there are none).

    yt-dlp writes back to the cookie file it is given, so every use gets its own copy, which is
    removed afterwards. That avoids concurrent downloads clobbering one shared file.
    """
    cookies = _configured_cookies()
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


def is_retryable(raw: Optional[str]) -> bool:
    """False for failures a retry cannot fix (bot check, private, unavailable, age-restricted)."""
    lowered = _ANSI_CODES.sub('', raw or '').lower()
    permanent = ('not a bot', 'private video', 'video unavailable', 'is not available',
                 'has been removed', 'confirm your age', 'age-restricted')
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
    if 'private video' in lowered:
        return 'This video is private, so it cannot be downloaded.'
    if 'age' in lowered and ('confirm your age' in lowered or 'age-restricted' in lowered):
        return ('This video is age-restricted. YouTube only allows it for a signed-in account, so '
                'YouTube cookies are needed (see "YouTube bot check" in the README).')
    if 'video unavailable' in lowered or 'is not available' in lowered or 'has been removed' in lowered:
        return 'This video is unavailable (removed, region-locked, or not public).'

    if not text:
        return 'Failed to fetch video info. Please check the URL and try again.'
    cleaned = _ERROR_PREFIX.sub('', text).strip() or text
    return cleaned[:300]
