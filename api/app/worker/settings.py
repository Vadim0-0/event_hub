from arq.connections import RedisSettings

from ..config import settings
from ..redis_client import init_redis, close_redis

from ..notifications.handlers import (
  notify_verification_code,
  notify_welcome,
  notify_login,
  notify_email_change_code,
  notify_password_changed,
  notify_email_changed,
  notify_profile_updated,
  notify_event_created,
  notify_event_updated,
  notify_event_deleted,
  notify_registration_confirmed,
  notify_new_participant,
  notify_leave_confirmed,
  notify_participant_left,
  notify_participant_removed,
)


async def startup(ctx):
  await init_redis()


async def shutdown(ctx):
  await close_redis()


class WorkerSettings:
  on_startup = startup
  on_shutdown = shutdown

  redis_settings = RedisSettings.from_dsn(settings.arq_redis_url)

  functions = [
    notify_verification_code,
    notify_welcome,
    notify_login,
    notify_email_change_code,
    notify_password_changed,
    notify_email_changed,
    notify_profile_updated,
    notify_event_created,
    notify_event_updated,
    notify_event_deleted,
    notify_registration_confirmed,
    notify_new_participant,
    notify_leave_confirmed,
    notify_participant_left,
    notify_participant_removed,
  ]