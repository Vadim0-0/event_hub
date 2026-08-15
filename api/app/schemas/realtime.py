from pydantic import BaseModel
from uuid import UUID
from .messaging import MessageOut, ConversationOut


class RealtimeEvent(BaseModel):
  type: str 
  payload: dict


class MessageNewPayload(BaseModel):
  conversation_id: UUID
  sender_username: str
  message: MessageOut