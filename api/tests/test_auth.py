from httpx import AsyncClient
import pytest

import helpers
from app.services.email_verification import _cooldown_key


REGISTER_URL = "/auth/register"
VERIFY_URL = "/auth/verify-email"
LOGIN_URL = "/auth/login"
ME_URL = "/auth/me"
RESEND_URL = "/auth/resend-verification-code"


@pytest.fixture
def user_data_factory():
  """ factory for generating unique user data """
  counter = 0

  def _counter_user_data(username_prefix="Test User"):
    nonlocal counter
    counter += 1
    return {
      "username": f"{username_prefix}{counter}",
      "email": f"test{counter}@example.com",
      "password": "password123",
    }
  
  return _counter_user_data


@pytest.mark.asyncio
async def test_register_user(client, user_data_factory):
  user_data = user_data_factory()
  response = await client.post(REGISTER_URL, json=user_data)
  
  assert response.status_code == 201
  data = response.json()
  assert data["email"] == user_data["email"]
  assert "message" in data


@pytest.mark.asyncio
async def test_register_user_duplicate_email(client: AsyncClient, user_data_factory):
  """ Test registering a user with an existing email address """

  user1_data = user_data_factory()
  await client.post(
    REGISTER_URL,
    json=user1_data
  )

  response = await client.post(
    REGISTER_URL,
    json=user1_data
  )
  assert response.status_code == 409
  assert "detail" in response.json()


@pytest.mark.asyncio
async def test_resend_verification_code_cooldown(client, redis, user_data_factory):
  user_data = user_data_factory()
  await client.post(REGISTER_URL, json=user_data)

  blocked = await client.post(RESEND_URL, json={"email": user_data["email"]})
  assert blocked.status_code == 429
  assert blocked.json()["detail"]["retry_after"] > 0
  assert "Retry-After" in blocked.headers

  await redis.delete(_cooldown_key(user_data["email"]))

  allowed = await client.post(RESEND_URL, json={"email": user_data["email"]})
  assert allowed.status_code == 200

  blocked_again = await client.post(RESEND_URL, json={"email": user_data["email"]})
  assert blocked_again.status_code == 429
  assert blocked_again.json()["detail"]["retry_after"] > 0
  assert "Retry-After" in blocked_again.headers


@pytest.mark.asyncio
async def test_login_before_verify(client, user_data_factory):
  user_data = user_data_factory()
  await client.post(REGISTER_URL, json=user_data)

  login_response = await client.post(LOGIN_URL, json={
    "email": user_data["email"],
    "password": user_data["password"],
  })
  assert login_response.status_code == 403


@pytest.mark.asyncio
async def test_verify_email(client, user_data_factory):
  user_data = user_data_factory()
  await client.post(REGISTER_URL, json=user_data)

  response = await client.post(VERIFY_URL, json={
    "email": user_data["email"],
    "code": "123456",
  })
  assert response.status_code == 200
  data = response.json()
  assert "access_token" in data
  assert data["user"]["email"] == user_data["email"]


@pytest.mark.asyncio
async def test_login_user(client: AsyncClient, user_data_factory):
  """Test successful login of a registered user."""

  user_data = user_data_factory()
  await client.post(
    REGISTER_URL,
    json = user_data,
  )
  await client.post(VERIFY_URL, json={
    "email": user_data["email"],
    "code": "123456",
  })

  login_response = await client.post(LOGIN_URL, json = {
    "email": user_data["email"],
    "password": user_data["password"],
  })
  assert login_response.status_code == 200

  data = login_response.json()
  assert "access_token" in data
  assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_user_wrong_password(client: AsyncClient, user_data_factory):
  """ Test unsuccessful login user """

  user_data = user_data_factory()
  await client.post(
    REGISTER_URL,
    json = user_data,
  )

  login_response = await client.post(LOGIN_URL, json = {
    "email": user_data["email"],
    "password": "wrongpassword",
  })
  assert login_response.status_code == 401
  assert "detail" in login_response.json()


@pytest.mark.asyncio
async def test_me_authenticated(client: AsyncClient, user_data_factory):
  """ Test  get current user profile"""

  user_data = user_data_factory()
  verify_data = await helpers.register_and_verify(client, user_data)
  token = verify_data["access_token"]

  me_response = await client.get(
    ME_URL,
    headers={"Authorization": f"Bearer {token}"},
  )
  assert me_response.status_code == 200
  assert me_response.json()["email"] == user_data["email"]


@pytest.mark.asyncio
async def test_me_without_token(client: AsyncClient):
  """ Test without a token"""
  
  response = await client.get(ME_URL)

  assert response.status_code == 401


@pytest.mark.asyncio
async def test_me_invalid_token(client: AsyncClient):
  """ Test with an invalid token"""
  response = await client.get(
    ME_URL,
    headers={"Authorization": f"Bearer (invalid)"},
  )
  assert response.status_code == 401

