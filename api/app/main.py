from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI

from .config import Settings, get_settings
from .routers import auth, events

from .redis_client import init_redis, close_redis


@asynccontextmanager
async def lifespan(app: FastAPI):
  await init_redis()
  yield
  await close_redis()


app = FastAPI(title="Authentication", lifespan=lifespan)
app.include_router(auth.router)
app.include_router(events.router)


@app.get("/health")
def health(settings: Settings = Depends(get_settings)):
  return {"db_host": settings.postgres_host}