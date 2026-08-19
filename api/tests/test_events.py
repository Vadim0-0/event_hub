from httpx import AsyncClient
import pytest
import helpers
from datetime import datetime, timedelta, timezone

EVENTS_URL = "/events/"
GET_USER_EVENTS_URL = "/users/me/events"

NONEXISTENT_EVENT_ID = "00000000-0000-0000-0000-000000000001"


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
      "location": f"Location {counter}",
      "latitude": 55.7558,
      "longitude": 37.6173,
      "max_participants": max_participants,
    }

  return _counter_event_data


# Creating Event
@pytest.mark.asyncio
async def test_creating_event(client: AsyncClient, user_data_factory, event_data_factory):
  """ Creating event """
  user_data = user_data_factory()
  auth = await helpers.register_and_verify(client, user_data)

  user_headers = {"Authorization": f"Bearer {auth['access_token']}"}

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
  assert created_event["location"] == event_data["location"]
  assert created_event["latitude"] == event_data["latitude"]
  assert created_event["longitude"] == event_data["longitude"]
  assert created_event["creator"]["id"] == 1
  assert "username" in created_event["creator"]


@pytest.mark.asyncio
async def test_create_event_coordinates_only_one_fails(client: AsyncClient, user_data_factory, event_data_factory):
  """ Create event coordinates only one fails """
  user_data = user_data_factory()
  auth = await helpers.register_and_verify(client, user_data)

  user_headers = {"Authorization": f"Bearer {auth['access_token']}"}

  event_data = event_data_factory()

  del event_data["longitude"]

  response = await client.post(
    EVENTS_URL,
    json = event_data,
    headers=user_headers
  )

  assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_event_invalid_latitude(client: AsyncClient, user_data_factory, event_data_factory):
  """ Create event invalid latitude """
  user_data = user_data_factory()
  auth = await helpers.register_and_verify(client, user_data)

  user_headers = {"Authorization": f"Bearer {auth['access_token']}"}

  event_data = event_data_factory()

  event_data["latitude"] = 91

  response = await client.post(
    EVENTS_URL,
    json = event_data,
    headers=user_headers
  )

  assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_event_invalid_longitude(client: AsyncClient, user_data_factory, event_data_factory):
  """ create event invalid longitude """
  user_data = user_data_factory()
  auth = await helpers.register_and_verify(client, user_data)

  user_headers = {"Authorization": f"Bearer {auth['access_token']}"}

  event_data = event_data_factory()

  event_data["longitude"] = 181

  response = await client.post(
    EVENTS_URL,
    json = event_data,
    headers=user_headers
  )

  assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_event_without_coordinates(client: AsyncClient, user_data_factory, event_data_factory):
  """ Create event without coordinates """
  user_data = user_data_factory()
  auth = await helpers.register_and_verify(client, user_data)

  user_headers = {"Authorization": f"Bearer {auth['access_token']}"}

  event_data = event_data_factory()

  del event_data["longitude"]
  del event_data["longitude"]

  response = await client.post(
    EVENTS_URL,
    json = event_data,
    headers=user_headers
  )

  assert response.status_code == 201


@pytest.mark.asyncio
async def test_get_user_events(client: AsyncClient, user_data_factory, event_data_factory):
  """ Get User Events """
  user_data = user_data_factory()
  auth = await helpers.register_and_verify(client, user_data)

  user_headers = {"Authorization": f"Bearer {auth['access_token']}"}

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

  auth1 = await helpers.register_and_verify(client, creator1_data)
  auth2 = await helpers.register_and_verify(client, creator2_data)

  creator1_headers = {"Authorization": f"Bearer {auth1['access_token']}"}
  creator2_headers = {"Authorization": f"Bearer {auth2['access_token']}"}

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


# Join Event
@pytest.mark.asyncio
async def test_join_event(client: AsyncClient, user_data_factory, event_data_factory):
  """ Test event registration """
  creator_data = user_data_factory()

  creator_auth = await helpers.register_and_verify(client, creator_data)
  creator_headers = {"Authorization": f"Bearer {creator_auth['access_token']}"}

  user_data = user_data_factory()

  user_auth = await helpers.register_and_verify(client, user_data)
  user_headers = {"Authorization": f"Bearer {user_auth['access_token']}"}

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
async def test_join_event_when_already_started(client: AsyncClient, user_data_factory, event_data_factory):
  """ Test leaving an event when already started """
  creator_data = user_data_factory()
  creator_auth = await helpers.register_and_verify(client, creator_data)
  creator_headers = {"Authorization": f"Bearer {creator_auth['access_token']}"}

  user_data = user_data_factory()

  user_auth = await helpers.register_and_verify(client, user_data)
  user_headers = {"Authorization": f"Bearer {user_auth['access_token']}"}

  event_data = event_data_factory()

  create_event = await client.post(
    EVENTS_URL,
    json={
      **event_data,
      "starts_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
    },
    headers=creator_headers,
  )
  event_id = create_event.json()["id"]

  response = await client.post(
    f"/events/{event_id}/join",
    headers=user_headers,
  )
  assert response.status_code == 409


@pytest.mark.asyncio
async def test_join_event_when_full(client: AsyncClient, user_data_factory, event_data_factory):
  """ Test registration for a completed event """

  creator_data = user_data_factory()
  creator_auth = await helpers.register_and_verify(client, creator_data)
  creator_headers = {"Authorization": f"Bearer {creator_auth['access_token']}"}

  event_data = event_data_factory(max_participants=2)

  create_event = await client.post(
    EVENTS_URL,
    json=event_data,
    headers=creator_headers,
  )
  event_id = create_event.json()["id"]

  for _ in range(1, event_data["max_participants"] + 1):
    participant_data = user_data_factory()
    participant_auth = await helpers.register_and_verify(client, participant_data)
    participant_headers = {"Authorization": f"Bearer {participant_auth['access_token']}"}
    await client.post(
      f"/events/{event_id}/join",
      headers=participant_headers,
    )

  extra_user_data = user_data_factory()
  extra_user_auth = await helpers.register_and_verify(client, extra_user_data)
  extra_user_headers = {"Authorization": f"Bearer {extra_user_auth['access_token']}"}

  response = await client.post(
    f"/events/{event_id}/join",
    headers=extra_user_headers,
  )
  assert response.status_code == 409


@pytest.mark.asyncio
async def test_creator_cannot_join_own_event(client: AsyncClient, user_data_factory, event_data_factory):
  """ Test, creator cannot register for his event """

  creator_data = user_data_factory()
  creator_auth = await helpers.register_and_verify(client, creator_data)
  creator_headers = {"Authorization": f"Bearer {creator_auth['access_token']}"}

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
  creator_auth = await helpers.register_and_verify(client, creator_data)
  creator_headers = {"Authorization": f"Bearer {creator_auth['access_token']}"}

  user_data = user_data_factory()
  user_auth = await helpers.register_and_verify(client, user_data)
  user_headers = {"Authorization": f"Bearer {user_auth['access_token']}"}

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
  user_auth = await helpers.register_and_verify(client, user_data)
  user_headers = {"Authorization": f"Bearer {user_auth['access_token']}"}

  response = await client.post(
    f"/events/{NONEXISTENT_EVENT_ID}/join",
    headers=user_headers,
  )
  assert response.status_code == 404


# Leave Event
@pytest.mark.asyncio
async def test_leave_event(
  client: AsyncClient, 
  user_data_factory, 
  event_data_factory
):
  """ Test leave event """
  creator_data = user_data_factory()
  creator_auth = await helpers.register_and_verify(client, creator_data)
  creator_headers = {"Authorization": f"Bearer {creator_auth['access_token']}"}

  user_data = user_data_factory()
  user_auth = await helpers.register_and_verify(client, user_data)
  user_headers = {"Authorization": f"Bearer {user_auth['access_token']}"}

  event_data = event_data_factory()

  create_event = await client.post(
    EVENTS_URL,
    json=event_data,
    headers=creator_headers,
  )
  event_id = create_event.json()["id"]

  await client.post(
    f"/events/{event_id}/join",
    headers=user_headers,
  )

  response = await client.delete(
    f"/events/{event_id}/leave",
    headers=user_headers,
  )
  assert response.status_code == 204


@pytest.mark.asyncio
async def test_leave_event_twice(
  client: AsyncClient, 
  user_data_factory, 
  event_data_factory
):
  """ Test leave event twice """
  creator_data = user_data_factory()
  creator_auth = await helpers.register_and_verify(client, creator_data)
  creator_headers = {"Authorization": f"Bearer {creator_auth['access_token']}"}

  user_data = user_data_factory()
  user_auth = await helpers.register_and_verify(client, user_data)
  user_headers = {"Authorization": f"Bearer {user_auth['access_token']}"}

  event_data = event_data_factory()

  create_event = await client.post(
    EVENTS_URL,
    json=event_data,
    headers=creator_headers,
  )
  event_id = create_event.json()["id"]

  await client.post(
    f"/events/{event_id}/join",
    headers=user_headers,
  )

  await client.delete(
    f"/events/{event_id}/leave",
    headers=user_headers,
  )

  response = await client.delete(
    f"/events/{event_id}/leave",
    headers=user_headers,
  )
  assert response.status_code == 404


@pytest.mark.asyncio
async def test_leave_event_nonexistent(client: AsyncClient, user_data_factory, event_data_factory):
  """ Test leaving an event when the event does not exist """
  user_data = user_data_factory()
  user_auth = await helpers.register_and_verify(client, user_data)
  user_headers = {"Authorization": f"Bearer {user_auth['access_token']}"}

  response = await client.delete(
    f"/events/{NONEXISTENT_EVENT_ID}/leave",
    headers=user_headers,
  )
  assert response.status_code == 404


@pytest.mark.asyncio
async def test_leave_event_not_registered(client: AsyncClient, user_data_factory, event_data_factory):
  """ Test leaving an event when the user is not registered """
  creator_data = user_data_factory()
  creator_auth = await helpers.register_and_verify(client, creator_data)
  creator_headers = {"Authorization": f"Bearer {creator_auth['access_token']}"}

  user_data = user_data_factory()
  user_auth = await helpers.register_and_verify(client, user_data)
  user_headers = {"Authorization": f"Bearer {user_auth['access_token']}"}

  event_data = event_data_factory()

  create_event = await client.post(
    EVENTS_URL,
    json=event_data,
    headers=creator_headers,
  )
  event_id = create_event.json()["id"]

  response = await client.delete(
    f"/events/{event_id}/leave",
    headers=user_headers,
  )
  assert response.status_code == 404


@pytest.mark.asyncio
async def test_leave_event_when_already_started(client: AsyncClient, user_data_factory, event_data_factory):
  """ Test leaving an event when already started """
  creator_data = user_data_factory()
  creator_auth = await helpers.register_and_verify(client, creator_data)
  creator_headers = {"Authorization": f"Bearer {creator_auth['access_token']}"}

  user_data = user_data_factory()
  user_auth = await helpers.register_and_verify(client, user_data)
  user_headers = {"Authorization": f"Bearer {user_auth['access_token']}"}

  event_data = event_data_factory()

  create_event = await client.post(
    EVENTS_URL,
    json=event_data,
    headers=creator_headers,
  )
  event_id = create_event.json()["id"]

  await client.post(
    f"/events/{event_id}/join",
    headers=user_headers,
  )

  await client.patch(
    f"/events/{event_id}",
    json = {
      "starts_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
    },
    headers=creator_headers
  )

  response = await client.delete(
    f"/events/{event_id}/leave",
    headers=user_headers,
  )
  assert response.status_code == 409


# Participants
@pytest.mark.asyncio
async def test_get_participants(client: AsyncClient, user_data_factory, event_data_factory):
  """ Test getting a list of participants """

  creator_data = user_data_factory()
  creator_auth = await helpers.register_and_verify(client, creator_data)
  creator_headers = {"Authorization": f"Bearer {creator_auth['access_token']}"}

  participant1_data = user_data_factory()
  participant2_data = user_data_factory()

  participant1_auth = await helpers.register_and_verify(client, participant1_data)
  participant2_auth = await helpers.register_and_verify(client, participant2_data)

  participant1_headers = {"Authorization": f"Bearer {participant1_auth['access_token']}"}
  participant2_headers = {"Authorization": f"Bearer {participant2_auth['access_token']}"}

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

  response = await client.get(f"/events/{NONEXISTENT_EVENT_ID}/participants")
  assert response.status_code == 404


# Update Event
@pytest.mark.asyncio
async def test_update_event(client: AsyncClient, user_data_factory, event_data_factory):
  """ Test update event """

  creator_data = user_data_factory()
  creator_auth = await helpers.register_and_verify(client, creator_data)
  creator_headers = {"Authorization": f"Bearer {creator_auth['access_token']}"}

  event_data = event_data_factory()

  create_event = await client.post(
    EVENTS_URL,
    json=event_data,
    headers=creator_headers,
  )
  event_id = create_event.json()["id"]

  update_event = await client.patch(
    f"/events/{event_id}",
    json = {
      "title": "New Title"
    },
    headers=creator_headers
  )
  assert update_event.status_code == 200

  update_event_data = update_event.json()

  assert update_event_data["title"] == "New Title"


@pytest.mark.asyncio
async def test_update_nonexistent_event(client: AsyncClient, user_data_factory, event_data_factory):
  """ Test update non-existent event """

  creator_data = user_data_factory()
  creator_auth = await helpers.register_and_verify(client, creator_data)
  creator_headers = {"Authorization": f"Bearer {creator_auth['access_token']}"}

  update_event = await client.patch(
    f"/events/{NONEXISTENT_EVENT_ID}",
    json = {
      "title": "New Title"
    },
    headers=creator_headers
  )
  assert update_event.status_code == 404


@pytest.mark.asyncio
async def test_update_event_not_authenticated(client: AsyncClient, user_data_factory, event_data_factory):
  """ Test event update without authorization """

  creator_data = user_data_factory()
  creator_auth = await helpers.register_and_verify(client, creator_data)
  creator_headers = {"Authorization": f"Bearer {creator_auth['access_token']}"}

  event_data = event_data_factory()

  create_event = await client.post(
    EVENTS_URL,
    json=event_data,
    headers=creator_headers,
  )
  event_id = create_event.json()["id"]

  update_event = await client.patch(
    f"/events/{event_id}",
    json = {
      "title": "New Title"
    }
  )
  assert update_event.status_code == 401


@pytest.mark.asyncio
async def test_update_event_other_authenticated(client: AsyncClient, user_data_factory, event_data_factory):
  """ Test event update other authorization """

  creator_data = user_data_factory()
  creator_auth = await helpers.register_and_verify(client, creator_data)
  creator_headers = {"Authorization": f"Bearer {creator_auth['access_token']}"}

  event_data = event_data_factory()

  create_event = await client.post(
    EVENTS_URL,
    json=event_data,
    headers=creator_headers,
  )
  event_id = create_event.json()["id"]

  other_user = user_data_factory()
  other_auth = await helpers.register_and_verify(client, other_user)
  other_headers = {"Authorization": f"Bearer {other_auth['access_token']}"}

  update_event = await client.patch(
    f"/events/{event_id}",
    json = {
      "title": "New Title"
    },
    headers=other_headers
  )
  assert update_event.status_code == 403


# Delete Event
@pytest.mark.asyncio
async def test_delete_event(client: AsyncClient, user_data_factory, event_data_factory):
  """ Test delete event """

  creator_data = user_data_factory()
  creator_auth = await helpers.register_and_verify(client, creator_data)
  creator_headers = {"Authorization": f"Bearer {creator_auth['access_token']}"}

  event_data = event_data_factory()

  create_event = await client.post(
    EVENTS_URL,
    json=event_data,
    headers=creator_headers,
  )
  event_id = create_event.json()["id"]

  delete_event = await client.delete(
    f"/events/{event_id}",
    headers=creator_headers
  )
  assert delete_event.status_code == 204


@pytest.mark.asyncio
async def test_delete_event_not_authenticated(client: AsyncClient, user_data_factory, event_data_factory):
  """ Test event delete without authorization """

  creator_data = user_data_factory()
  creator_auth = await helpers.register_and_verify(client, creator_data)
  creator_headers = {"Authorization": f"Bearer {creator_auth['access_token']}"}

  event_data = event_data_factory()

  create_event = await client.post(
    EVENTS_URL,
    json=event_data,
    headers=creator_headers,
  )
  event_id = create_event.json()["id"]

  delete_event = await client.delete(
    f"/events/{event_id}",
  )
  assert delete_event.status_code == 401


@pytest.mark.asyncio
async def test_delete_event_other_authenticated(client: AsyncClient, user_data_factory, event_data_factory):
  """ Test delete update other authorization """

  creator_data = user_data_factory()
  creator_auth = await helpers.register_and_verify(client, creator_data)
  creator_headers = {"Authorization": f"Bearer {creator_auth['access_token']}"}

  event_data = event_data_factory()

  create_event = await client.post(
    EVENTS_URL,
    json=event_data,
    headers=creator_headers,
  )
  event_id = create_event.json()["id"]

  other_user = user_data_factory()
  other_auth = await helpers.register_and_verify(client, other_user)
  other_headers = {"Authorization": f"Bearer {other_auth['access_token']}"}

  delete_event = await client.delete(
    f"/events/{event_id}",
    headers=other_headers
  )
  assert delete_event.status_code == 403
