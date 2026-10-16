
import json
import logging
import os
from typing import Any, Dict, Optional

import redis
from redis.exceptions import RedisError

logger = logging.getLogger(__name__)

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
DEFAULT_TTL_SECONDS = 60

redis_client = redis.Redis.from_url(
    REDIS_URL,
    decode_responses=True,
    socket_connect_timeout=2,
    socket_timeout=2,
)


def get_json(key: str) -> Optional[Dict[str, Any]]:
    try:
        cached_value = redis_client.get(key)

        if cached_value is None:
            return None

        value = json.loads(cached_value)

        if not isinstance(value, dict):
            logger.warning("Invalid cache value type for key %s", key)
            return None

        return value

    except (RedisError, json.JSONDecodeError) as error:
        logger.warning("Cache read failed for key %s: %s", key, error)
        return None


def set_json(
    key: str,
    value: Dict[str, Any],
    ttl_seconds: int = DEFAULT_TTL_SECONDS,
) -> bool:
    try:
        redis_client.set(
            name=key,
            value=json.dumps(value),
            ex=ttl_seconds,
        )
        return True

    except (RedisError, TypeError, ValueError) as error:
        logger.warning("Cache write failed for key %s: %s", key, error)
        return False


def delete_key(key: str) -> bool:
    try:
        redis_client.delete(key)
        return True

    except RedisError as error:
        logger.warning("Cache invalidation failed for key %s: %s", key, error)
        return False
