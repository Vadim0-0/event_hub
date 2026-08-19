from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, model_validator


def _validate_coordinates_pair(
  latitude: float | None,
  longitude: float | None,
) -> tuple[float | None, float | None]:
  if latitude is None and longitude is None:
    return None, None

  if latitude is None or longitude is None:
    raise ValueError("latitude and longitude must be provided together")

  if not (-90 <= latitude <= 90):
    raise ValueError("latitude must be between -90 and 90")

  if not (-180 <= longitude <= 180):
    raise ValueError("longitude must be between -180 and 180")

  return latitude, longitude


class EventCreate(BaseModel):
  title: str = Field(max_length=200)
  description: str | None = None
  starts_at: datetime
  location: str | None = Field(default=None, max_length=500)
  latitude: float | None = Field(default=None, ge=-90, le=90)
  longitude: float | None = Field(default=None, ge=-180, le=180)
  max_participants: int | None = None

  @model_validator(mode="after")
  def check_coordinates(self):
    _validate_coordinates_pair(self.latitude, self.longitude)
    return self


class EventUpdate(BaseModel):
  title: str | None = None
  description: str | None = None
  starts_at: datetime | None = None
  location: str | None = Field(default=None, max_length=500)
  latitude: float | None = Field(default=None, ge=-90, le=90)
  longitude: float | None = Field(default=None, ge=-180, le=180)
  max_participants: int | None = Field(default=None, ge=1)

  @model_validator(mode="after")
  def check_coordinates(self):
    _validate_coordinates_pair(self.latitude, self.longitude)
    return self


class CreatorOut(BaseModel):
  id: int
  username: str


class EventOut(BaseModel):
  id: UUID
  creator: CreatorOut
  title: str
  description: str | None
  starts_at: datetime
  location: str | None
  latitude: float | None
  longitude: float | None
  max_participants: int | None
  participants_count: int
  created_at: datetime

  model_config = ConfigDict(from_attributes=True)


class EventsCountOut(BaseModel):
  total: int


class EventDetailOut(EventOut):
  is_participant: bool | None = None
  is_creator: bool | None = None