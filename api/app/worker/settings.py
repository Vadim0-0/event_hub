from arq.connections import RedisSettings
from arq import cron

from .demo_simulator import demo_simulator_tick
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
  notify_upcoming_events,
  notify_registration_confirmed,
  notify_new_participant,
  notify_leave_confirmed,
  notify_participant_left,
  notify_participant_removed,
  notify_new_message,
)


async def startup(ctx):
  from ..models import (  # noqa: F401
    user,
    event,
    registration,
    notification,
    conversation,
    message,
    conversation_read,
    ai_message,
    conversation_user_state,
    message_user_hide,
  )
  
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
    notify_upcoming_events,
    notify_registration_confirmed,
    notify_new_participant,
    notify_leave_confirmed,
    notify_participant_left,
    notify_participant_removed,
    notify_new_message,
    demo_simulator_tick,
  ]

  cron_jobs = [
    cron(
      notify_upcoming_events, 
      minute={0, 15, 30, 45}, unique=True
    ),
    cron(
      demo_simulator_tick,
      minute=set(range(0, 60, settings.demo_simulator_interval_minutes)),
      run_at_startup=True,
      unique=True,
    ),
  ]