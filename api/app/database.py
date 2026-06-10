# database connection module

from sqlalchemy.orm import declarative_base
from .config import settings

from sqlalchemy.ext.asyncio import (
  AsyncSession,
  async_sessionmaker,
  create_async_engine,
)

# create async engine
engine = create_async_engine(settings.sqlalchemy_database_url)

# creates a session factory
AsyncSessionLocal = async_sessionmaker(
  bind=engine,
  class_=AsyncSession,
  expire_on_commit=False,
)

# base class of models 
Base = declarative_base()

# Dependency
async def get_db():
  async with AsyncSessionLocal() as session:
    try:
      yield session
    except Exception:
      await session.rollback()
      raise
    finally:
      await session.close()