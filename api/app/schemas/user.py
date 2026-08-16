from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

class UserRegister(BaseModel):
  username: str = Field(min_length=3, max_length=100, pattern=r"^[a-zA-Z0-9_ ]+$", default="user")
  email: EmailStr
  password: str = Field(min_length=8)
  timezone: str = Field(default="UTC", max_length=64)

  @field_validator("timezone")
  @classmethod
  def validate_timezone(cls, v: str) -> str:
    try:
      ZoneInfo(v)
    except ZoneInfoNotFoundError:
      raise ValueError("Invalid timezone")
    return v


class UserLogin(BaseModel):
  email: EmailStr
  password: str


class Token(BaseModel):
  access_token: str
  token_type: str = "bearer"


class UserOut(BaseModel):
  id: int
  username: str
  email: EmailStr
  created_at: datetime
  timezone: str = Field(default="UTC", max_length=64)
  
  @field_validator("timezone")
  @classmethod
  def validate_timezone(cls, v: str) -> str:
    try:
      ZoneInfo(v)
    except ZoneInfoNotFoundError:
      raise ValueError("Invalid timezone")
    return v

  model_config = ConfigDict(from_attributes=True)


class UserListItemOut(BaseModel):
  id: int
  username: str
  email: EmailStr
  created_at: datetime
  is_me: bool

  
class UsersCountOut(BaseModel):
  total: int


class UserEventStatsOut(BaseModel):
  created_count: int
  joined_count: int


class RegisterPendingOut(BaseModel):
  message: str
  email: EmailStr


class VerifyEmailIn(BaseModel):
  email: EmailStr
  code: str = Field(min_length=6, max_length=6, pattern=r"^\d{6}$")


class ResendVerificationIn(BaseModel):
  email: EmailStr


class VerifyEmailOut(BaseModel):
  user: UserOut
  access_token: str
  token_type: str = "bearer"


class UserUpdate(BaseModel):
  username: str | None = Field(default=None, min_length=3, max_length=100, pattern=r"^[a-zA-Z0-9_ ]+$")
  timezone: str | None = Field(default=None, max_length=64)
  
  @field_validator("timezone")
  @classmethod
  def validate_timezone(cls, v: str | None) -> str | None:
    if v is None:
      return v
    try:
      ZoneInfo(v)
    except ZoneInfoNotFoundError:
      raise ValueError("Invalid timezone")
    return v


class UserPasswordUpdate(BaseModel):
  current_password: str
  new_password: str = Field(min_length=8)


class EmailChangeRequest(BaseModel):
  new_email: EmailStr


class EmailChangeConfirm(BaseModel):
  token: str = Field(min_length=6, max_length=6)


class EmailChangePendingOut(BaseModel):
  message: str
  new_email: EmailStr