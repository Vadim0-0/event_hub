from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..database import Base

class EventRegistration(Base):
  __tablename__ = "event_registrations"
  __table_args__ = (
    UniqueConstraint("user_id", "event_id", name="uq_user_event"),
  )

  id: Mapped[int] = mapped_column(primary_key=True)
  user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
  event_id: Mapped[int] = mapped_column(ForeignKey("events.id", ondelete="CASCADE"))
  registered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

  user: Mapped["User"] = relationship(back_populates="registrations")
  event: Mapped["Event"] = relationship(back_populates="registrations")