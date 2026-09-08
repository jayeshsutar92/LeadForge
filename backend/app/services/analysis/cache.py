import json
import logging
from typing import Any

from app.core.redis import get_redis_client

logger = logging.getLogger(__name__)

async def get_candidate_cache(platform: str, business_hash: str) -> list[dict] | None:
    redis = get_redis_client()
    key = f"candidates:{platform}:{business_hash}"
    try:
        val = await redis.get(key)
        if val:
            return json.loads(val)
    except Exception as e:
        logger.error(f"Failed to get candidate cache for {key}: {e}")
    return None

async def set_candidate_cache(platform: str, business_hash: str, candidates: list[dict], ttl_days: int = 7) -> None:
    redis = get_redis_client()
    key = f"candidates:{platform}:{business_hash}"
    try:
        # TTL of 7 to 14 days
        await redis.set(key, json.dumps(candidates), ex=86400 * ttl_days)
    except Exception as e:
        logger.error(f"Failed to set candidate cache for {key}: {e}")

