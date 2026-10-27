"""The landing page: the night scene from scene.py with the site menu drawn into it.

Rendered as HTML for browsers and as ANSI text for `curl foth.dev`.
"""
from django.urls import reverse
from django.utils.html import escape, format_html
from django.utils.safestring import mark_safe

from stars.progress import collected, curl_code, seen
from stars.registry import STARS

from . import scene

# Rows of the scene that double as menu entries: (row, label, view name or url).
MENU = [
    (4, 'about', 'pages:about'),
    (5, 'projects', 'projects:index'),
    (6, 'teaser', 'teaser:sheet'),
    (7, 'stars', 'stars:index'),
    (8, 'contact', 'pages:contact'),
    (9, 'cs', 'cs:index'),
    (10, 'poker', 'poker:index'),
    (11, 'github', 'https://github.com/NicoFoth'),
    (12, 'terminal', '#terminal'),
    (13, 'legal', 'pages:legal'),
]

SLOTS = {pos: i for i, pos in enumerate(scene.STAR_SLOTS)}


def _is_url(target):
    return target.startswith(('#', 'http'))


def _sky(request):
    """The scene, with a lit sky slot for every star this visitor has found."""
    have = set(collected(request))
    return scene.build(lit=[i for i, star in enumerate(STARS) if star.key in have])


def _marks(request, label, target):
    """The little stars after a menu entry: puzzle parts solved, or page visited."""
    if label == 'teaser':
        have = collected(request)
        return ['teaser_a' in have, 'teaser_b' in have]
    if _is_url(target):
        return []
    return [target in seen(request)]


def html(request):
    # Built here rather than in a template: the scene is white-space: pre, so
    # every stray space or newline between tags would show up on screen.
    out = []
    for y, runs in enumerate(_sky(request)):
        art, x = '', 0
        for text, m in runs:
            if m == ' ':
                art += escape(text)
            elif m in ('*', 'O'):  # a star slot; site.js lights it up when a star is found
                art += format_html('<span class="sc-{}" data-slot="{}">{}</span>', m, SLOTS[(y, x)], text)
            else:
                art += format_html('<span class="sc-{}{}">{}</span>', m, ' moon' if m == 'm' else '', text)
            x += len(text)
        out.append(_menu_row(request, y, art) or f'<span>{art}</span>')
    return mark_safe(''.join(out))


def _menu_row(request, y, art):
    entry = next((e for e in MENU if e[0] == y), None)
    if entry is None:
        return None
    _, label, target = entry
    href = target if _is_url(target) else reverse(target)
    marks = ''.join(f'<span class="cal-mark{" on" if on else ""}">*</span>' for on in _marks(request, label, target))
    extra = ' data-open-terminal' if target == '#terminal' else ''
    return format_html(
        '<a href="{}"{}>{}  <span class="cal-label">{}</span>{}</a>',
        href, mark_safe(extra), mark_safe(art), f'{label:<9}', mark_safe(marks),
    )


def text(request):
    art = scene.ansi(_sky(request))
    for row, label, target in MENU:
        if target == '#terminal':
            continue
        href = target if _is_url(target) else request.build_absolute_uri(reverse(target))
        art[row] += f'   \x1b[38;5;34m{label:<9}\x1b[0m \x1b[38;5;240m{href}\x1b[0m'
    return '\n'.join(art) + f"""

  \x1b[1;38;5;46mFoth.dev\x1b[0m  Nico Foth, software engineer.

  You fetched this with a terminal instead of a browser. Respect.
  The website has a terminal too (press \x1b[1m:\x1b[0m). Type this into it:

      \x1b[38;5;227munlock {curl_code()}\x1b[0m

"""
