from datetime import datetime
import uuid

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class AiMessage(Base):
  __tablename__ = "ai_messages"

  id: Mapped[uuid.UUID] = mapped_column(
    UUID(as_uuid=True),
    primary_key=True,
    default=uuid.uuid7,
  )
  user_id: Mapped[int] = mapped_column(
    ForeignKey("users.id", ondelete="CASCADE"),
    index=True,
  )
  role: Mapped[str] = mapped_column(String(20))
  content: Mapped[str] = mapped_column(Text)
  created_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True),
    server_default=func.now(),
  )

  user: Mapped["User"] = relationship(back_populates="ai_messages")