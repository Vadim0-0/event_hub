from uuid import UUID
from .notifications import send_email

from ...database import AsyncSessionLocal
from ...models.event import Event
from ...models.user import User
from ...models.notification import NotificationType
from ...redis_client import get_redis


async def send_registration_confirmed_notification(
  ctx, event_id: UUID, participant_email: str
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
    notification_type=NotificationType.REGISTRATION_CONFIRMED,
    task_name="send_registration_confirmed_notification",
    event_id=event_id,
    redis=get_redis(),
  )
  return {"event_id": event_id, "status": "sent"}


async def send_new_participant_notification(
  ctx, event_id: UUID, participant_email: str
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
    notification_type=NotificationType.NEW_PARTICIPANT,
    task_name="send_new_participant_notification",
    event_id=event_id,
    redis=get_redis(),
  )
  return {"event_id": event_id, "status": "sent"}


async def send_leave_confirmed_notification(
  ctx, event_id: UUID, participant_email: str
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
    notification_type=NotificationType.LEAVE_CONFIRMED,
    task_name="send_leave_confirmed_notification",
    event_id=event_id,
    redis=get_redis(),
  )
  return {"event_id": event_id, "status": "sent"}


async def send_participant_left_notification(
  ctx, event_id: UUID, participant_email: str
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
    notification_type=NotificationType.PARTICIPANT_LEFT,
    task_name="send_participant_left_notification",
    event_id=event_id,
    redis=get_redis(),
  )
  return {"event_id": event_id, "status": "sent"}