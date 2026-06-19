from datetime import datetime
from pydantic import BaseModel, ConfigDict

from .user import UserOut


class RegistrationOut(BaseModel):
  id: int
  user_id: int
  event_id: int
  registered_at: datetime

  model_config = ConfigDict(from_attributes=True)


class ParticipantOut(BaseModel):
  user: UserOut
  registered_at: datetime

  model_config = ConfigDict(from_attributes=True)