import hmac
import json

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from .progress import award, collected, curl_code
from .registry import BY_KEY, CLIENT_CLAIMABLE, STARS


def index(request):
    have = set(collected(request))
    rows = [(i, star, star.key in have) for i, star in enumerate(STARS, start=1)]
    return render(request, 'stars/stars.html', {'rows': rows})


@require_POST
def claim(request):
    """Stars found in the browser (see site.js) are reported here."""
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
        'total': len(STARS),
    })


def nothing_to_see_here(request):
    award(request, 'robots')
    return render(request, 'stars/nothing.html')


def coffee(request):
    award(request, 'teapot')
    return render(request, 'stars/teapot.html', status=418)
