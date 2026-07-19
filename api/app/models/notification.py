from datetime import datetime
from enum import StrEnum
import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column
from ..database import Base


class NotificationType(StrEnum):
  WELCOME = "welcome"
  EVENT_CREATED = "event_created"
  EVENT_UPDATED = "event_updated"
  EVENT_DELETED = "event_deleted"
  REGISTRATION_CONFIRMED = "registration_confirmed"
  NEW_PARTICIPANT = "new_participant"
  LEAVE_CONFIRMED = "leave_confirmed"
  PARTICIPANT_LEFT = "participant_left"


class NotificationStatus(StrEnum):
  SENT = "sent"
  SKIPPED = "skipped"
  FAILED = "failed"


class Notification(Base):
  __tablename__ = "notifications"

  id: Mapped[uuid.UUID] = mapped_column(
    UUID(as_uuid=True),
    primary_key=True,
    default=uuid.uuid7,
  )
  type: Mapped[str] = mapped_column(String(50), index=True)
  recipient_email: Mapped[str] = mapped_column(String(255), index=True)
  subject: Mapped[str] = mapped_column(String(255))
  body: Mapped[str] = mapped_column(Text)
  status: Mapped[str] = mapped_column(String(20), default=NotificationStatus.SENT)
  task_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
  event_id: Mapped[uuid.UUID | None] = mapped_column(
    UUID(as_uuid=True),
    ForeignKey("events.id", ondelete="SET NULL"),
    nullable=True,
  )
  user_id: Mapped[int | None] = mapped_column(
    ForeignKey("users.id", ondelete="SET NULL"), nullable=True
  )
  created_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True), server_default=func.now()
  )