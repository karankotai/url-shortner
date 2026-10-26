import redis

redis_client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

CACHE_TTL = 3600

def get_cached_url(short_code: str) -> str | None:
    return redis_client.get(f"url:{short_code}")

def set_cached_url(short_code: str, original_url: str) -> None:
    redis_client.set(f"url:{short_code}", original_url, ex=CACHE_TTL)
