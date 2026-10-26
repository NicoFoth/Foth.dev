import functools
import platform
import random
import sqlite3
from pathlib import Path

import django
from django.conf import settings

from .progress import collected
from .registry import STARS

# Like the year under the Advent of Code logo, the name under ours is wrapped
# in a different language's syntax on every request.
SUBTITLES = [
    ('λ.', ''), ('{:', '}'), ('<', '/>'), ('/*', '*/'), ('$', ''), ('&', ''),
    ('', '++'), ('', '!()'), ('@', ''), ('', '()'), ('#', ''), ('', ';'),
    ("'", ''), ('(', ')'), ('//', ''), ('*', ''), ('::', ''), ('%', ''),
    ('--', ''), ('0x', ''), ('$(', ')'), ('`', '`'), ('[', ']'), ('', ':='),
]


@functools.lru_cache(maxsize=1)
def build_sha():
    git = Path(settings.BASE_DIR) / '.git'
    try:
        head = (git / 'HEAD').read_text().strip()
        if not head.startswith('ref: '):
            return head[:7]
        ref = head[5:]
        ref_file = git / ref
        if ref_file.exists():
            return ref_file.read_text().strip()[:7]
        for line in (git / 'packed-refs').read_text().splitlines():
            if line.endswith(' ' + ref):
                return line[:7]
    except OSError:
        pass
    return 'dev'


@functools.lru_cache(maxsize=1)
def versions():
    return {
        'django': django.get_version(),
        'python': platform.python_version(),
        'sqlite': sqlite3.sqlite_version,
    }


def site(request):
    stars = collected(request)
    match = getattr(request, 'resolver_match', None)
    return {
        'star_keys': stars,
        'star_count': len(stars),
        'star_total': len(STARS),
        'star_order': [star.key for star in STARS],
        'subtitle': random.choice(SUBTITLES),
        'build_sha': build_sha(),
        'versions': versions(),
        'current': match.url_name if match else '',
    }
