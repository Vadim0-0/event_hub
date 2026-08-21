from datetime import datetime
from sqlalchemy import Boolean, String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base

class User(Base):
  __tablename__ = "users"

  id: Mapped[int] = mapped_column(primary_key=True)
  email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
  username: Mapped[str] = mapped_column(String(100), unique=True, index=True)
  password_hash: Mapped[str] = mapped_column(String(255))
  created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
  timezone: Mapped[str] = mapped_column(String(64), server_default="UTC")

  is_email_verified: Mapped[bool] = mapped_column(
    Boolean,
    default=False,
    server_default="false",
  )
  
  created_events: Mapped[list["Event"]] = relationship(back_populates="creator")
  registrations: Mapped[list["EventRegistration"]] = relationship(back_populates="user")

  conversations_as_user1: Mapped[list["Conversation"]] = relationship(
    back_populates="user1",
    foreign_keys="Conversation.user1_id",
  )
  conversations_as_user2: Mapped[list["Conversation"]] = relationship(
    back_populates="user2",
    foreign_keys="Conversation.user2_id",
  )

  sent_messages: Mapped[list["Message"]] = relationship(
    back_populates="sender",
    foreign_keys="Message.sender_id",
  )

  ai_messages: Mapped[list["AiMessage"]] = relationship(
    back_populates="user",
    cascade="all, delete-orphan",
  )

  @property
  def conversations(self) -> list["Conversation"]:
    return self.conversations_as_user1 + self.conversations_as_user2