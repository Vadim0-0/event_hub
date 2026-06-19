from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class EventCreate(BaseModel):
  title: str = Field(max_length=200)
  description: str | None = None
  starts_at: datetime
  max_participants: int | None = None


class EventUpdate(BaseModel):
  title: str | None = None
  description: str | None = None
  starts_at: datetime | None = None
  max_participants: int | None = Field(default=None, ge=1)


class EventOut(BaseModel):
  id: int
  creator_id: int
  title: str
  description: str | None
  starts_at: datetime
  max_participants: int | None
  created_at: datetime

  model_config = ConfigDict(from_attributes=True)