from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone

from sqlalchemy.orm import selectinload

from ..models.event import Event
from ..models.registration import EventRegistration


class EventCreatorCannotJoinError(Exception):
  """The event creator cannot register"""
  pass


class EventAlreadyStartedError(Exception):
  """The event has already begun"""
  pass


class EventNotFoundError(Exception):
  """Event not found"""
  pass


class AlreadyRegisteredError(Exception):
  """The user is already registered"""
  pass


class EventFullError(Exception):
  """There are no vacancies"""
  pass


class NotRegisteredError(Exception):
  """User is not registered for this event"""
  pass


async def join_event(
  db: AsyncSession,
  *,
  event_id: int, 
  user_id: int,
):
  # check if an event exists
  event = await db.get(Event, event_id, with_for_update=True)
  if event is None:
    raise EventNotFoundError(
      f"Event (id:{event_id}) not found"
    )

  # The registered user is the creator
  if event.creator_id == user_id:
    raise EventCreatorCannotJoinError(
      f"Event creator cannot join event '{event.title}' (id:{event_id})"
    )

  # The event has already begun
  if event.starts_at < datetime.now(timezone.utc):
    raise EventAlreadyStartedError(
      f"Event '{event.title}' (id:{event_id}) has already started"
    )

  # Checking if a user is registered
  existing = await db.execute(
    select(EventRegistration).where(
      EventRegistration.user_id == user_id,
      EventRegistration.event_id == event_id,
    )
  )
  if existing.scalar_one_or_none() is not None:
    raise AlreadyRegisteredError(
      f"User (id:{user_id}) already registered for event '{event.title}' (id:{event_id})"
    )

  # Checking the participant limit
  if event.max_participants is not None:
    count_result = await db.execute(
      select(func.count())
      .select_from(EventRegistration)
      .where(EventRegistration.event_id == event_id)
    )
    count = count_result.scalar_one()
    if count >= event.max_participants:
      raise EventFullError(
        f"Event '{event.title}' (id:{event_id}) is full ({count}/{event.max_participants})"
      )

  # Recording
  registration = EventRegistration(user_id=user_id, event_id=event_id)
  db.add(registration)
  await db.commit()
  await db.refresh(registration)

  return registration


async def leave_event(
  db: AsyncSession,
  *,
  event_id: int, 
  user_id: int,
):
  # check if an event exists
  event = await db.get(Event, event_id, with_for_update=True)
  if event is None:
    raise EventNotFoundError(
      f"Event (id:{event_id}) not found"
    )

  result = await db.execute(
    select(EventRegistration).where(
      EventRegistration.user_id == user_id,
      EventRegistration.event_id == event_id,
    )
  )

  registration = result.scalar_one_or_none()
  if registration is None:
    raise NotRegisteredError(
      f"User (id:{user_id}) is not registered for event (id:{event_id})"
    )

  if event.starts_at < datetime.now(timezone.utc):
    raise EventAlreadyStartedError(
      f"Event '{event.title}' (id:{event.id}) has already started"
    )

  await db.delete(registration)
  await db.commit()


# getting a list of registered users
async def get_event_participants(
  db: AsyncSession,
  *,
  event_id: int,
  skip: int,
  limit: int,
):
   # check if an event exists
  event = await db.get(Event, event_id)
  if event is None:
    raise EventNotFoundError(f"Event (id:{event_id}) not found")

  result = await db.execute(
    select(EventRegistration)
    .where(EventRegistration.event_id == event_id)
    .options(selectinload(EventRegistration.user))
    .order_by(EventRegistration.registered_at)
    .offset(skip)
    .limit(limit)
  )

  registrations = result.unique().scalars().all()

  return list(registrations)
