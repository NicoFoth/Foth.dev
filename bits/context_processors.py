from .progress import collected
from .registry import BITS


def bits(request):
    have = collected(request)
    return {
        'bit_keys': have,
        'bit_count': len(have),
        'bit_total': len(BITS),
        'bit_order': [bit.key for bit in BITS],
    }
