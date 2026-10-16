
import hashlib
import os

import redis
from fastapi import HTTPException, Request, status


WINDOW_SECONDS = 15 * 60
MAX_FAILED_ATTEMPTS = 5

_redis_client = None


def get_redis_client():
    global _redis_client

    if _redis_client is None:
        redis_url = os.getenv("REDIS_URL")

        if not redis_url:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Login protection is not configured",
            )

        _redis_client = redis.Redis.from_url(
            redis_url,
            decode_responses=True,
            socket_connect_timeout=2,
            socket_timeout=2,
            health_check_interval=30,
        )

    return _redis_client


def _get_keys(request: Request, username: str) -> tuple[str, str]:
    client_ip = request.client.host if request.client else "unknown"

    ip_hash = hashlib.sha256(client_ip.encode("utf-8")).hexdigest()
    username_hash = hashlib.sha256(
        username.strip().lower().encode("utf-8")
    ).hexdigest()

    return (
        f"auth:login:ip:{ip_hash}",
        f"auth:login:user:{username_hash}",
    )


def _get_counts(client, keys: tuple[str, str]) -> tuple[int, int]:
    try:
        values = client.mget(list(keys))
        return tuple(int(value or 0) for value in values)
    except (redis.RedisError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Login protection is temporarily unavailable",
        ) from None


def check_login_rate_limit(request: Request, username: str) -> None:
    client = get_redis_client()

    try:
        client.ping()
    except redis.RedisError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Login protection is temporarily unavailable",
        ) from None

    keys = _get_keys(request, username)
    counts = _get_counts(client, keys)

    if max(counts) >= MAX_FAILED_ATTEMPTS:
        try:
            ttls = [
                client.ttl(key)
                for key, count in zip(keys, counts)
                if count >= MAX_FAILED_ATTEMPTS
            ]
        except redis.RedisError:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Login protection is temporarily unavailable",
            ) from None

        retry_after = max(
            [ttl for ttl in ttls if ttl > 0],
            default=WINDOW_SECONDS,
        )

        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many failed login attempts. Try again later.",
            headers={"Retry-After": str(retry_after)},
        )


def record_failed_login(request: Request, username: str) -> None:
    client = get_redis_client()
    keys = _get_keys(request, username)

    try:
        for key in keys:
            count = client.incr(key)

            if count == 1:
                client.expire(key, WINDOW_SECONDS)
    except redis.RedisError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Login protection is temporarily unavailable",
        ) from None


def reset_login_rate_limit(request: Request, username: str) -> None:
    """Clear the username counter but preserve the IP counter."""
    client = get_redis_client()
    _, username_key = _get_keys(request, username)

    try:
        client.delete(username_key)
    except redis.RedisError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Login protection is temporarily unavailable",
        ) from None
