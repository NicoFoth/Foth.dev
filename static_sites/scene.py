"""The ASCII night scene on the landing page.

The picture is composited from sprites onto a character canvas. Every sprite
has a colour mask of the same shape, so the result can be rendered either as
HTML spans or as ANSI escapes for `curl foth.dev`.

Mask characters map to CSS classes (``.sc-<char>`` in site.css) and to the ANSI
colours in ``ANSI``. A space in a sprite is transparent; ``OPAQUE`` paints a
blank that hides whatever is behind it.
"""
import random

OPAQUE = '`'
WIDTH = 58
HEIGHT = 21

# The twelve sky positions that light up as visitors collect stars, in the
# order of stars.registry.STARS.
STAR_SLOTS = [
    (1, 18), (2, 27), (1, 47), (4, 12), (5, 29), (4, 49),
    (6, 22), (6, 52), (7, 3), (3, 55), (0, 37), (5, 40),
]

DUST = [
    (0, 12), (1, 31), (2, 14), (2, 51), (3, 21), (4, 37), (5, 18), (5, 56),
    (6, 43), (8, 46), (0, 25), (7, 11), (6, 32), (0, 55),
]

MOON = (0, 2, [
    "  _.._",
    ".' .-'\"",
    "/  /",
    "|  |",
    "\\  \\",
    "'._'-._",
], [
    "  mmmm",
    "mm mmmm",
    "m  m",
    "m  m",
    "m  m",
    "mmmmmmm",
])

PLANE = (2, 34, [
    "        __|__",
    "--o--o--(_)--o--o--",
], [
    "        ppppp",
    "ppRppppppppppppppGpp",
])

BRIDGE = (7, 6, [
    "            _.--''''''''''--._",
    "        _.-'/\\/\\/\\/\\/\\/\\/\\/\\'-._",
    "     .-'/\\/\\/\\/\\/\\/\\/\\/\\/\\/\\/\\/\\'-.",
    "   .'/\\/\\/\\/\\/\\/\\/\\/\\/\\/\\/\\/\\/\\/\\/\\'.",
    "__/_/\\/\\/\\/\\/\\/\\/\\/\\/\\/\\/\\/\\/\\/\\/\\/\\_\\__",
    "===*=========*=========*=========*=========*",
    "  ||       ||                    ||       ||",
], [
    "            AAAAAAAAAAAAAAAAAA",
    "        AAAAhhhhhhhhhhhhhhhhAAAA",
    "     AAAhhhhhhhhhhhhhhhhhhhhhhhhAAA",
    "   AAhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhAA",
    "DDAAhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhAADD",
    "DDDLDDDDDDDDDLDDDDDDDDDLDDDDDDDDDLDDDDDDDDDL",
    "  PP       PP                    PP       PP",
])

HOUSE = (9, 0, [
    "  /\\",
    " /  \\",
    " |[]|",
    "_|__|__",
    "^^^^^^^\\",
], [
    "  HH",
    " HHHH",
    " HyyH",
    "gHHHHgg",
    "gggggggg",
])

LIGHTHOUSE = (7, 51, [
    "  _",
    " (*)",
    " |=|",
    " | |",
    " |=|",
    " | |",
    "/___\\",
    "^^^^^^^",
], [
    "  x",
    " xYx",
    " rrr",
    " x x",
    " rrr",
    " x x",
    "xxxxx",
    "eeeeeee",
])

BOAT = (13, 25, [
    "  |\\",
    "  |`\\",
    "  |__\\",
    "\\_____/",
], [
    "  ss",
    "  s s",
    "  ssss",
    "bbbbbbb",
])

WATER_TOP = 14

# ANSI 256-colour codes for the curl rendering.
ANSI = {
    'm': 229, 'p': 250, 'R': 196, 'G': 46, 'A': 252, 'h': 60, 'D': 245,
    'L': 227, 'P': 240, 'H': 250, 'y': 227, 'g': 34, 'x': 252, 'r': 196,
    'Y': 227, 'e': 94, 's': 252, 'b': 130, 'w': 26, 'W': 33, 'd': 238,
    '*': 236, 'O': 227,
}


def _blank():
    return [[' '] * WIDTH for _ in range(HEIGHT)], [[' '] * WIDTH for _ in range(HEIGHT)]


def _stamp(chars, mask, sprite):
    top, left, lines, masks = sprite
    for dy, (line, line_mask) in enumerate(zip(lines, masks)):
        for dx, ch in enumerate(line):
            if ch == ' ':
                continue
            y, x = top + dy, left + dx
            if 0 <= y < HEIGHT and 0 <= x < WIDTH:
                chars[y][x] = ch
                mask[y][x] = line_mask[dx] if dx < len(line_mask) else ' '


def _water(chars, mask):
    rng = random.Random(1907)  # deterministic, so the sea doesn't jump between requests
    for y in range(WATER_TOP, HEIGHT):
        density = 0.18 + 0.05 * (y - WATER_TOP)
        for x in range(WIDTH):
            if chars[y][x] == OPAQUE:
                chars[y][x] = ' '
                continue
            if chars[y][x] != ' ':
                continue
            if y == WATER_TOP or rng.random() < density:
                chars[y][x] = '~'
                mask[y][x] = 'W' if rng.random() < 0.25 else 'w'


def build(lit=()):
    """Return the scene as rows of (text, mask_char) runs.

    ``lit`` is a collection of indices into STAR_SLOTS that should glow.
    """
    chars, mask = _blank()
    for y, x in DUST:
        chars[y][x], mask[y][x] = '.', 'd'
    for i, (y, x) in enumerate(STAR_SLOTS):
        chars[y][x], mask[y][x] = '*', 'O' if i in lit else '*'
    for sprite in (MOON, PLANE, BRIDGE, HOUSE, LIGHTHOUSE):
        _stamp(chars, mask, sprite)
    # Piers reach down into the sea before the water is painted around them.
    for x in (8, 9, 17, 18, 38, 39, 47, 48):
        chars[WATER_TOP][x], mask[WATER_TOP][x] = '|', 'P'
    _stamp(chars, mask, BOAT)
    _water(chars, mask)

    rows = []
    for y in range(HEIGHT):
        runs = []
        for ch, m in zip(chars[y], mask[y]):
            m = m if ch != ' ' else ' '
            if runs and runs[-1][1] == m:
                runs[-1][0] += ch
            else:
                runs.append([ch, m])
        rows.append([(text, m) for text, m in runs])
    return rows


def ansi(rows):
    out = []
    for runs in rows:
        line = ''
        for text, m in runs:
            code = ANSI.get(m)
            line += f'\x1b[38;5;{code}m{text}\x1b[0m' if code else text
        out.append(line)
    return out
