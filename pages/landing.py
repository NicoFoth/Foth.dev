"""The landing page: an LED dot-matrix panel that spells NICO, and the page list.

Rendered as HTML for browsers and as ANSI text for `curl foth.dev`.
"""
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from bits.progress import collected, curl_code, seen

# 5x7 glyphs, one column of space between letters and a one-LED margin all round.
GLYPHS = {
    'N': ['#...#', '#...#', '##..#', '#.#.#', '#..##', '#...#', '#...#'],
    'I': ['.###.', '..#..', '..#..', '..#..', '..#..', '..#..', '.###.'],
    'C': ['.###.', '#...#', '#....', '#....', '#....', '#...#', '.###.'],
    'O': ['.###.', '#...#', '#...#', '#...#', '#...#', '#...#', '.###.'],
}
WORD = 'NICO'
WIDTH = 1 + len(WORD) * 6  # 25
HEIGHT = 9

# The loose LED in the top right corner. Clicking it three times fixes it (site.js).
LOOSE = (WIDTH - 1, 0)

PAGES = [
    ('About', 'pages:about', 'Background, written by a chatbot and left as it is.'),
    ('Projects', 'projects:index', 'Things I built after work.'),
    ('Brain teaser', 'teaser:sheet', 'A small exercise from a first-semester problem sheet.'),
    ('Bits', 'bits:index', 'Twelve hidden bits and the ones you have found.'),
    ('Contact', 'pages:contact', 'Leave me a message.'),
    ('CS', 'cs:index', 'Elo ladder for our Counter-Strike evenings.'),
    ('Poker', 'poker:index', 'Chip counts from our home games.'),
    ('Legal', 'pages:legal', 'Impressum and privacy policy, in German.'),
]


def lit():
    """Coordinates (x, y) of every LED that is on."""
    on = set()
    for i, letter in enumerate(WORD):
        for y, row in enumerate(GLYPHS[letter]):
            for x, cell in enumerate(row):
                if cell == '#':
                    on.add((1 + i * 6 + x, 1 + y))
    return on


def panel(request):
    on = lit()
    fixed = 'flicker' in collected(request)
    leds = []
    for y in range(HEIGHT):
        for x in range(WIDTH):
            cx, cy = x * 10 + 5, y * 10 + 5
            if (x, y) == LOOSE:
                continue
            if (x, y) in on:
                # --d sets the delay of the power-on sweep, one step per diagonal
                leds.append(format_html('<circle class="on" cx="{}" cy="{}" r="3.8" style="--d:{}"/>', cx, cy, x + y))
            else:
                leds.append(format_html('<circle cx="{}" cy="{}" r="2.4"/>', cx, cy))
    x, y = LOOSE
    loose = format_html(
        '<g class="loose{}" data-loose role="button" tabindex="0" aria-label="{}">'
        '<circle class="hit" cx="{}" cy="{}" r="5"/><circle class="led" cx="{}" cy="{}" r="3.8"/></g>',
        ' fixed' if fixed else '', 'Repaired LED' if fixed else 'Loose LED',
        x * 10 + 5, y * 10 + 5, x * 10 + 5, y * 10 + 5,
    )
    return format_html(
        '<svg class="panel" viewBox="0 0 {} {}" role="img" aria-labelledby="panel-title">'
        '<title id="panel-title">NICO, spelled out in LEDs</title>{}{}</svg>',
        WIDTH * 10, HEIGHT * 10, mark_safe(''.join(leds)), loose,
    )


def pages(request):
    visited = set(seen(request))
    return [
        {'name': name, 'url': reverse(view), 'text': text, 'visited': view in visited}
        for name, view, text in PAGES
    ]


def context(request):
    return {'panel': panel(request), 'pages': pages(request)}


def text(request):
    on = lit()
    amber, dim, cyan, reset = '\x1b[1;38;5;214m', '\x1b[38;5;23m', '\x1b[38;5;80m', '\x1b[0m'
    rows = []
    for y in range(HEIGHT):
        rows.append('  ' + ''.join(f'{amber}██{reset}' if (x, y) in on else f'{dim}· {reset}' for x in range(WIDTH)))
    links = [f'  {cyan}{name:<13}{reset}{request.build_absolute_uri(reverse(view))}' for name, view, _ in PAGES]
    links.append(f'  {cyan}{"GitHub":<13}{reset}https://github.com/NicoFoth')
    return '\n'.join(rows) + f"""

  {amber}foth.dev{reset}  Nico Foth, software engineer.

""" + '\n'.join(links) + f"""

  You fetched this with a terminal instead of a browser. Respect.
  The website has a terminal too (press \x1b[1m:\x1b[0m). Type this into it:

      {amber}unlock {curl_code()}{reset}

"""

