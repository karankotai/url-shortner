import redis
from fastapi import HTTPException, Request

redis_client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

RATE_LIMIT = 10
WINDOW_SECONDS = 60

def rate_limit_check(request: Request) -> None:
    # Get the client's IP address from the request
    client_ip = request.client.host
    key = f"rate_limit:{client_ip}"

    # Check if this IP has already hit the limit
    current_count = redis_client.get(key)
    
    if current_count is not None and int(current_count) >= RATE_LIMIT:
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Please try again later.",
        )
    
    # Increment the counter and set expiry automatically using a pipeline
    pipe = redis_client.pipeline()
    pipe.incr(key)
    pipe.expire(key, WINDOW_SECONDS)
    pipe.execute()
