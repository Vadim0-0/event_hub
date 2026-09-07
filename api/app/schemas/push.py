from pydantic import BaseModel, Field


class PushKeysIn(BaseModel):
  p256dh: str
  auth: str


class PushSubscribeIn(BaseModel):
  endpoint: str
  keys: PushKeysIn
  expirationTime: int | None = None


class PushUnsubscribeIn(BaseModel):
  endpoint: str


class VapidPublicKeyOut(BaseModel):
  public_key: str
  enabled: bool