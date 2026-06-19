from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI

from .config import Settings, get_settings
from .routers import auth, events, notifications

from .redis_client import init_redis, close_redis
from .worker.enqueue import init_arq_pool, close_arq_pool

@asynccontextmanager
async def lifespan(app: FastAPI):
  await init_redis()
  await init_arq_pool()
  yield
  await close_arq_pool()
  await close_redis()


app = FastAPI(title="Authentication", lifespan=lifespan)
app.include_router(auth.router)
app.include_router(events.router)
app.include_router(notifications.router)


@app.get("/health")
def health(settings: Settings = Depends(get_settings)):
  return {"db_host": settings.postgres_host}