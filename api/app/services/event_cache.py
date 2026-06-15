from redis.asyncio import Redis
from ..cache import cache_delete, cache_delete_pattern


async def invalidate_event_detail(redis: Redis, event_id: int) -> None:
  await cache_delete(redis, f"event:{event_id}")


async def invalidate_event_lists(redis: Redis, user_id: int | None = None) -> None:
  await cache_delete_pattern(redis, "events:list:*")
  if user_id is not None:
    await cache_delete_pattern(redis, f"events:my:user={user_id}:*")


async def invalidate_event_participants(redis: Redis, event_id: int) -> None:
  await cache_delete_pattern(redis, f"event:{event_id}:participants:*")


async def invalidate_event_completely(redis: Redis, event_id: int, user_id: int) -> None:
  await invalidate_event_detail(redis, event_id)
  await invalidate_event_lists(redis, user_id)
  await invalidate_event_participants(redis, event_id)