from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.user import User

from ..models.notification import (
  NotificationType,
  NotificationStatus,
  Notification
)


async def save_notification(
  db: AsyncSession,
  *,
  type: NotificationType | str,
  recipient_email: str,
  subject: str,
  body: str,
  status: NotificationStatus = NotificationStatus.SENT,
  task_name: str | None = None,
  event_id: int | None = None,
  user_id: int | None = None,
) -> Notification:

  notification = Notification(
    type = str(type),
    recipient_email = recipient_email,
    subject = subject,
    body = body,
    status = str(status),
    task_name = task_name,
    event_id = event_id,
    user_id = user_id,
  )

  db.add(notification)
  await db.commit()
  await db.refresh(notification)

  return notification


async def get_user_notifications(db: AsyncSession, current_user: User, skip: int, limit: int):
  result = await db.execute(
    select(Notification)
    .where(Notification.recipient_email == current_user.email)
    .order_by(Notification.created_at.desc())
    .offset(skip)
    .limit(limit)
  )

  return result.scalars().all()