from redis.asyncio import Redis
from .config import get_settings

redis_client: Redis | None = None

async def init_redis() -> Redis:
  global redis_client
  settings = get_settings()
  redis_client = Redis.from_url(
    settings.final_redis_url,
    encoding="utf-8",
    decode_responses=True,
  )
  return redis_client

async def close_redis():
  global redis_client
  if redis_client is not None:
    await redis_client.aclose()
    redis_client = None

def get_redis() -> Redis:
  if redis_client is None:
    raise RuntimeError("Redis is not initialized")
  return redis_client