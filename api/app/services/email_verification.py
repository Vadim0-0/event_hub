import secrets
import hashlib
from redis.asyncio import Redis

from ..config import settings


class ResendTooSoonError(Exception):
  def __init__(self, retry_after: int):
    self.retry_after = retry_after
    super().__init__(f"Please wait {retry_after} seconds before requesting a new code")


def _email_hash(email: str) -> str:
  return hashlib.sha256(email.lower().encode()).hexdigest()


def _code_key(email: str) -> str:
  email_hash = hashlib.sha256(email.lower().encode()).hexdigest()
  return f"verify:code:{email_hash}"


def _cooldown_key(email: str) -> str:
  return f"verify:cooldown:{_email_hash(email)}"


def generate_verification_code() -> str:
  return "".join(str(secrets.randbelow(10)) for _ in range(settings.email_verification_code_length))


async def store_verification_code(redis: Redis, email: str, code: str) -> None:
  await redis.setex(
    _code_key(email),
    settings.email_verification_code_ttl_seconds,
    code,
  )


async def set_resend_cooldown(redis: Redis, email: str) -> None:
  await redis.setex(
    _cooldown_key(email),
    settings.email_verification_resend_cooldown_seconds,
    "1",
  )


async def get_resend_cooldown_ttl(redis: Redis, email: str) -> int:
  ttl = await redis.ttl(_cooldown_key(email))
  return max(ttl, 0)


async def issue_verification_code(redis: Redis, email: str) -> str:
  ttl = await get_resend_cooldown_ttl(redis, email)
  if ttl > 0:
    raise ResendTooSoonError(retry_after=ttl)

  code = generate_verification_code()
  await store_verification_code(redis, email, code)
  await set_resend_cooldown(redis, email)
  return code


async def verify_and_consume_code(redis: Redis, email: str, code: str) -> bool:
  key = _code_key(email)
  stored = await redis.getdel(key)
  if stored is None or stored != code:
    return False
  return True