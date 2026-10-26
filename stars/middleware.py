import time

from .progress import mark_seen
from .registry import MENU_PAGES

RENDER_MARKER = b'<!--render-ms-->'


class StarsMiddleware:
    """Tracks which menu pages a visitor has seen and stamps the render time."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start = time.perf_counter()
        response = self.get_response(request)
        if (not response.streaming
                and response.get('Content-Type', '').startswith('text/html')
                and RENDER_MARKER in response.content):
            elapsed = f'{(time.perf_counter() - start) * 1000:.1f}ms'.encode()
            response.content = response.content.replace(RENDER_MARKER, elapsed)
            if response.has_header('Content-Length'):
                response['Content-Length'] = len(response.content)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        match = request.resolver_match
        if match and match.url_name in MENU_PAGES and request.method == 'GET':
            mark_seen(request, match.url_name)
        return None
