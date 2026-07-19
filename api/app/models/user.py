from datetime import datetime
from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base

class User(Base):
  __tablename__ = "users"

  id: Mapped[int] = mapped_column(primary_key=True)
  email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
  username: Mapped[str] = mapped_column(String(100), unique=True, index=True)
  password_hash: Mapped[str] = mapped_column(String(255))
  created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
  
  created_events: Mapped[list["Event"]] = relationship(back_populates="creator")
  registrations: Mapped[list["EventRegistration"]] = relationship(back_populates="user")