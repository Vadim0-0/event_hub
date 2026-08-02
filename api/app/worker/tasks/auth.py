from ...models.notification import NotificationType
from .notifications import send_email
from ...redis_client import get_redis

async def send_verification_email(ctx, user_id: int, user_email: str, code: str):
  await send_email(
    to=user_email,
    subject="Event Hub — verification code",
    body=(
      f"Your verification code: {code}\n\n"
      f"It expires in 15 minutes."
    ),
    notification_type=NotificationType.EMAIL_VERIFICATION,
    task_name="send_verification_email",
    user_id=user_id,
    redis=get_redis(),
  )
  return {"user_id": user_id, "status": "sent"}


async def send_welcome_email(ctx, user_id: int, user_email: str):
  await send_email(
    to=user_email,
    subject="Welcome to Event Hub",
    body=f"Hi! Your account #{user_id} is ready.",
    notification_type=NotificationType.WELCOME,
    task_name="send_welcome_email",
    user_id=user_id,
    redis=get_redis(),
  )
  return {"user_id": user_id, "status": "sent"}