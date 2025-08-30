"""
Redis client configuration and initialization (Disabled for MVP)
"""

import logging
from typing import Optional
import redis.asyncio as redis

logger = logging.getLogger(__name__)

from app.core.config import get_settings

settings = get_settings()

redis_client: Optional[redis.Redis] = None


async def init_redis() -> redis.Redis:
    """Initialize Redis connection"""
    global redis_client
    try:
        redis_client = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True,
            health_check_interval=30
        )
        
        # Test connection
        await redis_client.ping()
        logger.info("Redis connection established successfully")
        return redis_client
        
    except Exception as e:
        logger.error(f"Error connecting to Redis: {e}")
        logger.warning("Redis unavailable, falling back to in-memory storage...")
        # Return None to indicate Redis is not available
        return None


async def get_redis() -> redis.Redis:
    """Get Redis client instance"""
    global redis_client
    if redis_client is None:
        await init_redis()
    return redis_client


async def close_redis() -> None:
    """Close Redis connection"""
    global redis_client
    if redis_client:
        await redis_client.close()
        logger.info("Redis connection closed")
