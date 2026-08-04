from redis.asyncio import Redis
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ...models.event import Event
from ...models.registration import EventRegistration
from ...models.user import User
from ...schemas.user import UserUpdate, UserPasswordUpdate
from ...security import get_password_hash, verify_password
from .. import email_change
from ..email_verification import generate_verification_code

from . import helpers
from . import exceptions


async def get_user_or_raise(db: AsyncSession, user_id: int) -> User:
  user = await db.get(User, user_id)
  if user is None:
    raise exceptions.UserNotFoundError(f"User (id:{user_id}) not found")
  return user


async def list_users(
  db: AsyncSession,
  skip: int,
  limit: int,
  search: str | None = None,
  exclude_user_id: int | None = None,
) -> list[User]:
  query = select(User).order_by(User.username.asc())
  query = helpers.verified_users_only(query)
  query = helpers.apply_user_search(query, search)

  if exclude_user_id is not None:
    query = query.where(User.id != exclude_user_id)

  query = query.offset(skip).limit(limit)

  result = await db.execute(query)
  return list(result.scalars().all())


async def count_users(
  db: AsyncSession,
  search: str | None = None,
  exclude_user_id: int | None = None,
) -> int:
  query = select(func.count()).select_from(User)
  query = helpers.verified_users_only(query)
  query = helpers.apply_user_search(query, search)

  if exclude_user_id is not None:
    query = query.where(User.id != exclude_user_id)

  result = await db.execute(query)
  return result.scalar_one()


async def get_user_events(
  db: AsyncSession,
  user_id: int,
  skip: int,
  limit: int,
  search: str | None = None,
  sort: str = "asc",
):
  query = (
    select(Event)
    .options(selectinload(Event.creator))
    .where(Event.creator_id == user_id)
  )
  query = helpers.apply_event_search(query, search)

  order = Event.starts_at.asc() if sort == "asc" else Event.starts_at.desc()
  query = query.order_by(order).offset(skip).limit(limit)

  result = await db.execute(query)
  return list(result.scalars().all())


async def count_user_events(
  db: AsyncSession,
  user_id: int,
  search: str | None = None,
) -> int:
  query = (
    select(func.count())
    .select_from(Event)
    .where(Event.creator_id == user_id)
  )
  query = helpers.apply_event_search(query, search)

  result = await db.execute(query)
  return result.scalar_one()


async def get_user_joined_events(
  db: AsyncSession,
  user_id: int,
  skip: int,
  limit: int,
  search: str | None = None,
  sort: str = "asc",
):
  query = (
    select(Event)
    .join(EventRegistration, EventRegistration.event_id == Event.id)
    .options(selectinload(Event.creator))
    .where(EventRegistration.user_id == user_id)
  )
  query = helpers.apply_event_search(query, search)

  order = Event.starts_at.asc() if sort == "asc" else Event.starts_at.desc()
  query = query.order_by(order).offset(skip).limit(limit)

  result = await db.execute(query)
  return list(result.scalars().all())


async def count_user_joined_events(
  db: AsyncSession,
  user_id: int,
  search: str | None = None,
) -> int:
  query = (
    select(func.count())
    .select_from(Event)
    .join(EventRegistration, EventRegistration.event_id == Event.id)
    .where(EventRegistration.user_id == user_id)
  )
  query = helpers.apply_event_search(query, search)

  result = await db.execute(query)
  return result.scalar_one()


async def get_user_event_stats(
  db: AsyncSession,
  user_id: int,
) -> dict[str, int]:
  created_result = await db.execute(
    select(func.count())
    .select_from(Event)
    .where(Event.creator_id == user_id)
  )
  created_count = created_result.scalar_one()

  joined_result = await db.execute(
    select(func.count())
    .select_from(EventRegistration)
    .where(EventRegistration.user_id == user_id)
  )
  joined_count = joined_result.scalar_one()

  return {
    "created_count": created_count,
    "joined_count": joined_count,
  }


async def update_user_profile(
  db: AsyncSession,
  user: User,
  data: UserUpdate,
) -> User:
  if data.username is None:
    return user

  if data.username == user.username:
    return user

  taken = await db.scalar(
    select(User.id).where(
      User.username == data.username,
      User.id != user.id,
    )
  )
  if taken is not None:
    raise exceptions.UsernameAlreadyTakenError(f"Username ({data.username}) already taken")

  user.username = data.username
  await db.commit()
  await db.refresh(user)

  return user


async def update_user_password(
  db: AsyncSession,
  user: User,
  data: UserPasswordUpdate,
) -> None:
  if data.current_password == data.new_password:
    raise exceptions.SamePasswordError("New password must be different from the current one")

  if not verify_password(data.current_password, user.password_hash):
    raise exceptions.InvalidCurrentPasswordError("Current password is incorrect")

  user.password_hash = get_password_hash(data.new_password)
  await db.commit()


async def request_email_change(
  db: AsyncSession,
  redis: Redis,
  user: User,
  new_email: str,
) -> str:
  new_email = new_email.lower()

  if new_email == user.email.lower():
    raise exceptions.SameEmailError("New email must be different from current email")

  existing = await db.scalar(
    select(User.id).where(User.email == new_email)
  )
  if existing is not None:
    raise exceptions.EmailAlreadyTakenError("This email is already registered")

  code = await email_change.issue_email_change_code(
    redis=redis,
    user_id=user.id,
    new_email=new_email,
  )

  return code


async def confirm_email_change(
  db: AsyncSession,
  redis: Redis,
  user: User,
  token: str,
) -> User:
  new_email = await email_change.verify_and_consume(
    redis,
    user_id=user.id,
    code=token,
  )

  if new_email is None:
    raise exceptions.InvalidEmailChangeCodeError("Invalid or expired confirmation code")

  existing = await db.scalar(
    select(User.id).where(
      User.email == new_email,
      User.id != user.id,
    )
  )
  if existing is not None:
    raise exceptions.EmailAlreadyTakenError("This email is already registered")

  user.email = new_email
  user.is_email_verified = True

  await db.commit()
  await db.refresh(user)

  return user