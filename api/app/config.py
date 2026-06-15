# Central configuration management for the API-application

from functools import lru_cache
from pathlib import Path

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILE = Path(__file__).resolve().parents[2] / ".env"

class Settings(BaseSettings):
  model_config = SettingsConfigDict(
    env_file=ENV_FILE,
    env_file_encoding="utf-8",
    extra="ignore",
    case_sensitive=False,
  )

  # --- JWT Settings ---
  secret_key: str
  algorithm: str = "HS256"
  access_token_expire_minutes: int = 30

  # --- Redis Settings ---
  redis_url: str | None = None
  redis_host: str = "localhost"
  redis_port: int = 6379
  redis_db: int = 0
  cache_ttl_seconds: int = 60

  @computed_field
  @property
  def final_redis_url(self) -> str:
    if self.redis_url:
      return self.redis_url
    return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"

  # --- PostgreSQL Settings ---
  database_url: str | None = None
  postgres_user: str = "postgres"
  postgres_password: str = ""
  postgres_host: str = "localhost"
  postgres_port: int = 5432
  postgres_db: str = "postgres"

  @computed_field
  @property
  def sqlalchemy_database_url(self) -> str:
    if self.database_url:
      return self.database_url
    return (
      f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
      f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
    )

# Caching result
@lru_cache
def get_settings() -> Settings:
  return Settings()


settings = get_settings()