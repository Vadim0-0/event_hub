from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

class AiChatRequest(BaseModel):
  message: str = Field(min_length=1, max_length=4000)


class AiChatResponse(BaseModel):
  reply: str
  model: str
  user_message_id: UUID
  assistant_message_id: UUID


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