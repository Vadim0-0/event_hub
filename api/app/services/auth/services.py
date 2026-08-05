from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...models.user import User
from ...schemas.user import UserLogin, UserRegister
from ...security import (
  get_password_hash,
  verify_password,
  create_access_token,
)
from .. import email_verification

from . import helpers
from . import exceptions


async def register_user(
  data: UserRegister,
  db: AsyncSession,
  redis: Redis,
) -> tuple[User, str]:
  existing = await helpers.get_user_by_email(db, data.email)

  if existing is not None:
    if existing.is_email_verified:
      raise exceptions.EmailAlreadyRegisteredError("This email is already registered")

    username_taken = await helpers.is_username_taken(db, data.username)
    if username_taken:
      raise exceptions.UsernameAlreadyRegisteredError(f"Username ({data.username}) already registered")
    
    existing.username = data.username
    existing.password_hash = get_password_hash(data.password)
    user = existing
  else:
    username_taken = await helpers.is_username_taken(db, data.username)
    if username_taken:
      raise exceptions.UsernameAlreadyRegisteredError(
        f"Username ({data.username}) already registered"
      )
    
    user = User(
      username=data.username,
      email=data.email,
      password_hash=get_password_hash(data.password),
      is_email_verified=False,
    )

    db.add(user)

  await db.commit()
  await db.refresh(user)

  code = email_verification.generate_verification_code()
  await email_verification.store_verification_code(redis, user.email, code)
  await email_verification.set_resend_cooldown(redis, user.email)

  return user, code


async def verify_email(
  email: str,
  code: str,
  db: AsyncSession,
  redis: Redis,
) -> tuple[User, str]:
  user = await helpers.get_user_by_email(db, email)
  if user is None:
    raise exceptions.UserNotFoundForVerificationError("User not found")
  
  if user.is_email_verified:
    raise exceptions.EmailAlreadyVerifiedError("Email is already verified")
  
  is_valid = await email_verification.verify_and_consume_code(redis, email, code)
  if not is_valid:
    raise exceptions.InvalidVerificationCodeError("Invalid or expired verification code")
  
  user.is_email_verified = True
  await db.commit()
  await db.refresh(user)

  return user, create_access_token(subject=user.id)


async def resend_verification_code(
  email: str,
  db: AsyncSession,
  redis: Redis,
) -> tuple[User | None, str | None]:
  user = await helpers.get_user_by_email(db, email)
  if user is None or user.is_email_verified:
    return None, None

  try:
    code = await email_verification.issue_verification_code(redis, user.email)
  except email_verification.ResendTooSoonError as e:
    raise email_verification.ResendTooSoonError(retry_after=e.retry_after) from e

  return user, code


async def login(data: UserLogin, db: AsyncSession) -> tuple[User, str]:
  user = await helpers.get_user_by_email(db, data.email)

  if not user or not verify_password(data.password, user.password_hash):
    raise exceptions.InvalidCredentialsError("Incorrect email or password")

  if not user.is_email_verified:
    raise exceptions.EmailNotVerifiedError("Email is not verified")
    
  return user, create_access_token(subject=user.id)