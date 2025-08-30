"""
Rate limiting middleware for API protection
"""

import time
from typing import Dict, Any
from fastapi import Request, Response, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import redis.asyncio as redis

from app.core.config import get_settings
from app.core.redis_client import get_redis

settings = get_settings()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware using sliding window - MVP version"""
    
    def __init__(self, app):
        super().__init__(app)
        self.redis_client = None
        self.redis_available = False
    
    async def dispatch(self, request: Request, call_next):
        """Process request with rate limiting (disabled for MVP)"""
        try:
            # For MVP, skip rate limiting entirely
            return await call_next(request)
            
        except Exception:
            # If anything fails, allow request through
            return await call_next(request)
