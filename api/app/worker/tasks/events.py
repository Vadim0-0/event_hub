from sqlalchemy import select

from ...database import AsyncSessionLocal
from ...models.event import Event
from .notifications import send_email
from ...models.registration import EventRegistration
from ...models.user import User

async def send_event_created_notification(
  ctx, event_id: int, user_email: str
):
  """ Confirmation of creation """
  async with AsyncSessionLocal() as db:
    event = await db.get(Event, event_id)
  
    if event is None:
      return {"event_id": event_id, "status": "skipped", "reason": "not_found"}

    event_title = event.title
    event_starts_at = event.starts_at
  
  await send_email(
    to=user_email,
    subject=f"Event created: {event_title}",
    body=f"Your event '{event_title}' starts at {event_starts_at}.",
  )
  return {"event_id": event_id, "status": "sent"}


async def send_event_updated_notification(
  ctx, event_id: int
):
  """ Change event """
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
    event_title = event.title

  for email in participant_emails:
    await send_email(
      to=email,
      subject=f"Event updated: {event_title}",
      body="Date, place or details were changed. Check the app.",
    )
  return {"event_id": event_id, "sent_to": len(participant_emails)}


async def send_event_deleted_notification(
  ctx, event_id: int, event_title: str, participant_emails: list[str]
):
  for email in participant_emails:
    await send_email(
      to=email,
      subject=f"Event deleted: {event_title}",
      body=f"The event '{event_title}' was cancelled.",
    )
  return {"event_id": event_id, "sent_to": len(participant_emails)}
