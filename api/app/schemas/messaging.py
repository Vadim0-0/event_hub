from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field

from .user import UserListItemOut


class MessageCreate(BaseModel):
  body: str = Field(min_length=1, max_length=4000)


class MessageOut(BaseModel):
  id: UUID
  conversation_id: UUID
  sender_id: int
  body: str
  created_at: datetime
  is_deleted: bool

  model_config = ConfigDict(from_attributes=True)


class ConversationCreate(BaseModel):
  recipient_id: int


class ConversationParticipantOut(BaseModel):
  id: int
  username: str


class ConversationOut(BaseModel):
  id: UUID
  participant: ConversationParticipantOut
  last_message: MessageOut | None
  unread_count: int
  updated_at: datetime

  model_config = ConfigDict(from_attributes=True)


class ConversationsListOut(BaseModel):
  items: list[ConversationOut]
  total: int


class UnreadCountOut(BaseModel):
  total: int


class DeleteForEveryoneFlag(BaseModel):
  for_everyone: bool = False


class ConversationDeleteIn(DeleteForEveryoneFlag):
  pass


class ConversationClearHistoryIn(DeleteForEveryoneFlag):
  pass


class MessageDeleteIn(DeleteForEveryoneFlag):
  pass