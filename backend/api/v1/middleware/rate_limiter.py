"""
Rate Limiter Middleware

This module provides rate limiting functionality for API endpoints.
Supports both in-memory and Redis-based rate limiting with configurable
windows and limits.
"""

import time
from typing import Dict, Optional, Callable, Any
from functools import wraps
from collections import defaultdict
from datetime import datetime, timedelta

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse

from utils.logger import logger


class RateLimiter:
    """
    In-memory rate limiter implementation using sliding window algorithm.
    
    This implementation stores request timestamps and enforces rate limits
    based on configurable time windows and maximum request counts.
    """
    
    def __init__(self) -> None:
        """Initialize the rate limiter with empty storage."""
        # Storage: {identifier: [(timestamp, request_count), ...]}
        self._storage: Dict[str, list] = defaultdict(list)
        self._lock_storage: Dict[str, float] = {}  # Temporary lockout storage
        
    def _clean_old_requests(self, identifier: str, window_seconds: int) -> None:
        """
        Remove expired requests from storage.
        
        Args:
            identifier: Unique identifier for the client
            window_seconds: Time window in seconds
        """
        current_time = time.time()
        cutoff_time = current_time - window_seconds
        
        # Remove requests older than the window
        self._storage[identifier] = [
            (ts, count) for ts, count in self._storage[identifier]
            if ts > cutoff_time
        ]
    
    def is_rate_limited(
        self,
        identifier: str,
        max_requests: int,
        window_seconds: int
    ) -> tuple[bool, Dict[str, Any]]:
        """
        Check if the identifier has exceeded the rate limit.
        
        Args:
            identifier: Unique identifier for the client (IP, user ID, etc.)
            max_requests: Maximum number of requests allowed in the window
            window_seconds: Time window in seconds
            
        Returns:
            Tuple of (is_limited, rate_limit_info)
        """
        current_time = time.time()
        
        # Check if client is temporarily locked out
        if identifier in self._lock_storage:
            lockout_until = self._lock_storage[identifier]
            if current_time < lockout_until:
                remaining_lockout = int(lockout_until - current_time)
                return True, {
                    "limited": True,
                    "retry_after": remaining_lockout,
                    "reason": "temporary_lockout"
                }
            else:
                # Lockout expired
                del self._lock_storage[identifier]
        
        # Clean old requests
        self._clean_old_requests(identifier, window_seconds)
        
        # Count requests in current window
        request_count = sum(count for _, count in self._storage[identifier])
        
        # Calculate rate limit info
        remaining = max(0, max_requests - request_count)
        reset_time = int(current_time + window_seconds)
        
        rate_limit_info = {
            "limit": max_requests,
            "remaining": remaining,
            "reset": reset_time,
            "window": window_seconds
        }
        
        # Check if rate limit exceeded
        if request_count >= max_requests:
            logger.warning(f"Rate limit exceeded for identifier: {identifier}")
            return True, {
                **rate_limit_info,
                "limited": True,
                "retry_after": window_seconds
            }
        
        # Record this request
        self._storage[identifier].append((current_time, 1))
        
        return False, {
            **rate_limit_info,
            "limited": False
        }
    
    def reset_limit(self, identifier: str) -> None:
        """
        Reset rate limit for a specific identifier.
        
        Args:
            identifier: Unique identifier to reset
        """
        if identifier in self._storage:
            del self._storage[identifier]
        if identifier in self._lock_storage:
            del self._lock_storage[identifier]
        logger.info(f"Rate limit reset for identifier: {identifier}")
    
    def apply_lockout(self, identifier: str, lockout_seconds: int) -> None:
        """
        Apply a temporary lockout to an identifier.
        
        Args:
            identifier: Unique identifier to lockout
            lockout_seconds: Duration of lockout in seconds
        """
        lockout_until = time.time() + lockout_seconds
        self._lock_storage[identifier] = lockout_until
        logger.warning(f"Applied {lockout_seconds}s lockout to identifier: {identifier}")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get rate limiter statistics.
        
        Returns:
            Dictionary with current statistics
        """
        return {
            "total_clients": len(self._storage),
            "locked_out_clients": len(self._lock_storage),
            "total_tracked_requests": sum(
                sum(count for _, count in requests)
                for requests in self._storage.values()
            )
        }


# Global rate limiter instance
_rate_limiter = RateLimiter()


def get_client_identifier(request: Request) -> str:
    """
    Extract a unique identifier from the request.
    
    Priority: API Key > User ID > IP Address
    
    Args:
        request: FastAPI request object
        
    Returns:
        Unique client identifier
    """
    # Check for API key in headers
    api_key = request.headers.get("X-API-Key")
    if api_key:
        return f"api_key:{api_key}"
    
    # Check for user ID (if authentication is implemented)
    # user_id = getattr(request.state, "user_id", None)
    # if user_id:
    #     return f"user:{user_id}"
    
    # Fall back to IP address
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        ip = forwarded.split(",")[0].strip()
    else:
        ip = request.client.host if request.client else "unknown"
    
    return f"ip:{ip}"


def rate_limit(
    max_requests: int = 100,
    window_seconds: int = 60,
    identifier_func: Optional[Callable[[Request], str]] = None
):
    """
    Decorator for rate limiting API endpoints.
    
    Args:
        max_requests: Maximum number of requests allowed in the window
        window_seconds: Time window in seconds
        identifier_func: Optional custom function to extract client identifier
        
    Returns:
        Decorated function with rate limiting
        
    Example:
        ```python
        @router.get("/endpoint")
        @rate_limit(max_requests=10, window_seconds=60)
        async def my_endpoint():
            return {"message": "Success"}
        ```
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract request from args/kwargs
            request: Optional[Request] = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            
            if not request:
                request = kwargs.get("request")
            
            if not request:
                # No request found, skip rate limiting
                logger.warning("Rate limiter: No request object found, skipping")
                return await func(*args, **kwargs)
            
            # Get client identifier
            identifier = identifier_func(request) if identifier_func else get_client_identifier(request)
            
            # Check rate limit
            is_limited, rate_info = _rate_limiter.is_rate_limited(
                identifier,
                max_requests,
                window_seconds
            )
            
            # Add rate limit headers to response
            if is_limited:
                logger.warning(
                    f"Rate limit exceeded for {identifier}: "
                    f"{max_requests} requests per {window_seconds}s"
                )
                
                # Return 429 Too Many Requests
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "detail": "Rate limit exceeded",
                        "retry_after": rate_info.get("retry_after", window_seconds),
                        "limit": rate_info["limit"],
                        "window": rate_info["window"]
                    },
                    headers={
                        "X-RateLimit-Limit": str(rate_info["limit"]),
                        "X-RateLimit-Remaining": "0",
                        "X-RateLimit-Reset": str(rate_info["reset"]),
                        "Retry-After": str(rate_info.get("retry_after", window_seconds))
                    }
                )
            
            # Execute the endpoint
            response = await func(*args, **kwargs)
            
            # Add rate limit info to response headers if it's a Response object
            if hasattr(response, "headers"):
                response.headers["X-RateLimit-Limit"] = str(rate_info["limit"])
                response.headers["X-RateLimit-Remaining"] = str(rate_info["remaining"])
                response.headers["X-RateLimit-Reset"] = str(rate_info["reset"])
            
            return response
        
        return wrapper
    return decorator


class RateLimitMiddleware:
    """
    Global rate limiting middleware for FastAPI.
    
    This middleware applies rate limiting to all requests globally.
    Use this for application-wide rate limiting.
    """
    
    def __init__(
        self,
        max_requests: int = 1000,
        window_seconds: int = 3600
    ) -> None:
        """
        Initialize the middleware.
        
        Args:
            max_requests: Maximum requests per window (default: 1000/hour)
            window_seconds: Time window in seconds (default: 3600s = 1 hour)
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.rate_limiter = _rate_limiter
    
    async def __call__(self, request: Request, call_next):
        """
        Process the request with rate limiting.
        
        Args:
            request: FastAPI request object
            call_next: Next middleware/endpoint in chain
            
        Returns:
            Response with rate limit headers
        """
        # Get client identifier
        identifier = get_client_identifier(request)
        
        # Check rate limit
        is_limited, rate_info = self.rate_limiter.is_rate_limited(
            identifier,
            self.max_requests,
            self.window_seconds
        )
        
        if is_limited:
            logger.warning(f"Global rate limit exceeded for {identifier}")
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": "Too many requests",
                    "retry_after": rate_info.get("retry_after", self.window_seconds)
                },
                headers={
                    "X-RateLimit-Limit": str(rate_info["limit"]),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(rate_info["reset"]),
                    "Retry-After": str(rate_info.get("retry_after", self.window_seconds))
                }
            )
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(rate_info["limit"])
        response.headers["X-RateLimit-Remaining"] = str(rate_info["remaining"])
        response.headers["X-RateLimit-Reset"] = str(rate_info["reset"])
        
        return response


# Export utilities
def get_rate_limiter() -> RateLimiter:
    """Get the global rate limiter instance."""
    return _rate_limiter
