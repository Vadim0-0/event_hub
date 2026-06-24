from dotenv import load_dotenv
from pathlib import Path
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine  
from fakeredis.aioredis import FakeRedis
from unittest.mock import AsyncMock, patch

load_dotenv(Path(__file__).parent / ".env.test", override=True)

from app.config import get_settings
from app.database import Base, get_db
from app.main import app

get_settings.cache_clear()

from app.models.user import User # noqa: F401
from app.models.event import Event # noqa: F401
from app.models.registration import EventRegistration # noqa: F401
from app.redis_client import get_redis

settings = get_settings()
TEST_DATABASE_URL = settings.sqlalchemy_database_url


@pytest_asyncio.fixture(scope="function")
async def db_engine():
  """ Creates an engine and tables for each test """
  engine = create_async_engine(TEST_DATABASE_URL, echo=False) 
  
  async with engine.begin() as conn:
    await conn.run_sync(Base.metadata.create_all)
  
  yield engine
  
  async with engine.begin() as conn:
    await conn.run_sync(Base.metadata.drop_all)
  
  await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(db_engine):
  """ Creates a new session for each test """
  session_factory = async_sessionmaker(
    bind=db_engine,
    class_=AsyncSession,
    expire_on_commit=False,
  )
  
  async with session_factory() as session:
    yield session
    await session.rollback()


@pytest_asyncio.fixture(scope="function")
async def client(db_session):
  """ HTTP client with overridden database """
  fake_redis = FakeRedis(decode_responses=True)
  
  async def override_get_db():
    yield db_session

  app.dependency_overrides[get_db] = override_get_db
  app.dependency_overrides[get_redis] = lambda: fake_redis

  mock_enqueue = AsyncMock(return_value=None)
  with (
    patch("app.routers.events.enqueue_job", mock_enqueue),
    patch("app.routers.auth.enqueue_job", mock_enqueue),
  ):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
      yield ac
  
  app.dependency_overrides.clear()
  await fake_redis.aclose()