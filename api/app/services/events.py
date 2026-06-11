from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.event import Event
from ..schemas.event import EventCreate


class EventNotFoundError(Exception):
  """Event not found"""
  pass


# Creating an event
async def create_event(data: EventCreate, db: AsyncSession, creator_id: int) -> Event:

  event = Event(
    title = data.title,
    description = data.description,
    starts_at=data.starts_at,
    max_participants=data.max_participants,
    creator_id = creator_id
  )

  db.add(event)
  await db.commit()
  await db.refresh(event)

  return event


async def list_events(db: AsyncSession, skip: int, limit: int):

  result = await db.execute(
    select(Event)
    .where(Event.starts_at > func.now())
    .order_by(Event.starts_at)
    .offset(skip)
    .limit(limit)
  )

  return result.scalars().all()


async def get_user_events(db: AsyncSession, user_id: int, skip: int, limit: int):
  result = await db.execute(
    select(Event)
    .where(Event.creator_id == user_id)
    .offset(skip)
    .limit(limit)
  )

  return result.scalars().all()


async def get_event_by_id(db: AsyncSession, event_id: int) -> Event:
  event = await db.get(Event, event_id)
  if event is None:
    raise EventNotFoundError(f"Event (id:{event_id}) not found")
  return event