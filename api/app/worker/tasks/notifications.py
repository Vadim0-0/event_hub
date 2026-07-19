import logging
from uuid import UUID
from redis.asyncio import Redis
from sqlalchemy import select

from ...models.user import User
from ...database import AsyncSessionLocal
from ...models.notification import (
  NotificationType,
  NotificationStatus,
)
from ...services.notifications import save_notification
from ...services.notification_cache import invalidate_user_notifications

logger = logging.getLogger(__name__)

async def send_email(
  to: str, 
  subject: str, 
  body: str,
  *,
  redis: Redis,
  notification_type: NotificationType | str,
  task_name: str | None = None,
  event_id: UUID | None = None,
  user_id: int | None = None,
  status: NotificationStatus = NotificationStatus.SENT,
) -> None:
  logger.info("EMAIL to=%s subject=%s body=%s", to, subject, body)

  async with AsyncSessionLocal() as db:
    await save_notification(
      db,
      type=notification_type,
      recipient_email=to,
      subject=subject,
      body=body,
      status=status,
      task_name=task_name,
      event_id=event_id,
      user_id=user_id,
    )

    user_id_for_cache = user_id
    if user_id_for_cache is None:
      result = await db.execute(select(User.id).where(User.email == to))
      user_id_for_cache = result.scalar_one_or_none()

  if user_id_for_cache is not None:
    await invalidate_user_notifications(redis, user_id_for_cache)