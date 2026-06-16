from sqlalchemy import select
from sqlalchemy.orm import selectinload
from .notifications import send_email

from ...database import AsyncSessionLocal
from ...models.event import Event
from ...models.user import User


async def send_registration_confirmed_notification(
  ctx, event_id: int, participant_email: str
):
  """ Notify participant that registration was confirmed """
  
  async with AsyncSessionLocal() as db:
    event = await db.get(Event, event_id)
  
    if event is None:
      return {"event_id": event_id, "status": "skipped", "reason": "not_found"}

    event_title = event.title
    event_starts_at = event.starts_at
  
  await send_email(
    to=participant_email,
    subject=f"Join Event: {event_title}",
    body=f"You are registered for the event '{event_title}' starts at {event_starts_at}.",
  )
  return {"event_id": event_id, "status": "sent"}


async def send_new_participant_notification(
  ctx, event_id: int, participant_email: str
):
  """ Notify event creator about a new participant """
  
  async with AsyncSessionLocal() as db:
    event = await db.get(Event, event_id)

    if event is None:
      return {"event_id": event_id, "status": "skipped", "reason": "not_found"}
    
    creator = await db.get(User, event.creator_id)
    if creator is None:
      return {"event_id": event_id, "status": "skipped", "reason": "creator_not_found"}

    creator_email = event.creator.email
    event_title = event.title
  
  await send_email(
    to=creator_email,
    subject=f"A new member has joined: {participant_email}",
    body=f"A new participant({participant_email}) has joined the event({event_title})",
  )
  return {"event_id": event_id, "status": "sent"}


async def send_leave_confirmed_notification(
  ctx, event_id: int, participant_email: str
):
  """ Notify participant that they left the event """
  
  async with AsyncSessionLocal() as db:
    event = await db.get(Event, event_id)
  
    if event is None:
      return {"event_id": event_id, "status": "skipped", "reason": "not_found"}

    event_title = event.title
  
  await send_email(
    to=participant_email,
    subject=f"Leave Event: {event_title}",
    body=f"You left the event '{event_title}'.",
  )
  return {"event_id": event_id, "status": "sent"}


async def send_participant_left_notification(
  ctx, event_id: int, participant_email: str
):
  """ Notify event creator that a participant left """

  async with AsyncSessionLocal() as db:
    event = await db.get(Event, event_id)

    if event is None:
      return {"event_id": event_id, "status": "skipped", "reason": "not_found"}
    
    creator = await db.get(User, event.creator_id)
    if creator is None:
      return {"event_id": event_id, "status": "skipped", "reason": "creator_not_found"}

    creator_email = event.creator.email
    event_title = event.title
  
  await send_email(
    to=creator_email,
    subject=f"A member has left: {participant_email}",
    body=f"Participant {participant_email} has left the event '{event_title}'.",
  )
  return {"event_id": event_id, "status": "sent"}