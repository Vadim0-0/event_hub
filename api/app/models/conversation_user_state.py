from datetime import datetime
import uuid
from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class ConversationUserState(Base):
  __tablename__ = "conversation_user_states"

  conversation_id: Mapped[uuid.UUID] = mapped_column(
    UUID(as_uuid=True),
    ForeignKey("conversations.id", ondelete="CASCADE"),
    primary_key=True,
  )
  user_id: Mapped[int] = mapped_column(
    ForeignKey("users.id", ondelete="CASCADE"),
    primary_key=True,
  )
  hidden_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
  cleared_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

  conversation: Mapped["Conversation"] = relationship()
  user: Mapped["User"] = relationship()