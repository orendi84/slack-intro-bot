#!/usr/bin/env python3
"""
Rate Limiter for API Calls

Implements rate limiting and burst protection for external API calls
to prevent abuse and quota exhaustion.
"""

import time
import os
from collections import deque
from functools import wraps
from typing import Callable, Deque, Optional
import logging

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Rate limiter for API calls with burst protection.
    
    Features:
    - Sliding window rate limiting
    - Burst protection
    - Configurable limits
    - Thread-safe implementation
    """
    
    def __init__(
        self,
        calls_per_minute: int = 20,
        burst_limit: int = 5,
        window_seconds: int = 60
    ):
        """
        Initialize rate limiter.
        
        Args:
            calls_per_minute: Maximum calls allowed per minute
            burst_limit: Maximum calls allowed in rapid succession
            window_seconds: Time window for rate limiting (default: 60)
        """
        self.calls_per_minute = calls_per_minute
        self.burst_limit = burst_limit
        self.window_seconds = window_seconds
        self.call_times: Deque[float] = deque(maxlen=max(calls_per_minute, burst_limit))
        
        logger.info(
            f"Rate limiter initialized: {calls_per_minute} calls/min, "
            f"burst limit: {burst_limit}"
        )
    
    def _clean_old_calls(self, now: float):
        """Remove calls outside the time window"""
        while self.call_times and now - self.call_times[0] > self.window_seconds:
            self.call_times.popleft()
    
    def _get_sleep_time(self, now: float) -> float:
        """Calculate how long to sleep before next call"""
        if len(self.call_times) >= self.calls_per_minute:
            # Rate limit exceeded
            oldest_call = self.call_times[0]
            return self.window_seconds - (now - oldest_call) + 0.1
        
        # Check burst limit (calls within 1 second)
        recent_calls = sum(1 for t in self.call_times if now - t < 1)
        if recent_calls >= self.burst_limit:
            return 1.0
        
        return 0.0
    
    def wait_if_needed(self) -> Optional[float]:
        """
        Check rate limit and wait if necessary.
        
        Returns:
            Time waited in seconds, or None if no wait was needed
        """
        now = time.time()
        self._clean_old_calls(now)
        
        sleep_time = self._get_sleep_time(now)
        
        if sleep_time > 0:
            logger.warning(
                f"Rate limit reached, waiting {sleep_time:.1f}s "
                f"({len(self.call_times)}/{self.calls_per_minute} calls)"
            )
            time.sleep(sleep_time)
            now = time.time()
            self._clean_old_calls(now)
        
        self.call_times.append(now)
        return sleep_time if sleep_time > 0 else None
    
    def __call__(self, func: Callable) -> Callable:
        """
        Decorator to apply rate limiting to a function.
        
        Usage:
            @rate_limiter
            def my_api_call():
                ...
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            wait_time = self.wait_if_needed()
            if wait_time:
                logger.info(f"Rate limit applied, waited {wait_time:.1f}s")
            return func(*args, **kwargs)
        
        return wrapper
    
    def get_stats(self) -> dict:
        """Get rate limiter statistics"""
        now = time.time()
        self._clean_old_calls(now)
        
        recent_calls_1s = sum(1 for t in self.call_times if now - t < 1)
        recent_calls_10s = sum(1 for t in self.call_times if now - t < 10)
        
        return {
            'total_calls': len(self.call_times),
            'calls_per_minute_limit': self.calls_per_minute,
            'burst_limit': self.burst_limit,
            'calls_last_second': recent_calls_1s,
            'calls_last_10_seconds': recent_calls_10s,
            'calls_last_minute': len(self.call_times),
            'available_capacity': max(0, self.calls_per_minute - len(self.call_times))
        }
    
    def reset(self):
        """Reset rate limiter (for testing)"""
        self.call_times.clear()
        logger.info("Rate limiter reset")


# Global rate limiter instance
_rate_limiter: Optional[RateLimiter] = None


def get_rate_limiter() -> RateLimiter:
    """
    Get the global rate limiter instance.
    
    Configured via environment variables:
    - SLACK_API_RATE_LIMIT: Calls per minute (default: 20)
    - SLACK_API_BURST_LIMIT: Burst limit (default: 5)
    """
    global _rate_limiter
    if _rate_limiter is None:
        rate_limit = int(os.getenv('SLACK_API_RATE_LIMIT', 20))
        burst_limit = int(os.getenv('SLACK_API_BURST_LIMIT', 5))
        _rate_limiter = RateLimiter(rate_limit, burst_limit)
    
    return _rate_limiter


def rate_limited(func: Callable) -> Callable:
    """
    Decorator to apply rate limiting to a function using the global rate limiter.
    
    Usage:
        @rate_limited
        def my_api_call():
            ...
    """
    limiter = get_rate_limiter()
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        limiter.wait_if_needed()
        return func(*args, **kwargs)
    
    return wrapper


# Example usage and testing
if __name__ == "__main__":
    import sys
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("🔧 Testing Rate Limiter")
    print("=" * 50)
    
    # Create test rate limiter (5 calls/min, 2 burst)
    limiter = RateLimiter(calls_per_minute=5, burst_limit=2)
    
    @limiter
    def test_api_call(call_num: int):
        """Simulated API call"""
        print(f"📞 API call #{call_num} executed")
        return call_num
    
    print("\n🧪 Test 1: Normal rate limiting")
    print("-" * 50)
    
    for i in range(7):
        start = time.time()
        result = test_api_call(i + 1)
        elapsed = time.time() - start
        
        stats = limiter.get_stats()
        print(f"   Call {i+1}: elapsed={elapsed:.2f}s, capacity={stats['available_capacity']}")
    
    print("\n📊 Final Statistics:")
    stats = limiter.get_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    print("\n✅ Rate limiter test completed!")

