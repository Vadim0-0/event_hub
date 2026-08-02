from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field

class UserRegister(BaseModel):
  username: str = Field(min_length=3, max_length=100, pattern=r"^[a-zA-Z0-9_ ]+$", default="user")
  email: EmailStr
  password: str = Field(min_length=8)


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