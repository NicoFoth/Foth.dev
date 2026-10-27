"""Every star that can be found on the site.

The order matters: star N lights up sky slot N in the landing page scene.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Star:
    key: str
    title: str
    hint: str


STARS = [
    Star('teaser_a', 'Traced it', 'Solve part (a) of the brain teaser.'),
    Star('teaser_b', 'Ten ones', 'Solve part (b) of the brain teaser.'),
    Star('explorer', 'Tourist', 'Visit every page in the menu.'),
    Star('lost', 'Off the map', 'Get lost.'),
    Star('robots', 'Trespasser', 'Go where the robots are told not to.'),
    Star('humans', 'Credits', 'Humans read the source.'),
    Star('teapot', 'Short and stout', 'Ask the server for a coffee.'),
    Star('curl', 'No browser required', 'Not everyone visits with a browser.'),
    Star('sudo', 'Root access', 'Try to become root.'),
    Star('konami', 'Cheat code', 'Some old cheat codes still work.'),
    Star('moon', 'Moonstruck', 'Some things in the sky are clickable.'),
    Star('owl', 'Night owl', 'Come back when you should be asleep.'),
]

BY_KEY = {star.key: star for star in STARS}

# Stars that are discovered in the browser and reported back by site.js.
CLIENT_CLAIMABLE = {'sudo', 'konami', 'moon', 'owl'}

# Visiting all of these (by view name) earns the "explorer" star.
MENU_PAGES = {
    'pages:home', 'pages:about', 'pages:contact', 'pages:legal',
    'projects:index', 'teaser:sheet', 'stars:index', 'cs:index', 'poker:index',
}
