from datetime import datetime
import uuid
from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class MessageUserHide(Base):
  __tablename__ = "message_user_hides"

  message_id: Mapped[uuid.UUID] = mapped_column(
    UUID(as_uuid=True),
    ForeignKey("messages.id", ondelete="CASCADE"),
    primary_key=True,
  )
  user_id: Mapped[int] = mapped_column(
    ForeignKey("users.id", ondelete="CASCADE"),
    primary_key=True,
  )
  hidden_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True),
    server_default=func.now(),
  )

  message: Mapped["Message"] = relationship()
  user: Mapped["User"] = relationship()