from starlette.types import ASGIApp, Receive, Scope, Send
from backend.core.settings import APP_ENV


class SecurityHeadersMiddleware:
    """
    Middleware to add security headers to every response.
    """

    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                headers = dict(message.get("headers", []))
                # Add security headers
                headers[b"x-content-type-options"] = b"nosniff"
                headers[b"x-frame-options"] = b"DENY"
                headers[b"x-xss-protection"] = b"1; mode=block"
                headers[b"referrer-policy"] = b"strict-origin-when-cross-origin"
                # HSTS only for HTTPS requests and in production
                # Check if the request was made via HTTPS (using x-forwarded-proto header)
                forwarded_proto = scope.get("headers")
                is_https = False
                if forwarded_proto:
                    for header in forwarded_proto:
                        if header[0] == b"x-forwarded-proto" and header[1].lower() == b"https":
                            is_https = True
                            break
                # Also consider that the app might be behind a proxy that sets the scheme in X-Forwarded-Proto
                # If we are in production and the request is HTTPS, add HSTS
                if APP_ENV == "production" and is_https:
                    headers[b"strict-transport-security"] = b"max-age=31536000; includeSubDomains"
                # Re-encode headers to list of tuples
                message["headers"] = list(headers.items())
            await send(message)

        await self.app(scope, receive, send_wrapper)
