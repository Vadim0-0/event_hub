from arq import create_pool
from arq.connections import RedisSettings

from app.config import settings

_arq_pool = None


def arq_redis_settings() -> RedisSettings:
  password = settings.redis_password or None
  return RedisSettings(
    host=settings.redis_host,
    port=settings.redis_port,
    database=settings.arq_redis_db,
    username="default" if password else None,
    password=password,
  )


async def init_arq_pool():
  global _arq_pool
  _arq_pool = await create_pool(arq_redis_settings())


async def close_arq_pool():
  global _arq_pool
  if _arq_pool is not None:
    await _arq_pool.close()
    _arq_pool = None


async def enqueue_job(function_name: str, *args, **kwargs):
  if _arq_pool is None:
    raise RuntimeError("ARQ pool is not initialized")
  return await _arq_pool.enqueue_job(function_name, *args, **kwargs)