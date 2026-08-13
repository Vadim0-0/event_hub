import pytest
import helpers


CONVERSATIONS_URL = "/conversations/"


def get_auth_headers(token: str) -> dict:
  return {"Authorization": f"Bearer {token}"}


async def two_verified_users(client, user_data_factory):
  user1 = user_data_factory()
  user2 = user_data_factory()

  auth1 = await helpers.register_and_verify(client, user1)
  auth2 = await helpers.register_and_verify(client, user2)

  return user1, auth1, user2, auth2


@pytest.mark.asyncio
async def test_list_conversations_empty(client, user_data_factory):
  user_data = user_data_factory()
  auth = await helpers.register_and_verify(client, user_data)

  response = await client.get(CONVERSATIONS_URL, headers = get_auth_headers(auth["access_token"]),)
  
  assert response.status_code == 200
  assert response.json() == {"items": [], "total": 0}


@pytest.mark.asyncio
async def test_list_conversations_unauthorized(client):
  response = await client.get(CONVERSATIONS_URL)
  assert response.status_code == 401


@pytest.mark.asyncio
async def test_start_conversation(client, user_data_factory):
  _, auth1, user2, auth2 = await two_verified_users(client, user_data_factory)
  recipient_id = auth2["user"]["id"]

  response = await client.post(
    CONVERSATIONS_URL,
    json={"recipient_id": recipient_id},
    headers = get_auth_headers(auth1["access_token"]),
  )

  assert response.status_code == 201
  data = response.json()
  assert data["participant"]["id"] == recipient_id
  assert data["last_message"] is None
  assert data["unread_count"] == 0


@pytest.mark.asyncio
async def test_start_conversation_with_self(client, user_data_factory):
  user_data = user_data_factory()
  auth = await helpers.register_and_verify(client, user_data)
  my_id = auth["user"]["id"]

  response = await client.post(
    CONVERSATIONS_URL,
    json={"recipient_id": my_id},
    headers=get_auth_headers(auth["access_token"]),
  )
  assert response.status_code == 400
  assert response.json()["detail"]["field"] == "recipient_id"


@pytest.mark.asyncio
async def test_start_conversation_recipient_not_found(client, user_data_factory):
  user_data = user_data_factory()
  auth = await helpers.register_and_verify(client, user_data)

  response = await client.post(
    CONVERSATIONS_URL,
    json={"recipient_id": 99999},
    headers=get_auth_headers(auth["access_token"]),
  )
  assert response.status_code == 404


@pytest.mark.asyncio
async def test_start_conversation_idempotent(client, user_data_factory):
  _, auth1, _, auth2 = await two_verified_users(client, user_data_factory)
  recipient_id = auth2["user"]["id"]
  headers = get_auth_headers(auth1["access_token"])

  first = await client.post(CONVERSATIONS_URL, json={"recipient_id": recipient_id}, headers=headers)
  second = await client.post(CONVERSATIONS_URL, json={"recipient_id": recipient_id}, headers=headers)

  assert first.status_code == 201
  assert second.status_code == 201
  assert first.json()["id"] == second.json()["id"]


@pytest.mark.asyncio
async def test_send_and_list_messages(client, user_data_factory):
  _, auth1, _, auth2 = await two_verified_users(client, user_data_factory)
  headers1 = get_auth_headers(auth1["access_token"])
  headers2 = get_auth_headers(auth2["access_token"])

  conv = await client.post(
    CONVERSATIONS_URL,
    json={"recipient_id": auth2["user"]["id"]},
    headers=headers1,
  )
  conversation_id = conv.json()["id"]

  sent = await client.post(
    f"{CONVERSATIONS_URL}{conversation_id}/messages",
    json={"body": "Hello!"},
    headers=headers1,
  )
  assert sent.status_code == 201
  assert sent.json()["body"] == "Hello!"

  messages = await client.get(
    f"{CONVERSATIONS_URL}{conversation_id}/messages",
    headers=headers2,
  )
  assert messages.status_code == 200
  assert len(messages.json()) == 1
  assert messages.json()[0]["body"] == "Hello!"


@pytest.mark.asyncio
async def test_unread_count_after_message(client, user_data_factory):
  _, auth1, _, auth2 = await two_verified_users(client, user_data_factory)
  headers1 = get_auth_headers(auth1["access_token"])
  headers2 = get_auth_headers(auth2["access_token"])

  conv = await client.post(
    CONVERSATIONS_URL,
    json={"recipient_id": auth2["user"]["id"]},
    headers=headers1,
  )
  conversation_id = conv.json()["id"]

  await client.post(
    f"{CONVERSATIONS_URL}{conversation_id}/messages",
    json={"body": "Ping"},
    headers=headers1,
  )

  unread = await client.get(
    f"{CONVERSATIONS_URL}unread-count", 
    headers=headers2
  )
  assert unread.status_code == 200
  assert unread.json()["total"] >= 1


@pytest.mark.asyncio
async def test_mark_read_clears_unread(client, user_data_factory):
  _, auth1, _, auth2 = await two_verified_users(client, user_data_factory)
  headers1 = get_auth_headers(auth1["access_token"])
  headers2 = get_auth_headers(auth2["access_token"])

  conv = await client.post(
    CONVERSATIONS_URL,
    json={"recipient_id": auth2["user"]["id"]},
    headers=headers1,
  )
  conversation_id = conv.json()["id"]

  await client.post(
    f"{CONVERSATIONS_URL}{conversation_id}/messages",
    json={"body": "Ping"},
    headers=headers1,
  )
  
  read = await client.post(
    f"{CONVERSATIONS_URL}{conversation_id}/read",
    headers=headers2,
  )
  assert read.status_code == 204

  detail = await client.get(
    f"{CONVERSATIONS_URL}{conversation_id}",
    headers=headers2,
  )
  assert detail.json()["unread_count"] == 0


@pytest.mark.asyncio
async def test_cannot_access_foreign_conversation(client, user_data_factory):
  user1, auth1, _, auth2 = await two_verified_users(client, user_data_factory)
  user3_data = user_data_factory()
  auth3 = await helpers.register_and_verify(client, user3_data)

  conv = await client.post(
    CONVERSATIONS_URL,
    json={"recipient_id": auth2["user"]["id"]},
    headers=get_auth_headers(auth1["access_token"]),
  )
  conversation_id = conv.json()["id"]
  
  response = await client.get(
    f"{CONVERSATIONS_URL}{conversation_id}",
    headers=get_auth_headers(auth3["access_token"]),
  )
  assert response.status_code == 403