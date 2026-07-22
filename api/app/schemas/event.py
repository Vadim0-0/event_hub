from uuid import UUID
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


class CreatorOut(BaseModel):
  id: int
  username: str


class EventOut(BaseModel):
  id: UUID
  creator: CreatorOut
  title: str
  description: str | None
  starts_at: datetime
  max_participants: int | None
  participants_count: int
  created_at: datetime

  model_config = ConfigDict(from_attributes=True)


class EventsCountOut(BaseModel):
  total: int


class EventDetailOut(EventOut):
  is_participant: bool | None = None
  is_creator: bool | None = None


class UserEventStatsOut(BaseModel):
  created_count: int
  joined_count: int