from dataclasses import dataclass
from enum import StrEnum


class NotificationType(StrEnum):
  # auth
  EMAIL_VERIFICATION = "email_verification"
  WELCOME = "welcome"
  LOGIN = "login"

  # profile
  PROFILE_UPDATED = "profile_updated"
  PASSWORD_CHANGED = "password_changed"
  EMAIL_CHANGED = "email_changed"
  EMAIL_CHANGE = "email_change"

  # events
  EVENT_CREATED = "event_created"
  EVENT_UPDATED = "event_updated"
  EVENT_DELETED = "event_deleted"

  # registrations
  REGISTRATION_CONFIRMED = "registration_confirmed"
  NEW_PARTICIPANT = "new_participant"
  LEAVE_CONFIRMED = "leave_confirmed"
  PARTICIPANT_LEFT = "participant_left"
  PARTICIPANT_REMOVED = "participant_removed"


class NotificationStatus(StrEnum):
  SENT = "sent"
  SKIPPED = "skipped"
  FAILED = "failed"


@dataclass
class ChangedField:
  name: str          # "username", "title", "starts_at"
  label: str         # "Username", "Start time"
  old: str | None
  new: str | None
