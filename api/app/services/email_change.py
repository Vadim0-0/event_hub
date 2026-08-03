import hashlib
import hmac
from redis.asyncio import Redis

from ..config import settings
from .email_verification import ResendTooSoonError, generate_verification_code 

def _target_key(user_id: int) -> str:
  return f"email_change:target:user={user_id}"


def _code_key(user_id: int) -> str:
  return f"email_change:code:user={user_id}"


def _cooldown_key(user_id: int) -> str:
  return f"email_change:cooldown:user={user_id}"


async def store_email_change_request(
  redis: Redis,
  user_id: int,
  new_email: str,
  code: str,
) -> None:
  ttl = settings.email_verification_code_ttl_seconds

  await redis.setex(_target_key(user_id), ttl, new_email.lower())

  await redis.setex(_code_key(user_id), ttl, code)

  await redis.setex(
    _cooldown_key(user_id),
    settings.email_verification_resend_cooldown_seconds,
    "1",
  )


async def get_cooldown_ttl(redis: Redis, user_id: int) -> int:
  ttl = await redis.ttl(_cooldown_key(user_id))
  return max(ttl, 0)


async def verify_and_consume(
  redis: Redis,
  user_id: int,
  code: str,
) -> str | None:
  stored_code = await redis.get(_code_key(user_id))
  new_email = await redis.get(_target_key(user_id))
  
  if stored_code is None or new_email is None:
    return None 
  
  if not hmac.compare_digest(stored_code, code):
    return None

  await redis.delete(_code_key(user_id))
  await redis.delete(_target_key(user_id))
  await redis.delete(_cooldown_key(user_id))
  
  return new_email


async def issue_email_change_code(
  redis: Redis,
  user_id: int,
  new_email: str,
) -> str:
  ttl = await get_cooldown_ttl(redis, user_id)
  if ttl > 0:
    raise ResendTooSoonError(retry_after=ttl)
  
  code = generate_verification_code()
  await store_email_change_request(redis, user_id, new_email, code)
  return code