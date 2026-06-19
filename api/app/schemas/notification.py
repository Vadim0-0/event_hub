from datetime import datetime
from pydantic import BaseModel, ConfigDict


class NotificationOut(BaseModel):

  id: int
  type: str
  recipient_email: str
  subject: str
  body: str
  status: str
  task_name: str | None
  event_id: int | None
  user_id: int | None
  created_at: datetime

  model_config = ConfigDict(from_attributes=True)

