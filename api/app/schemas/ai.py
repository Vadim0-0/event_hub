from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field
from .event import EventCreate, EventOut

class AiChatRequest(BaseModel):
  message: str = Field(min_length=1, max_length=4000)


class AiEventDraft(BaseModel):
  title: str = Field(min_length=1, max_length=200)
  description: str | None = None
  starts_at: datetime
  location: str | None = Field(default=None, max_length=500)
  latitude: float | None = None
  longitude: float | None = None
  max_participants: int | None = Field(default=None, ge=1)


class AiChatResponse(BaseModel):
  reply: str
  model: str
  user_message_id: UUID
  assistant_message_id: UUID
  draft: AiEventDraft | None = None
  ready_to_create: bool = False


class AiMessageOut(BaseModel):
  id: UUID
  role: str
  content: str
  created_at: datetime
  model_config = ConfigDict(from_attributes=True)

  
class AiMessagesListOut(BaseModel):
  items: list[AiMessageOut]
  total: int


class AiHealthResponse(BaseModel):
  enabled: bool
  available: bool
  model: str


class AiEventDraftResponse(BaseModel):
  reply: str
  draft: AiEventDraft | None = None
  ready_to_create: bool = False


class AiEventCreateResponse(BaseModel):
  reply: str
  event: EventOut