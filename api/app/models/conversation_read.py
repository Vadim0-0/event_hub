from datetime import datetime
import uuid
from sqlalchemy import Boolean, ForeignKey, String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base

class ConversationRead(Base):
  __tablename__ = "conversation_reads"

  conversation_id: Mapped[uuid.UUID] = mapped_column(
    ForeignKey("conversations.id", ondelete="CASCADE"),
    primary_key=True,
  )
  user_id: Mapped[int] = mapped_column(
    ForeignKey("users.id", ondelete="CASCADE"),
    primary_key=True,
  )
  last_read_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True),
    server_default=func.now(),
  )

  conversation: Mapped["Conversation"] = relationship()
  user: Mapped["User"] = relationship()