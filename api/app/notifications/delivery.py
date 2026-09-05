import logging
from uuid import UUID

from redis.asyncio import Redis
from sqlalchemy import select

from ..models.user import User
from ..database import AsyncSessionLocal
from ..services.demo.data import is_demo_email
from ..services.mailer import deliver_email
from ..services import notifications as notifications_service
from . import types

logger = logging.getLogger(__name__)


async def _is_demo_recipient(db, *, to: str, user_id: int | None) -> bool:
  if is_demo_email(to):
    return True

  if user_id is not None:
    user = await db.get(User, user_id)
    return user is not None and user.is_demo

  result = await db.execute(select(User.is_demo).where(User.email == to))
  is_demo = result.scalar_one_or_none()
  return is_demo is True


async def send(
  *,
  to: str,
  subject: str,
  body: str,
  redis: Redis,
  notification_type: types.NotificationType | str,
  task_name: str,
  user_id: int | None = None,
  event_id: UUID | None = None,
) -> None:
  async with AsyncSessionLocal() as db:
    if await _is_demo_recipient(db, to=to, user_id=user_id):
      logger.info("Skip notification for demo recipient: %s", to)
      return

    status = types.NotificationStatus.SENT

    try:
      await deliver_email(to, subject, body)
      logger.info("EMAIL sent to=%s subject=%s", to, subject)
    except Exception:
      logger.exception("Failed to send email to=%s", to)
      status = types.NotificationStatus.FAILED

    await notifications_service.save_notification(
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

    cache_user_id = user_id
    if cache_user_id is None:
      result = await db.execute(select(User.id).where(User.email == to))
      cache_user_id = result.scalar_one_or_none()

  if cache_user_id is not None:
    await notifications_service.invalidate_user_notifications(redis, cache_user_id)
