import json
from redis.asyncio import Redis


async def cache_get(redis: Redis, key: str):
  data = await redis.get(key)
  return json.loads(data) if data else None


async def cache_set(redis: Redis, key: str, value, ttl: int):
  await redis.set(key, json.dumps(value, default=str), ex=ttl)


async def cache_delete(redis: Redis, key: str):
  await redis.delete(key)


async def cache_delete_pattern(redis: Redis, pattern: str) -> None:
  async for key in redis.scan_iter(match=pattern):
    await redis.delete(key)