from arq import create_pool
from arq.connections import RedisSettings

from app.config import settings

_arq_pool = None


async def init_arq_pool():
  global _arq_pool
  _arq_pool = await create_pool(RedisSettings.from_dsn(settings.arq_redis_url))


async def close_arq_pool():
  global _arq_pool
  if _arq_pool is not None:
    await _arq_pool.close()
    _arq_pool = None


async def enqueue_job(function_name: str, *args, **kwargs):
  if _arq_pool is None:
    raise RuntimeError("ARQ pool is not initialized")
  return await _arq_pool.enqueue_job(function_name, *args, **kwargs)