from uuid import UUID

from sqlalchemy import select

from ...database import AsyncSessionLocal
from ...models.event import Event
from ...models.user import User
from ...redis_client import get_redis
from .. import messages
from ...notifications import delivery, types


async def notify_registration_confirmed(ctx, event_id: UUID, participant_email: str):
  async with AsyncSessionLocal() as db:
    event = await db.get(Event, event_id)
    if event is None:
      return {"status": "skipped"}
    subject, body = messages.registration_confirmed_message(event.title, str(event.starts_at))

  await delivery.send(
    to=participant_email, subject=subject, body=body,
    redis=get_redis(),
    notification_type=types.NotificationType.REGISTRATION_CONFIRMED,
    task_name="notify_registration_confirmed",
    event_id=event_id,
  )


async def notify_new_participant(ctx, event_id: UUID, participant_email: str):
  async with AsyncSessionLocal() as db:
    event = await db.get(Event, event_id)
    if event is None:
      return {"status": "skipped"}

    creator = await db.get(User, event.creator_id)
    if creator is None:
      return {"status": "skipped"}

    subject, body = messages.new_participant_message(event.title, participant_email)

  await delivery.send(
    to=creator.email, subject=subject, body=body,
    redis=get_redis(),
    notification_type=types.NotificationType.NEW_PARTICIPANT,
    task_name="notify_new_participant",
    event_id=event_id,
    user_id=creator.id,
  )


async def notify_leave_confirmed(
  ctx, 
  event_id: UUID, 
  participant_email: str
):
  async with AsyncSessionLocal() as db:
    event = await db.get(Event, event_id)
  
    if event is None:
      return {"event_id": event_id, "status": "skipped", "reason": "not_found"}

    event_title = event.title

    subject, body = messages.leave_confirmed_message(event_title)
  
  await delivery.send(
    to=participant_email,
    subject=subject,
    body=body,
    redis=get_redis(),
    notification_type=types.NotificationType.LEAVE_CONFIRMED,
    task_name="notify_leave_confirmed",
    event_id=event_id,
  )

async def notify_participant_left(ctx, event_id: UUID, participant_email: str):
  async with AsyncSessionLocal() as db:
    event = await db.get(Event, event_id)

    if event is None:
      return {"event_id": event_id, "status": "skipped", "reason": "not_found"}
    
    creator = await db.get(User, event.creator_id)
    if creator is None:
      return {"event_id": event_id, "status": "skipped", "reason": "creator_not_found"}

    creator_email = event.creator.email
    event_title = event.title

    subject, body = messages.participant_left_message(event_title, participant_email)
  
  await delivery.send(
    to=creator_email,
    subject=subject,
    body=body,
    redis=get_redis(),
    notification_type=types.NotificationType.PARTICIPANT_LEFT,
    task_name="notify_participant_left",
    event_id=event_id,
  )


async def notify_participant_removed(ctx, event_id: UUID, participant_email: str):
  async with AsyncSessionLocal() as db:
    event = await db.get(Event, event_id)
    if event is None:
      return {"status": "skipped"}

    subject, body = messages.participant_removed_message(event.title)

  await delivery.send(
    to=participant_email,
    subject=subject,
    body=body,
    redis=get_redis(),
    notification_type=types.NotificationType.PARTICIPANT_REMOVED,
    task_name="notify_participant_removed",
    event_id=event_id,
  )