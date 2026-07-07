from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.user import User
from ..schemas.user import UserLogin, UserRegister
from ..security import (
  get_password_hash,
  verify_password,
  create_access_token,
)

class EmailAlreadyRegisteredError(Exception):
  """Email is already taken"""
  pass

class UsernameAlreadyRegisteredError(Exception):
  pass

class InvalidCredentialsError(Exception):
  """Wrong email or password"""
  pass

# User registration, password hashing, saving to the DB
async def register_user(data: UserRegister, db: AsyncSession) -> User:
  email_taken = await db.scalar(select(User.id).where(User.email == data.email))
  if email_taken:
    raise EmailAlreadyRegisteredError("This email is already registered")

  username_taken = await db.scalar(select(User.id).where(User.username == data.username))
  if username_taken:
    raise UsernameAlreadyRegisteredError(f"Username ({data.username}) already registered")

  user = User(
    username = data.username,
    email=data.email,
    password_hash=get_password_hash(data.password),
  )

  db.add(user)
  await db.commit()
  await db.refresh(user)

  return user


async def login(data: UserLogin, db: AsyncSession) -> str:
  result = await db.execute(select(User).where(User.email == data.email))
  user = result.scalar_one_or_none()

  if not user or not verify_password(data.password, user.password_hash):
    raise InvalidCredentialsError("Incorrect email or password")

  return create_access_token(subject=user.id)