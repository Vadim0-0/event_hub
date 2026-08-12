from uuid import UUID
from redis.asyncio import Redis

from ...cache import cache_delete, cache_delete_pattern


async def invalidate_user_conversations(redis: Redis, user_id: int) -> None:
  await cache_delete_pattern(redis, f"conversations:list:user={user_id}:*")


async def invalidate_user_unread_count(redis: Redis, user_id: int) -> None:
  await cache_delete(redis, f"conversations:unread:user={user_id}")


async def invalidate_conversation_detail(
  redis: Redis,
  conversation_id: UUID,
  user_id: int,
) -> None:
  await cache_delete(
    redis,
    f"conversations:detail:user={user_id}:id={conversation_id}",
  )


async def invalidate_conversation_messages(redis: Redis, conversation_id: UUID) -> None:
  await cache_delete_pattern(
    redis,
    f"conversations:{conversation_id}:messages:*",
  )


async def invalidate_for_both_participants(
  redis: Redis,
  user1_id: int,
  user2_id: int,
  conversation_id: UUID | None = None,
) -> None:
  for user_id in (user1_id, user2_id):
    await invalidate_user_conversations(redis, user_id)
    await invalidate_user_unread_count(redis, user_id)
    if conversation_id is not None:
      await invalidate_conversation_detail(redis, conversation_id, user_id)

  if conversation_id is not None:
    await invalidate_conversation_messages(redis, conversation_id)