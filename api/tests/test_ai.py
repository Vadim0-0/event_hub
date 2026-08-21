from unittest.mock import AsyncMock, patch

import pytest
import helpers
from httpx import ASGITransport, AsyncClient

from app.main import app


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
      "app.routers.ai.ai_service.chat",
      new=AsyncMock(return_value=("Привет! Чем могу помочь?", "llama3.2:3b")),
    )
  ):
    response = await client.post(
      "/ai/chat",
      headers=headers,
      json={"message": "Привет"},
    )

  assert response.status_code == 200
  data = response.json()
  assert data["reply"] == "Привет! Чем могу помочь?"
  assert data["model"] == "llama3.2:3b"


@pytest.mark.asyncio
async def test_ai_chat_requires_auth():
  transport = ASGITransport(app=app)
  async with AsyncClient(transport=transport, base_url="http://test") as client:
    response = await client.post("/ai/chat", json={"message": "Hello"})
  assert response.status_code == 401