from pydantic import BaseModel, Field

class AiChatRequest(BaseModel):
  message: str = Field(min_length=1, max_length=4000)


class AiChatResponse(BaseModel):
  reply: str
  model: str


class AiHealthResponse(BaseModel):
  enabled: bool
  available: bool
  model: str