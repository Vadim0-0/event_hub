from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models.event import Event
from ..models.registration import EventRegistration
from ..models.user import User


class UserNotFoundError(Exception):
  pass


async def get_user_or_raise(db: AsyncSession, user_id: int) -> User:
  user = await db.get(User, user_id)
  if user is None:
    raise UserNotFoundError(f"User (id:{user_id}) not found")
  return user


def _apply_user_search(query, search: str | None):
  if not search:
    return query

  pattern = f"%{search.strip()}%"
  return query.where(
    or_(
      User.username.ilike(pattern),
      User.email.ilike(pattern),
    )
  )


def _apply_event_search(query, search: str | None):
  if not search:
    return query

  pattern = f"%{search.strip()}%"
  return query.where(
    or_(
      Event.title.ilike(pattern),
      Event.description.ilike(pattern),
    )
  )


def _verified_users_only(query):
  return query.where(User.is_email_verified.is_(True))


async def list_users(
  db: AsyncSession,
  skip: int,
  limit: int,
  search: str | None = None,
  exclude_user_id: int | None = None,
) -> list[User]:
  query = select(User).order_by(User.username.asc())
  query = _verified_users_only(query)
  query = _apply_user_search(query, search)

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
  query = _verified_users_only(query)
  query = _apply_user_search(query, search)

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
  query = _apply_event_search(query, search)

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
  query = _apply_event_search(query, search)

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
  query = _apply_event_search(query, search)

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
  query = _apply_event_search(query, search)

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
