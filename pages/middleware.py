import time

RENDER_MARKER = b'<!--render-ms-->'


class RenderTimeMiddleware:
    """Replaces the marker in the footer with how long the request took."""

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
