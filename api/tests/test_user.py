import pytest

import helpers

from app.services.email_change import _cooldown_key


UPDATE_ME_URL = "/users/me"
CHANGE_PASSWORD_URL = "/users/me/password"
EMAIL_CHANGE_REQUEST_URL = "/users/me/email-change/request"
EMAIL_CHANGE_CONFIRM_URL = "/users/me/email-change/confirm"


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
async def test_update_username(client, user_data_factory):
  user_data = user_data_factory()
  auth = await helpers.register_and_verify(client, user_data)
  token = auth["access_token"]

  response = await client.patch(
    UPDATE_ME_URL,
    json={"username": "Updated Name"},
    headers={"Authorization": f"Bearer {token}"},
  )

  assert response.status_code == 200
  assert response.json()["username"] == "Updated Name"
  assert response.json()["email"] == user_data["email"]


@pytest.mark.asyncio
async def test_update_username_already_taken(client, user_data_factory):
  user1 = user_data_factory()
  user2 = user_data_factory()

  await helpers.register_and_verify(client, user1)
  auth2 = await helpers.register_and_verify(client, user2)
  token2 = auth2["access_token"]

  response = await client.patch(
    UPDATE_ME_URL,
    json={"username": user1["username"]},
    headers={"Authorization": f"Bearer {token2}"},
  )

  assert response.status_code == 409
  assert response.json()["detail"]["field"] == "username"


@pytest.mark.asyncio
async def test_update_username_unauthorized(client):
  response = await client.patch(UPDATE_ME_URL, json={"username": "Hack"})
  assert response.status_code == 401


@pytest.mark.asyncio
async def test_change_password_success(client, user_data_factory):
  user_data = user_data_factory()
  auth = await helpers.register_and_verify(client, user_data)
  token = auth["access_token"]

  response = await client.patch(
    CHANGE_PASSWORD_URL,
    json={
      "current_password": user_data["password"],
      "new_password": "newpassword123",
    },
    headers={"Authorization": f"Bearer {token}"},
  )
  assert response.status_code == 204

  login = await client.post("/auth/login", json={
    "email": user_data["email"],
    "password": "newpassword123",
  })
  assert login.status_code == 200


@pytest.mark.asyncio
async def test_change_password_wrong_current(client, user_data_factory):
  user_data = user_data_factory()
  auth = await helpers.register_and_verify(client, user_data)
  token = auth["access_token"]

  response = await client.patch(
    CHANGE_PASSWORD_URL,
    json={"current_password": "wrong", "new_password": "newpass123"},
    headers={"Authorization": f"Bearer {token}"},
  )
  assert response.status_code == 400


@pytest.mark.asyncio
async def test_change_password_same_as_current(client, user_data_factory):
  user_data = user_data_factory()
  auth = await helpers.register_and_verify(client, user_data)
  token = auth["access_token"]

  response = await client.patch(
    CHANGE_PASSWORD_URL,
    json={
      "current_password": user_data["password"],
      "new_password": user_data["password"],
    },
    headers={"Authorization": f"Bearer {token}"},
  )
  assert response.status_code == 400


@pytest.mark.asyncio
async def test_request_email_change(client, user_data_factory):
  user_data = user_data_factory()
  auth = await helpers.register_and_verify(client, user_data)
  token = auth["access_token"]
  new_email = 'testNewEmail@gmail.com'

  response = await client.post(
    EMAIL_CHANGE_REQUEST_URL,
    json={
      "new_email": new_email
    },
    headers={"Authorization": f"Bearer {token}"},
  )

  assert response.status_code == 200
  data = response.json()
  assert data["new_email"] == new_email
  assert "message" in data


@pytest.mark.asyncio
async def test_request_same_email(client, user_data_factory):
  user_data = user_data_factory()
  auth = await helpers.register_and_verify(client, user_data)
  token = auth["access_token"]

  response = await client.post(
    EMAIL_CHANGE_REQUEST_URL,
    json={
      "new_email": user_data["email"]
    },
    headers={"Authorization": f"Bearer {token}"},
  )

  assert response.status_code == 400


@pytest.mark.asyncio
async def test_request_email_change_cooldown(client, redis, user_data_factory):
  user_data = user_data_factory()
  auth = await helpers.register_and_verify(client, user_data)
  token = auth["access_token"]
  user_id = auth["user"]["id"]

  response_first = await client.post(
    EMAIL_CHANGE_REQUEST_URL,
    json={
      "new_email": "first@gmail.com",
    },
    headers={"Authorization": f"Bearer {token}"},
  )
  assert response_first.status_code == 200

  response_second = await client.post(
    EMAIL_CHANGE_REQUEST_URL,
    json={
      "new_email": "second@gmail.com",
    },
    headers={"Authorization": f"Bearer {token}"},
  )
  assert response_second.status_code == 429
  assert response_second.json()["detail"]["retry_after"] > 0

  await redis.delete(_cooldown_key(user_id))


@pytest.mark.asyncio
async def test_confirm_email_change(client, user_data_factory):
  user_data = user_data_factory()
  auth = await helpers.register_and_verify(client, user_data)
  token = auth["access_token"]
  new_email = 'testNewEmail@gmail.com'

  request = await client.post(
    EMAIL_CHANGE_REQUEST_URL,
    json={
      "new_email": new_email
    },
    headers={"Authorization": f"Bearer {token}"},
  )
  assert request.status_code == 200

  confirm = await client.post(
    EMAIL_CHANGE_CONFIRM_URL,
    json={"token": "123456"},
    headers={"Authorization": f"Bearer {token}"},
  )

  assert confirm.status_code == 200
  assert confirm.json()["email"] == new_email.lower()


@pytest.mark.asyncio
async def test_confirm_email_change_invalid_code(client, user_data_factory):
  user_data = user_data_factory()
  auth = await helpers.register_and_verify(client, user_data)
  token = auth["access_token"]

  await client.post(
    EMAIL_CHANGE_REQUEST_URL,
    json={"new_email": "other@example.com"},
    headers={"Authorization": f"Bearer {token}"},
  )

  response = await client.post(
    EMAIL_CHANGE_CONFIRM_URL,
    json={"token": "000000"},
    headers={"Authorization": f"Bearer {token}"},
  )
  assert response.status_code == 400