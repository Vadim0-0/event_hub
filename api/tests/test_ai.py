import uuid
from unittest.mock import AsyncMock, patch
from datetime import datetime, timezone

import pytest
import helpers
from httpx import ASGITransport, AsyncClient

from app.main import app


class FakeMsg:
  def __init__(self):
    self.id = uuid.uuid4()
    self.role = "user"
    self.content = "Hello"
    self.created_at = datetime.now(timezone.utc)


@pytest.mark.asyncio
async def test_ai_health_disabled(client: AsyncClient, user_data_factory):
  user_data = user_data_factory()
  auth = await helpers.register_and_verify(client, user_data)
  headers = {"Authorization": f"Bearer {auth['access_token']}"}

  with patch("app.config.settings.ai_enabled", False):
    response = await client.get("/ai/health", headers=headers)
  assert response.status_code == 200
  data = response.json()
  assert data["enabled"] is False
  assert data["available"] is False


@pytest.mark.asyncio
async def test_ai_chat_success(client: AsyncClient, user_data_factory):
  user_data = user_data_factory()
  auth = await helpers.register_and_verify(client, user_data)
  headers = {"Authorization": f"Bearer {auth['access_token']}"}

  with (
    patch("app.config.settings.ai_enabled", True),
    patch(
      "app.routers.ai.ai_service.chat_with_memory",
      new=AsyncMock(return_value=(
        "Hello! How can I help you?",
        "qwen2.5:3b",
        FakeMsg(),
        FakeMsg(),
        None,
        False,
      )),
    ),
  ):
    response = await client.post(
      "/ai/chat",
      headers=headers,
      json={"message": "Hello!"},
    )

  assert response.status_code == 200
  data = response.json()
  assert data["reply"] == "Hello! How can I help you?"
  assert data["model"] == "qwen2.5:3b"


@pytest.mark.asyncio
async def test_ai_chat_requires_auth():
  transport = ASGITransport(app=app)
  async with AsyncClient(transport=transport, base_url="http://test") as client:
    response = await client.post("/ai/chat", json={"message": "Hello"})
  assert response.status_code == 401