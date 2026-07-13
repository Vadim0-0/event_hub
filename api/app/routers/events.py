from sqlalchemy import select
from fastapi import APIRouter, Depends, HTTPException
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..dependencies import get_current_user
from ..models.user import User
from ..models.event import Event
from ..models.registration import EventRegistration
from ..schemas.event import EventCreate, EventUpdate, EventOut
from ..schemas.registration import RegistrationOut, ParticipantOut
from ..services import events as events_service
from ..services import registrations as registration_service
from ..cache import cache_get, cache_set, cache_delete
from ..redis_client import get_redis
from ..config import settings
from ..services import event_cache

from ..worker.enqueue import enqueue_job

router = APIRouter(prefix="/events", tags=["events"])


@router.post("/", response_model=EventOut, status_code=201, summary="Creating new event")
async def create_event(
  event_data: EventCreate,
  db: AsyncSession = Depends(get_db),
  current_user: User = Depends(get_current_user),
  redis: Redis = Depends(get_redis),
):
  """
    Creating event.
    Requires authentication.
  """

  new_event = await events_service.create_event(event_data, db, current_user.id)

  await event_cache.invalidate_event_lists(redis, current_user.id)

  await enqueue_job(
    "send_event_created_notification",
    new_event.id,
    current_user.email,
  )

  return new_event


@router.get("/", response_model=list[EventOut], summary="Get events")
async def list_events(
  db: AsyncSession = Depends(get_db),
  skip: int = 0,
  limit: int = 100,
  redis: Redis = Depends(get_redis),
):
  """ Get list of upcoming events """

  cache_key = f"events:list:skip={skip}:limit={limit}"

  cached = await cache_get(redis, cache_key)
  if cached is not None:
    return [EventOut.model_validate(item) for item in cached]

  events = await events_service.list_events(db, skip=skip, limit=limit)
  
  data = [EventOut.model_validate(e).model_dump(mode="json") for e in events]
  await cache_set(
    redis, 
    cache_key,
    data, 
    settings.cache_ttl_seconds
  )
  return data 


@router.get("/my", response_model=list[EventOut], summary="Get user events")
async def get_user_events(
  db: AsyncSession = Depends(get_db),
  current_user: User = Depends(get_current_user),
  skip: int = 0,
  limit: int = 100,
  redis: Redis = Depends(get_redis),
):
  """
    Get list of events created by the current user
  """

  cache_key = f"events:my:user={current_user.id}:skip={skip}:limit={limit}"

  cached = await cache_get(redis, cache_key)
  if cached is not None:
    return [EventOut.model_validate(item) for item in cached]

  events = await events_service.get_user_events(
    db, 
    user_id=current_user.id, 
    skip=skip, 
    limit=limit
  )

  data = [EventOut.model_validate(e).model_dump(mode="json") for e in events]
  await cache_set(redis, cache_key, data, settings.cache_ttl_seconds)
  return [EventOut.model_validate(item) for item in data]


@router.get("/{event_id}", response_model=EventOut, summary="Get event by ID")
async def get_event(
  event_id: int,
  db: AsyncSession = Depends(get_db),
  redis: Redis = Depends(get_redis),
):
  """
    Get event by ID
  """

  cache_key = f"event:{event_id}"

  cached = await cache_get(redis, cache_key)
  if cached is not None:
    return EventOut.model_validate(cached)

  try:
    event = await events_service.get_event_by_id(db, event_id)
  except events_service.EventNotFoundError as e:
    raise HTTPException(status_code=404, detail=str(e))

  event_out = EventOut.model_validate(event)
  await cache_set(redis, cache_key, event_out.model_dump(mode="json"), settings.cache_ttl_seconds)

  return event_out


@router.post("/{event_id}/join", response_model=RegistrationOut, status_code=201, summary='Registration for the event')
async def join_event(
  event_id: int,
  db: AsyncSession = Depends(get_db),
  current_user: User = Depends(get_current_user),
  redis: Redis = Depends(get_redis),
):
  """
    Registration for the event
  """

  try:
    registration =  await registration_service.join_event(
      db,
      event_id=event_id,
      user_id=current_user.id
    )
  except registration_service.EventNotFoundError as e:
    raise HTTPException(status_code=404, detail=str(e))
  except registration_service.EventCreatorCannotJoinError as e:
    raise HTTPException(status_code=409, detail=str(e))
  except registration_service.EventAlreadyStartedError as e:
    raise HTTPException(status_code=409, detail=str(e))
  except registration_service.AlreadyRegisteredError as e:
    raise HTTPException(status_code=409, detail=str(e))
  except registration_service.EventFullError as e:
    raise HTTPException(status_code=409, detail=str(e))

  await enqueue_job("send_registration_confirmed_notification", event_id, current_user.email)
  await enqueue_job("send_new_participant_notification", event_id, current_user.email)

  await event_cache.invalidate_event_participants(redis, event_id)
  
  return registration


@router.delete("/{event_id}/leave", status_code=204, summary='Leave the event')
async def leave_event(
  event_id: int,
  db: AsyncSession = Depends(get_db),
  current_user: User = Depends(get_current_user),
  redis: Redis = Depends(get_redis),
):
  """
    Leave the event
  """

  try:
    await registration_service.leave_event(
      db,
      event_id=event_id,
      user_id=current_user.id
    )
  except registration_service.EventNotFoundError as e:
    raise HTTPException(status_code=404, detail=str(e))
  except registration_service.NotRegisteredError as e:
    raise HTTPException(status_code=404, detail=str(e))
  except registration_service.EventAlreadyStartedError as e:
    raise HTTPException(status_code=409, detail=str(e))

  await event_cache.invalidate_event_participants(redis, event_id)


@router.get("/{event_id}/participants", response_model=list[ParticipantOut], summary="Get a list of event participants")
async def get_participants(
  event_id: int,
  db: AsyncSession = Depends(get_db),
  skip: int = 0,
  limit: int = 100,
  redis: Redis = Depends(get_redis)
):
  """
    Get a list of event participants
  """

  cache_key = f"event:{event_id}:participants:skip={skip}:limit={limit}"

  cached = await cache_get(redis, cache_key)
  if cached is not None:
    return [ParticipantOut.model_validate(item) for item in cached]

  try:
    registrations = await registration_service.get_event_participants(
      db,
      event_id=event_id,
      skip=skip,
      limit=limit
    )
  except registration_service.EventNotFoundError as e:
    raise HTTPException(status_code=404, detail=str(e))

  data = [
    ParticipantOut(user=reg.user, registered_at=reg.registered_at).model_dump(mode="json")
    for reg in registrations
  ]
  await cache_set(
    redis, 
    cache_key,
    data, 
    settings.cache_ttl_seconds
  )

  return [ParticipantOut.model_validate(item) for item in data]


@router.get("/joined/me", response_model=list[EventOut], summary="Get events user joined")
async def get_joined_events(
  db: AsyncSession = Depends(get_db),
  current_user: User = Depends(get_current_user),
  skip: int = 0,
  limit: int = 100,
):
  return await events_service.get_user_joined_events(
    db,
    user_id=current_user.id,
    skip=skip,
    limit=limit,
  )


@router.patch("/{event_id}", response_model=EventOut, summary="Update event")
async def update_event(
  event_id: int,
  event_data: EventUpdate,
  db: AsyncSession = Depends(get_db),
  current_user: User = Depends(get_current_user),
  redis: Redis = Depends(get_redis),
):
  """
    Update event
  """

  try:
    updated_event = await events_service.update_event(
      event_data=event_data,
      event_id=event_id,
      db=db,
      user_id=current_user.id
    )
  except events_service.EventNotFoundError as e:
    raise HTTPException(status_code=404, detail=str(e))
  except events_service.PermissionDeniedError as e:
    raise HTTPException(status_code=403, detail=str(e)) 

  await enqueue_job("send_event_updated_notification", event_id)

  cache_key = f"event:{event_id}"
  await cache_delete(redis, cache_key)

  await event_cache.invalidate_event_lists(redis, current_user.id)

  return updated_event


@router.delete("/{event_id}", status_code=204, summary="Delete event")
async def delete_event(
  event_id: int,
  db: AsyncSession = Depends(get_db),
  current_user: User = Depends(get_current_user),
  redis: Redis = Depends(get_redis),
):
  """
    Delete event
  """
  result = await db.execute(
    select(User.email, Event.title)
    .join(EventRegistration, EventRegistration.user_id == User.id)
    .join(Event, Event.id == EventRegistration.event_id)
    .where(EventRegistration.event_id == event_id)
  )
  participants = result.all()
  
  if not participants:
    participant_emails = []
    event_title = ""
  else:
    participant_emails = [p.email for p in participants]
    event_title = participants[0].title

  try:
    await events_service.delete_event(
      db=db,
      event_id=event_id,
      user_id=current_user.id
    )
  except events_service.EventNotFoundError as e:
    raise HTTPException(status_code=404, detail=str(e))
  except events_service.PermissionDeniedError as e:
    raise HTTPException(status_code=403, detail=str(e)) 

  
  cache_key = f"event:{event_id}"
  await cache_delete(redis, cache_key)

  await event_cache.invalidate_event_completely(redis, event_id, current_user.id)

  await enqueue_job(
    "send_event_deleted_notification",
    event_id,
    event_title,
    participant_emails,
  )