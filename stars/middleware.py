from .progress import mark_seen
from .registry import MENU_PAGES


class SeenPagesMiddleware:
    """Remembers which menu pages a visitor has opened (for the "explorer" star)."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        match = request.resolver_match
        if match and match.view_name in MENU_PAGES and request.method == 'GET':
            mark_seen(request, match.view_name)
        return None
