"""Common test fixtures and utilities."""

import httpx


def handle_not_found(request: httpx.Request) -> httpx.Response:
    """Handle 404 responses."""
    return httpx.Response(404, json={"error": "Not found"})


def build_transport(*handlers):
    """Build mock transport with route handlers.

    Args:
        *handlers: Tuples of (method, path, handler_function).
    """
    routes = {(method, path): handler for method, path, handler in handlers}

    def router(request: httpx.Request) -> httpx.Response:
        key = (request.method, request.url.path)
        handler = routes.get(key)
        if handler:
            return handler(request)
        return handle_not_found(request)

    return httpx.MockTransport(router)


# Reusable page skeleton
PAGE_BASE = {
    "count": 0,
    "next": None,
    "previous": None,
    "results": [],
}
