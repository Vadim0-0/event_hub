from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.event import Event
from ..schemas.event import EventCreate


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