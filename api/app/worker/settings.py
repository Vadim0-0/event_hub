from arq.connections import RedisSettings

from ..config import settings
from .tasks import (
  send_welcome_email,
  send_event_created_notification,
  send_event_updated_notification, 
  send_event_deleted_notification,
  send_registration_confirmed_notification,
  send_new_participant_notification,
  send_leave_confirmed_notification,
  send_participant_left_notification,
)


class WorkerSettings:
  functions = [
    send_welcome_email,
    send_event_created_notification,
    send_event_updated_notification,
    send_event_deleted_notification,
    send_registration_confirmed_notification,
    send_new_participant_notification,
    send_leave_confirmed_notification,
    send_participant_left_notification,
  ]
  redis_settings = RedisSettings.from_dsn(settings.arq_redis_url)