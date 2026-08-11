from datetime import datetime
import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base

class Conversation(Base):

  __tablename__ = "conversations"
  id: Mapped[uuid.UUID] = mapped_column(
    UUID(as_uuid=True),
    primary_key=True,
    default=uuid.uuid7,
  )
  user1_id: Mapped[int] = mapped_column(
    ForeignKey("users.id", ondelete="CASCADE"),
    index=True,
  )
  user2_id: Mapped[int] = mapped_column(
    ForeignKey("users.id", ondelete="CASCADE"), 
    index=True,
  )
  created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
  updated_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True), 
    server_default=func.now(),
    onupdate=func.now(),
  )

  messages: Mapped[list["Message"]] = relationship(back_populates="conversation")
  
  user1: Mapped["User"] = relationship(
    foreign_keys=[user1_id],
    back_populates="conversations_as_user1",
  )
  user2: Mapped["User"] = relationship(
    foreign_keys=[user2_id],
    back_populates="conversations_as_user2",
  )

  __table_args__ = (
    UniqueConstraint("user1_id", "user2_id", name="uq_conversation_pair"),
  )