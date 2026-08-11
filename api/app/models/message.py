from datetime import datetime
import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Boolean, DateTime, ForeignKey, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class Message(Base):
  __tablename__ = "messages"
  id: Mapped[uuid.UUID] = mapped_column(
    UUID(as_uuid=True),
    primary_key=True,
    default=uuid.uuid7,
  )
  conversation_id: Mapped[uuid.UUID] = mapped_column(
    ForeignKey("conversations.id", ondelete="CASCADE"),
    index=True,
  )
  sender_id: Mapped[int] = mapped_column(
    ForeignKey("users.id", ondelete="SET NULL"),
    index=True,
    nullable=True,
  )
  body: Mapped[str] = mapped_column(Text)
  created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
  is_deleted: Mapped[bool] = mapped_column(
    Boolean,
    default=False,
    server_default="false",
    nullable=False,
  )

  conversation: Mapped["Conversation"] = relationship(back_populates="messages")
  sender: Mapped["User"] = relationship(
    foreign_keys=[sender_id],
    back_populates="sent_messages",
  )