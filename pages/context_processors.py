import functools
import platform
import random
import sqlite3
from pathlib import Path

import django
from django.conf import settings

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
    """Short hash of the deployed commit, read straight from .git (no git binary needed)."""
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
    match = getattr(request, 'resolver_match', None)
    return {
        'subtitle': random.choice(SUBTITLES),
        'build_sha': build_sha(),
        'versions': versions(),
        # 'pages:about' and 'projects' respectively; the nav uses them to mark the current page
        'current': match.view_name if match else '',
        'section': match.namespace if match else '',
    }
