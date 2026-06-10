from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI

from .config import Settings, get_settings
from .routers import auth, events


@asynccontextmanager
async def lifespan(app: FastAPI):
  yield


app = FastAPI(title="Authentication", lifespan=lifespan)
app.include_router(auth.router)
app.include_router(events.router)


@app.get("/health")
def health(settings: Settings = Depends(get_settings)):
  return {"db_host": settings.postgres_host}