# description of the events table

from datetime import datetime
from sqlalchemy import String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..database import Base

class Event(Base):
  __tablename__ = "events"

  id: Mapped[int] = mapped_column(primary_key=True)
  creator_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
  title: Mapped[str] = mapped_column(String(200))
  description: Mapped[str | None] = mapped_column(Text, nullable=True)
  starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
  max_participants: Mapped[int | None] = mapped_column(nullable=True)
  created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

  creator: Mapped["User"] = relationship(back_populates="created_events")
  registrations: Mapped[list["EventRegistration"]] = relationship(back_populates="event")