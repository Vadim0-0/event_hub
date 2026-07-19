from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class NotificationOut(BaseModel):

  id: UUID
  type: str
  recipient_email: str
  subject: str
  body: str
  status: str
  task_name: str | None
  event_id: UUID | None
  user_id: int | None
  created_at: datetime

  model_config = ConfigDict(from_attributes=True)

