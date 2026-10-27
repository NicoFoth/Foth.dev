import hmac
import json

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from .progress import award, collected, curl_code
from .registry import BITS, BY_KEY, CLIENT_CLAIMABLE


def index(request):
    have = set(collected(request))
    rows = [(i, bit, bit.key in have) for i, bit in enumerate(BITS)]
    value = sum(1 << i for i, _, found in rows if found)
    return render(request, 'bits/index.html', {
        'rows': rows,
        'hex': f'0x{value:03X}',
        'binary': f'{value:012b}',
    })


@require_POST
def claim(request):
    """Bits found in the browser (see site.js) are reported here."""
    try:
        payload = json.loads(request.body or b'{}')
    except ValueError:
        payload = {}
    key = payload.get('key')
    if key == 'curl':
        if not hmac.compare_digest(str(payload.get('code', '')).strip().lower(), curl_code()):
            return JsonResponse({'ok': False, 'error': 'invalid code'}, status=400)
    elif key not in CLIENT_CLAIMABLE:
        return JsonResponse({'ok': False, 'error': 'nice try'}, status=400)
    new = award(request, key, notify=False)
    return JsonResponse({
        'ok': True,
        'new': new,
        'title': BY_KEY[key].title,
        'count': len(collected(request)),
        'total': len(BITS),
    })


def nothing_to_see_here(request):
    award(request, 'robots')
    return render(request, 'bits/nothing.html')


def coffee(request):
    award(request, 'teapot')
    return render(request, 'bits/teapot.html', status=418)
