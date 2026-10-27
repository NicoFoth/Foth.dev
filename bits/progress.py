import hashlib
import hmac

from django.conf import settings
from django.contrib import messages

from .registry import BY_KEY, MENU_PAGES, STARS

SESSION_KEY = 'stars'
SEEN_KEY = 'seen'


def collected(request):
    return [key for key in request.session.get(SESSION_KEY, []) if key in BY_KEY]


def award(request, key, notify=True):
    """Give the visitor a star. Returns True if it is a new one."""
    have = collected(request)
    if key in have:
        return False
    request.session[SESSION_KEY] = have + [key]
    if notify:
        messages.add_message(
            request, messages.SUCCESS,
            f'You found a star: {BY_KEY[key].title}! [{len(have) + 1}/{len(STARS)}]',
            extra_tags='star',
        )
    return True


def mark_seen(request, url_name):
    seen = request.session.get(SEEN_KEY, [])
    if url_name in seen:
        return
    seen = seen + [url_name]
    request.session[SEEN_KEY] = seen
    if set(MENU_PAGES) <= set(seen):
        award(request, 'explorer')


def seen(request):
    return request.session.get(SEEN_KEY, [])


def curl_code():
    """The unlock code printed for `curl foth.dev`. Stable per deployment."""
    secret = (settings.SECRET_KEY or 'foth.dev').encode()
    return hmac.new(secret, b'curl', hashlib.sha256).hexdigest()[:8]
