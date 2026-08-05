from uuid import UUID
from collections.abc import Sequence
from sqlalchemy import func, select, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from ...notifications import types, messages
from ...models.event import Event
from ...models.registration import EventRegistration
from ...schemas.event import CreatorOut, EventCreate, EventOut, EventUpdate

from . import helpers
from . import exceptions


async def build_event_out(
  db: AsyncSession, 
  event: Event
) -> EventOut:
  count_result = await db.execute(
    select(func.count())
    .select_from(EventRegistration)
    .where(EventRegistration.event_id == event.id)
  )
  participants_count = count_result.scalar_one()

  return EventOut(
    id=event.id,
    creator=CreatorOut(
      id=event.creator.id,
      username=event.creator.username,
    ),
    title=event.title,
    description=event.description,
    starts_at=event.starts_at,
    max_participants=event.max_participants,
    participants_count=participants_count,
    created_at=event.created_at,
  )


async def build_events_out(db: AsyncSession, events: Sequence[Event]) -> list[EventOut]:
  return [await build_event_out(db, event) for event in events]


async def is_user_participant(
  db: AsyncSession,
  event_id: UUID,
  user_id: int,
) -> bool:
  result = await db.execute(
    select(EventRegistration.id).where(
      EventRegistration.event_id == event_id,
      EventRegistration.user_id == user_id,
    )
  )
  return result.scalar_one_or_none() is not None


async def get_event_by_id(
  db: AsyncSession, 
  event_id: UUID
) -> EventOut:
  event = await db.get(Event, event_id, options=[selectinload(Event.creator)])
  if event is None:
    raise exceptions.EventNotFoundError(f"Event (id:{event_id}) not found")

  return await build_event_out(db, event)


# Creating an event
async def create_event(
  data: EventCreate, 
  db: AsyncSession, 
  creator_id: int
) -> Event:

  event = Event(
    title = data.title,
    description = data.description,
    starts_at=data.starts_at,
    max_participants=data.max_participants,
    creator_id = creator_id
  )

  db.add(event)
  await db.commit()
  result = await db.execute(
    select(Event)
    .options(selectinload(Event.creator))
    .where(Event.id == event.id)
  )
  return result.scalar_one()


async def list_events(
  db: AsyncSession, 
  skip: int, 
  limit: int,
  search: str | None = None,
  sort: str = "asc",
):

  query = (
    select(Event)
    .options(selectinload(Event.creator))
    .where(Event.starts_at > func.now())
  )

  if search:
    pattern = f"%{search.strip()}%"
    query = query.where(
      or_(
        Event.title.ilike(pattern),
        Event.description.ilike(pattern),
      )
    )

  order = Event.starts_at.asc() if sort == "asc" else Event.starts_at.desc()
  query = query.order_by(order).offset(skip).limit(limit)

  result = await db.execute(query)
  return result.scalars().all()


async def count_events(
  db: AsyncSession,
  search: str | None = None,
) -> int:
  query = (
    select(func.count())
    .select_from(Event)
    .where(Event.starts_at > func.now())
  )

  if search:
    pattern = f"%{search.strip()}%"
    query = query.where(
      or_(
        Event.title.ilike(pattern),
        Event.description.ilike(pattern),
      )
    )
    
  result = await db.execute(query)
  return result.scalar_one()



async def update_event(
  event_data: EventUpdate, 
  db: AsyncSession, 
  event_id: UUID, 
  user_id: int
) -> tuple[Event, list[types.ChangedField]]:
  changes = []

  result = await db.execute(
    select(Event)
    .where(Event.id == event_id)
  )
  event = result.scalar_one_or_none()

  if event is None:
    raise exceptions.EventNotFoundError(f"Event (id:{event_id}) not found")

  if event.creator_id != user_id:
    raise exceptions.PermissionDeniedError("Only the creator can update the event")

  update_data = event_data.model_dump(exclude_unset=True, exclude_none=True)

  for field, new_value in update_data.items():
    old_value = getattr(event, field)
    if old_value != new_value:
      changes.append(types.ChangedField(field, messages.EVENT_FIELD_LABELS[field], str(old_value), str(new_value)))
      setattr(event, field, new_value)

  await db.commit()
  await db.refresh(event, attribute_names=["creator"])
  
  return event


async def delete_event(
  db: AsyncSession, 
  event_id: UUID, 
  user_id: int
):
  result = await db.execute(
    select(Event)
    .where(Event.id == event_id)
  )
  event = result.scalar_one_or_none()

  if event is None:
    raise exceptions.EventNotFoundError(f"Event (id:{event_id}) not found")

  if event.creator_id != user_id:
    raise exceptions.PermissionDeniedError("Only the creator can update the event")

  await db.delete(event)
  await db.commit()
  
  return None