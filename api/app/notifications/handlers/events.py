from uuid import UUID
from datetime import datetime, timedelta, timezone
from sqlalchemy import select, and_

from ...database import AsyncSessionLocal
from ...models.event import Event
from ...models.user import User
from ...models.registration import EventRegistration
from ...redis_client import get_redis
from .. import messages, push_delivery
from ...notifications import delivery, types


async def notify_event_created(ctx, event_id: UUID, creator_email: str):
  async with AsyncSessionLocal() as db:
    event = await db.get(Event, event_id)
    if event is None:
      return {"status": "skipped"}
    title, starts_at = event.title, str(event.starts_at)

  subject, body = messages.event_created_message(title, starts_at)
  await delivery.send(
    to=creator_email, subject=subject, body=body,
    redis=get_redis(),
    notification_type=types.NotificationType.EVENT_CREATED,
    task_name="notify_event_created",
    event_id=event_id,
  )


async def notify_event_updated(ctx, event_id: UUID, changes: list[dict] | None = None):
  async with AsyncSessionLocal() as db:
    event = await db.get(Event, event_id)
    if event is None:
      return {"status": "skipped"}

    result = await db.execute(
      select(User.email)
      .join(EventRegistration, EventRegistration.user_id == User.id)
      .where(EventRegistration.event_id == event_id)
    )

    participant_emails = result.scalars().all()
    title = event.title

  parsed = [types.ChangedField(**c) for c in changes] if changes else None
  subject, body = messages.event_updated_message(title, parsed)

  for email in participant_emails:
    await delivery.send(
      to=email, subject=subject, body=body,
      redis=get_redis(),
      notification_type=types.NotificationType.EVENT_UPDATED,
      task_name="notify_event_updated",
      event_id=event_id,
    )


async def notify_event_deleted(ctx, event_id: UUID, title: str, participant_emails: list[str]):
  subject, body = messages.event_deleted_message(title)
  for email in participant_emails:
    await delivery.send(
      to=email, subject=subject, body=body,
      redis=get_redis(),
      notification_type=types.NotificationType.EVENT_DELETED,
      task_name="notify_event_deleted",
      event_id=event_id,
    )


async def notify_upcoming_events(ctx):
  now = datetime.now(timezone.utc)
  window_end = now + timedelta(minutes=15)

  async with AsyncSessionLocal() as db:
    result = await db.execute(
      select(Event, User)
      .join(EventRegistration, EventRegistration.event_id == Event.id)
      .join(User, User.id == EventRegistration.user_id)
      .where(
        and_(
          Event.starts_at > now,
          Event.starts_at <= window_end,
        )
      )
    )

    rows = result.all()

  for event, user in rows:
    minutes = max(1, int((event.starts_at - now).total_seconds() // 60))
    subject, body = messages.event_starting_message(event.title, minutes)

    await delivery.send(
      to=user.email,
      subject=subject,
      body=body,
      redis=get_redis(),
      notification_type=types.NotificationType.EVENT_STARTING,
      task_name="notify_upcoming_events",
      event_id=event.id,
      user_id=user.id,
    )

    await push_delivery.send_to_user(
      user_id=user.id,
      title=subject,
      body=body,
      url="/events/joinedEventsPage",
      tag=f"event-start:{event.id}",
    )
    
  return {"sent": len(rows)}