from ...models.notification import NotificationType
from .notifications import send_email
from ...redis_client import get_redis


async def send_email_change_code(ctx, user_id: int, new_email: str, code: str):
  await send_email(
    to=new_email,
    subject="Event Hub — confirm email change",
    body=(
      f"Your confirmation code: {code}\n\n"
      f"If you did not request this, ignore this email."
    ),
    notification_type=NotificationType.EMAIL_CHANGE,
    task_name="send_email_change_code",
    user_id=user_id,
    redis=get_redis(),
  )
  return {"user_id": user_id, "status": "sent"}