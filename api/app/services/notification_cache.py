from redis.asyncio import Redis

from ..cache import cache_delete_pattern


async def invalidate_user_notifications(redis: Redis, user_id: int) -> None:
  await cache_delete_pattern(redis, f"notifications:my:user={user_id}:*")