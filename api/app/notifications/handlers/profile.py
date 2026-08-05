from ...redis_client import get_redis
from .. import messages
from ...notifications import delivery, types


async def notify_email_change_code(ctx, user_id: int, new_email: str, code: str):
  subject, body = messages.email_change_code_message(code)
  await delivery.send(
    to=new_email, subject=subject, body=body,
    redis=get_redis(),
    notification_type=types.NotificationType.EMAIL_CHANGE,
    task_name="notify_email_change_code",
    user_id=user_id,
  )


async def notify_password_changed(ctx, user_id: int, email: str, username: str):
  subject, body = messages.password_changed_message(username)
  await delivery.send(
    to=email, subject=subject, body=body,
    redis=get_redis(),
    notification_type=types.NotificationType.PASSWORD_CHANGED,
    task_name="notify_password_changed",
    user_id=user_id,
  )


async def notify_email_changed(ctx, user_id: int, email: str, username: str, old_email: str):
  subject, body = messages.email_changed_message(username, old_email, email)
  await delivery.send(
    to=email, subject=subject, body=body,
    redis=get_redis(),
    notification_type=types.NotificationType.EMAIL_CHANGED,
    task_name="notify_email_changed",
    user_id=user_id,
  )


async def notify_profile_updated(ctx, user_id: int, email: str, username: str, changes: list[dict]):
  parsed = [types.ChangedField(**c) for c in changes]
  subject, body = messages.profile_updated_message(username, parsed)
  await delivery.send(
    to=email, subject=subject, body=body,
    redis=get_redis(),
    notification_type=types.NotificationType.PROFILE_UPDATED,
    task_name="notify_profile_updated",
    user_id=user_id,
  )