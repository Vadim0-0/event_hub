from httpx import AsyncClient
import pytest
import pytest_asyncio
from datetime import datetime, timedelta, timezone

EVENTS_URL = "/events/"
GET_USER_EVENTS_URL = "/events/my"

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


@pytest.fixture
def event_data_factory():
  """ factory for generating unique event data """
  counter = 0

  def _counter_event_data(title_prefix="Test Event", days_ahead=1, max_participants=10):
    nonlocal counter
    counter += 1
    return {
      "title": f"{title_prefix}{counter}",
      "description": f"about the event{counter}",
      "starts_at": (datetime.now(timezone.utc) + timedelta(days=days_ahead)).isoformat(),
      "max_participants": max_participants,
    }

  return _counter_event_data


async def register_user(client: AsyncClient, user_data: dict) -> dict:
  """ Register user """
  response = await client.post(
    "/auth/register",
    json=user_data,
  )

  assert response.status_code == 201
  return response.json()


async def login_user(client, email: str, password: str) -> dict:
  response = await client.post(
    "/auth/login",
    json={
      "email": email,
      "password": password,
    }
  )
  assert response.status_code == 200

  token = response.json()["access_token"]
  return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_creating_event(client: AsyncClient, user_data_factory, event_data_factory):
  """ Creating event """
  user_data = user_data_factory()
  await register_user(client, user_data)

  user_headers = await login_user(
    client, 
    email = user_data["email"],
    password =  user_data["password"]
  )

  event_data = event_data_factory()

  response = await client.post(
    EVENTS_URL,
    json = event_data,
    headers=user_headers
  )

  assert response.status_code == 201
  created_event = response.json()

  assert "id" in created_event
  assert created_event["title"] == event_data["title"]
  assert created_event["creator_id"] == 1


@pytest.mark.asyncio
async def test_get_user_events(client: AsyncClient, user_data_factory, event_data_factory):
  """ Get User Events """
  user_data = user_data_factory()
  await register_user(client, user_data)

  user_headers = await login_user(
    client, 
    email = user_data["email"],
    password =  user_data["password"]
  )

  event1_data = event_data_factory()
  event2_data = event_data_factory()

  await client.post(
    EVENTS_URL,
    json = event1_data,
    headers=user_headers
  )
  await client.post(
    EVENTS_URL,
    json = event2_data,
    headers=user_headers
  )

  response = await client.get(GET_USER_EVENTS_URL, headers=user_headers)
  assert response.status_code == 200

  events_data = response.json()
  assert len(events_data) == 2

  assert events_data[0]["title"] == event1_data["title"]
  assert events_data[1]["title"] == event2_data["title"]


@pytest.mark.asyncio
async def test_get_user_events_not_authenticated(client: AsyncClient):
  """ Test access to events without authorization """

  response = await client.get(GET_USER_EVENTS_URL, headers={"Authorization": f"Bearer (none)"})
  assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_all_events(client: AsyncClient, user_data_factory, event_data_factory):
  """ Test for receiving all events """
  creator1_data = user_data_factory()
  creator2_data = user_data_factory()
  await register_user(client, creator1_data)
  await register_user(client, creator2_data)

  creator1_headers = await login_user(
    client, 
    email = creator1_data["email"],
    password =  creator1_data["password"]
  )
  creator2_headers = await login_user(
    client, 
    email = creator2_data["email"],
    password =  creator2_data["password"]
  )

  event1_data = event_data_factory()
  event2_data = event_data_factory()

  await client.post(
    EVENTS_URL,
    json = event1_data,
    headers=creator1_headers
  )
  await client.post(
    EVENTS_URL,
    json = event2_data,
    headers=creator2_headers
  )

  response = await client.get(EVENTS_URL)
  assert response.status_code == 200

  events_data = response.json()
  assert len(events_data) == 2

  assert events_data[0]["title"] == event1_data["title"]
  assert events_data[1]["title"] == event2_data["title"]


@pytest.mark.asyncio
async def test_join_event(client: AsyncClient, user_data_factory, event_data_factory):
  """ Test event registration """
  creator_data = user_data_factory()
  await register_user(client, creator_data)

  creator_headers = await login_user(
    client, 
    email = creator_data["email"],
    password =  creator_data["password"]
  )

  user_data = user_data_factory()
  await register_user(client, user_data)

  user_headers = await login_user(
    client,
    email = user_data["email"],
    password =  user_data["password"]
  )

  event_data = event_data_factory()

  create_event = await client.post(
    EVENTS_URL,
    json=event_data,
    headers=creator_headers,
  )
  event_id = create_event.json()["id"]

  response = await client.post(
    f"/events/{event_id}/join",
    headers=user_headers,
  )
  assert response.status_code == 201

  response_data = response.json()
  assert response_data["event_id"] == event_id
  assert response_data["user_id"] == 2


@pytest.mark.asyncio
async def test_join_event_when_full(client: AsyncClient, user_data_factory, event_data_factory):
  """ Test registration for a completed event """

  creator_data = user_data_factory()
  await register_user(client, creator_data)

  creator_headers = await login_user(
    client, 
    email = creator_data["email"],
    password =  creator_data["password"]
  )

  event_data = event_data_factory(max_participants=2)

  create_event = await client.post(
    EVENTS_URL,
    json=event_data,
    headers=creator_headers,
  )
  event_id = create_event.json()["id"]

  for _ in range(1, event_data["max_participants"] + 1):
    participant_data = user_data_factory()
    await register_user(
      client,
      participant_data
    )
    participant_headers = await login_user(
      client,
      email=participant_data["email"],
      password=participant_data["password"]
    )
    await client.post(
      f"/events/{event_id}/join",
      headers=participant_headers,
    )

  extra_user_data = user_data_factory()
  await register_user(
    client,
    user_data=extra_user_data
  )
  extra_user_headers = await login_user(
    client,
    email=extra_user_data["email"],
    password=extra_user_data["password"]
  )

  response = await client.post(
    f"/events/{event_id}/join",
    headers=extra_user_headers,
  )
  response.status_code == 409


@pytest.mark.asyncio
async def test_creator_cannot_join_own_event(client: AsyncClient, user_data_factory, event_data_factory):
  """ Test, creator cannot register for his event """

  creator_data = user_data_factory()
  await register_user(client, creator_data)

  creator_headers = await login_user(
    client, 
    email = creator_data["email"],
    password =  creator_data["password"]
  )

  event_data = event_data_factory()

  create_event = await client.post(
    EVENTS_URL,
    json=event_data,
    headers=creator_headers,
  )
  event_id = create_event.json()["id"]

  response = await client.post(
    f"/events/{event_id}/join",
    headers=creator_headers,
  )
  assert response.status_code == 409


@pytest.mark.asyncio
async def test_join_same_event(client: AsyncClient, user_data_factory, event_data_factory):
  """ Test re-registration for the same event """
  creator_data = user_data_factory()
  await register_user(client, creator_data)

  creator_headers = await login_user(
    client, 
    email = creator_data["email"],
    password =  creator_data["password"]
  )

  user_data = user_data_factory()
  await register_user(client, user_data)

  user_headers = await login_user(
    client,
    email = user_data["email"],
    password =  user_data["password"]
  )

  event_data = event_data_factory()

  create_event = await client.post(
    EVENTS_URL,
    json=event_data,
    headers=creator_headers,
  )
  event_id = create_event.json()["id"]

  response = await client.post(
    f"/events/{event_id}/join",
    headers=user_headers,
  )
  assert response.status_code == 201

  re_response = await client.post(
    f"/events/{event_id}/join",
    headers=user_headers,
  )
  assert re_response.status_code == 409


@pytest.mark.asyncio
async def test_join_nonexistent_event(client: AsyncClient, user_data_factory):
  """ Test registration for non-existent events """

  user_data = user_data_factory()
  await register_user(client, user_data)

  user_headers = await login_user(
    client,
    email = user_data["email"],
    password =  user_data["password"]
  )

  response = await client.post(
    "/events/9999/join",
    headers=user_headers,
  )
  assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_participants(client: AsyncClient, user_data_factory, event_data_factory):
  """ Test getting a list of participants """

  creator_data = user_data_factory()
  await register_user(client, creator_data)

  creator_headers = await login_user(
    client, 
    email = creator_data["email"],
    password =  creator_data["password"]
  )

  participant1_data = user_data_factory()
  participant2_data = user_data_factory()

  await register_user(client, participant1_data)
  await register_user(client, participant2_data)

  participant1_headers = await login_user(
    client, 
    email = participant1_data["email"],
    password =  participant1_data["password"]
  )
  participant2_headers = await login_user(
    client, 
    email = participant2_data["email"],
    password =  participant2_data["password"]
  )

  event_data = event_data_factory()

  create_event = await client.post(
    EVENTS_URL,
    json=event_data,
    headers=creator_headers,
  )
  event_id = create_event.json()["id"]

  await client.post(
    f"/events/{event_id}/join",
    headers=participant1_headers,
  )
  await client.post(
    f"/events/{event_id}/join",
    headers=participant2_headers,
  )

  response = await client.get(f"/events/{event_id}/participants")
  assert response.status_code == 200

  response_data = response.json()
  assert len(response_data) == 2


@pytest.mark.asyncio
async def test_get_participants_nonexistent_event(client: AsyncClient):
  """ Test getting a list of participants for a non-existent event """

  response = await client.get("/events/999999999/participants")
  assert response.status_code == 404
