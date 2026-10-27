from .progress import collected
from .registry import STARS


def stars(request):
    have = collected(request)
    return {
        'star_keys': have,
        'star_count': len(have),
        'star_total': len(STARS),
        'star_order': [star.key for star in STARS],
    }
