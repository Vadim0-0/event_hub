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
  )

  # JWT
  secret_key: str
  algorithm: str = "HS256"
  access_token_expire_minutes: int = 30

  # Postgres — either a ready URL or parts
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