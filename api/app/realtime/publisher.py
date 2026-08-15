import json
from redis.asyncio import Redis


def user_channel(user_id: int) -> str:
  return f"realtime:user:{user_id}"


async def publish_to_user(redis: Redis, user_id: int, event: dict) -> None:
  await redis.publish(user_channel(user_id), json.dumps(event))