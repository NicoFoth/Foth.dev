"""Every bit that can be found on the site.

Together they make a 12-bit register. The order matters: the first entry is
bit 0, the rightmost LED in the status line.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Bit:
    key: str
    title: str
    hint: str


BITS = [
    Bit('teaser_a', 'Traced it', 'Solve part (a) of the brain teaser.'),
    Bit('teaser_b', 'Ten ones', 'Solve part (b) of the brain teaser.'),
    Bit('explorer', 'Tourist', 'Open every page in the menu.'),
    Bit('lost', 'No such file', 'Get lost.'),
    Bit('robots', 'Trespasser', 'Go where the robots are told not to.'),
    Bit('humans', 'Credits', 'Robots have a file of their own. So do humans.'),
    Bit('teapot', 'Short and stout', 'Ask the server for a coffee.'),
    Bit('curl', 'No browser required', 'Not everyone visits with a browser.'),
    Bit('sudo', 'Root access', 'Try to become root.'),
    Bit('konami', 'Cheat code', 'Some old cheat codes still work.'),
    Bit('flicker', 'Repair job', 'One LED on the front page is loose.'),
    Bit('owl', 'Night owl', 'Come back when you should be asleep.'),
]

BY_KEY = {bit.key: bit for bit in BITS}

# Bits that are discovered in the browser and reported back by site.js.
CLIENT_CLAIMABLE = {'sudo', 'konami', 'flicker', 'owl'}

# Visiting all of these (by view name) sets the "explorer" bit.
MENU_PAGES = {
    'pages:home', 'pages:about', 'pages:contact', 'pages:legal',
    'projects:index', 'teaser:sheet', 'bits:index', 'cs:index', 'poker:index',
}
