import hmac
import json

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.http import require_POST

from .context_processors import versions
from .progress import award, collected, curl_code
from .registry import BY_KEY, CLIENT_CLAIMABLE, STARS


def stars_page(request):
    have = set(collected(request))
    rows = [(i, star, star.key in have) for i, star in enumerate(STARS, start=1)]
    return render(request, 'stars/stars.html', {'rows': rows})


@require_POST
def claim(request):
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


def robots_txt(request):
    lines = [
        'User-agent: *',
        'Disallow: /admin/',
        'Disallow: /admin-login/',
        'Disallow: /nothing-to-see-here/',
        '',
    ]
    return HttpResponse('\n'.join(lines), content_type='text/plain; charset=utf-8')


def humans_txt(request):
    award(request, 'humans', notify=False)
    v = versions()
    body = f"""/* TEAM */
    Developer: Nico Foth
    Site: https://foth.dev
    GitHub: https://github.com/NicoFoth

/* THANKS */
    Eric Wastl, for Advent of Code and its unmistakable look.

/* SITE */
    Standards: HTML, CSS, a little vanilla JS
    Components: Django {v['django']}, Python {v['python']}, SQLite {v['sqlite']}
    Font: Source Code Pro (self-hosted)
    Build step: none

    You found a star for reading this. Check {request.build_absolute_uri(reverse('stars_page'))}
"""
    return HttpResponse(body, content_type='text/plain; charset=utf-8')


def nothing_to_see_here(request):
    award(request, 'robots')
    return render(request, 'stars/nothing.html')


def coffee(request):
    award(request, 'teapot')
    return render(request, 'stars/teapot.html', status=418)


def not_found(request, exception=None):
    award(request, 'lost')
    return render(request, 'stars/404.html', status=404)
