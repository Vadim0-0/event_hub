from uuid import UUID

from sqlalchemy import select

from ...database import AsyncSessionLocal
from ...models.user import User
from ...redis_client import get_redis
from .. import messages, push_delivery
from ...notifications import delivery, types


async def notify_new_message(
  ctx,
  conversation_id: UUID,
  recipient_id: int,
  sender_username: str,
  body_preview: str,
):
  async with AsyncSessionLocal() as db:
    recipient = await db.get(User, recipient_id)
    if recipient is None:
      return {"status": "skipped"}

  subject, text = messages.new_message_message(sender_username, body_preview)
  push_title, push_body = messages.new_message_push_message(sender_username, body_preview)

  await delivery.send(
    to=recipient.email,
    subject=subject,
    body=text,
    redis=get_redis(),
    notification_type=types.NotificationType.NEW_MESSAGE,
    task_name="notify_new_message",
    user_id=recipient.id,
  )

  await push_delivery.send_to_user(
    user_id=recipient.id,
    title=push_title,
    body=push_body,
    url=f"/chats?conversation={conversation_id}",
    tag=f"message:{conversation_id}",
  )