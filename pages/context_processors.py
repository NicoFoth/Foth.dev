import functools
import platform
import sqlite3
from pathlib import Path

import django
from django.conf import settings

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


# Every page is laid out like a man page. Its header reads NAME(SECTION), looked up
# by view name first, then by app namespace. The sections follow man(1).
MAN_PAGES = {
    'pages:home': ('foth', '1'),
    'pages:about': ('about', '7'),
    'pages:contact': ('contact', '1'),
    'pages:legal': ('legal', '7'),
    'pages:login': ('login', '8'),
    'bits:nothing': ('robots', '5'),
    'bits:coffee': ('coffee', '418'),
    'projects': ('projects', '1'),
    'teaser': ('teaser', '6'),
    'bits': ('bits', '4'),
    'cs': ('cs', '6'),
    'poker': ('poker', '6'),
}
MAN_SECTIONS = {
    '1': 'User Commands',
    '3': 'Library Functions',
    '4': 'Special Files',
    '5': 'File Formats',
    '6': 'Games',
    '7': 'Miscellaneous',
    '8': 'System Administration',
    '418': 'Coffee Pot Control Protocol',
}


def man_page(view_name, namespace):
    name, section = MAN_PAGES.get(view_name) or MAN_PAGES.get(namespace) or ('foth', '?')
    return {'title': f'{name.upper()}({section})', 'manual': MAN_SECTIONS.get(section, 'foth.dev manual')}


def site(request):
    match = getattr(request, 'resolver_match', None)
    return {
        # no match means a 404, which gets the man page of the error it is: ENOENT(3)
        'man': man_page(match.view_name, match.namespace) if match else {'title': 'ENOENT(3)', 'manual': MAN_SECTIONS['3']},
        'build_sha': build_sha(),
        'versions': versions(),
        # shown in the status line, like a shell prompt: ~/cs/season/3
        'shell_path': '~' + request.path.rstrip('/'),
        # 'pages:about' and 'projects' respectively; the nav uses them to mark the current page
        'current': match.view_name if match else '',
        'section': match.namespace if match else '',
    }
