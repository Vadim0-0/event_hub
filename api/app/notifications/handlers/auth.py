from ...redis_client import get_redis
from .. import messages
from ...notifications import delivery, types


async def notify_verification_code(ctx, user_id: int, email: str, code: str):
  subject, body = messages.verification_code_message(code)
  await delivery.send(
    to=email, subject=subject, body=body,
    redis=get_redis(),
    notification_type=types.NotificationType.EMAIL_VERIFICATION,
    task_name="notify_verification_code",
    user_id=user_id,
  )


async def notify_welcome(ctx, user_id: int, email: str, username: str):
  subject, body = messages.welcome_message(username)
  await delivery.send(
    to=email, subject=subject, body=body,
    redis=get_redis(),
    notification_type=types.NotificationType.WELCOME,
    task_name="notify_welcome",
    user_id=user_id,
  )


async def notify_login(ctx, user_id: int, email: str, username: str):
  subject, body = messages.login_message(username)
  await delivery.send(
    to=email, subject=subject, body=body,
    redis=get_redis(),
    notification_type=types.NotificationType.LOGIN,
    task_name="notify_login",
    user_id=user_id,
  )