from httpx import AsyncClient
import pytest


REGISTER_URL = "/auth/register"
LOGIN_URL = "/auth/login"
ME_URL = "/auth/me"

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
async def test_register_user(client: AsyncClient, user_data_factory):
  """ Test register user """

  user_data = user_data_factory()
  response = await client.post(
    REGISTER_URL,
    json = user_data,
  )
  assert response.status_code == 201
  response_data = response.json()

  assert "id" in response_data
  assert response_data["username"] == user_data["username"]
  assert response_data["email"] == user_data["email"]


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
  assert response.status_code == 400
  assert "detail" in response.json()


@pytest.mark.asyncio
async def test_login_user(client: AsyncClient, user_data_factory):
  """Test successful login of a registered user."""

  user_data = user_data_factory()
  await client.post(
    REGISTER_URL,
    json = user_data,
  )

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
  await client.post(
    REGISTER_URL,
    json = user_data,
  )

  login_response = await client.post(LOGIN_URL, json = {
    "email": user_data["email"],
    "password": user_data["password"],
  })
  assert login_response.status_code == 200
  token = login_response.json()["access_token"]

  me_response = await client.get(ME_URL, headers={"Authorization": f"Bearer {token}"})
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