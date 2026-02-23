"""
Security Middleware - Anonymity & Rate Limiting
"""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp
import time
from collections import defaultdict

class SecurityMiddleware(BaseHTTPMiddleware):
    """
    Custom security middleware:
    - No IP logging
    - Basic rate limiting (per-minute)
    - No session tracking
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.request_times = defaultdict(list)
        self.max_requests_per_minute = 10
    
    async def dispatch(self, request: Request, call_next):
        """Process request through security checks"""
        
        # Extract client IP (but don't log it)
        client_ip = request.client.host if request.client else "unknown"
        
        # Basic rate limiting (in-memory, resets on app restart)
        current_time = time.time()
        minute_ago = current_time - 60
        
        # Clean old entries
        self.request_times[client_ip] = [
            t for t in self.request_times[client_ip] if t > minute_ago
        ]
        
        # Check rate limit
        if len(self.request_times[client_ip]) >= self.max_requests_per_minute:
            return Response(
                content="Rate limit exceeded",
                status_code=429
            )
        
        self.request_times[client_ip].append(current_time)
        
        # Process request
        response = await call_next(request)
        
        # Ensure no sensitive headers leak
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        
        # Don't log anything
        
        return response