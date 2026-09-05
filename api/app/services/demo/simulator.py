from __future__ import annotations

import random
import secrets
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ...config import settings
from ...models.event import Event
from ...models.user import User
from ...schemas.event import EventCreate
from ...security import get_password_hash
from ...services.events import services as events_service
from ...services.registrations import services as registration_service
from ...services.registrations import exceptions as registration_exceptions

from . import data


async def count_demo_users(db: AsyncSession) -> int:
  result = await db.execute(
    select(func.count()).select_from(User).where(User.is_demo.is_(True))
  )
  return result.scalar_one()


async def pick_random_demo_user(db: AsyncSession) -> User | None:
  result = await db.execute(
    select(User)
    .where(User.is_demo.is_(True), User.is_email_verified.is_(True))
    .order_by(func.random())
    .limit(1)
  )
  return result.scalar_one_or_none()


async def pick_random_future_event(db: AsyncSession, *, exclude_creator_id: int | None = None) -> Event | None:
  query = select(Event).where(Event.starts_at > func.now())
  if exclude_creator_id is not None:
    query = query.where(Event.creator_id != exclude_creator_id)
  query = query.order_by(func.random()).limit(1)
  result = await db.execute(query)
  return result.scalar_one_or_none()


async def create_demo_user(db: AsyncSession) -> User:
  base_name = data.random_name()
  suffix = uuid.uuid4().hex[:4]
  username = f"{base_name}"

  email: str | None = None
  for _ in range(5):
    candidate = data.random_demo_email(base_name)
    exists = await db.scalar(select(User.id).where(User.email == candidate))
    if exists is None:
      email = candidate
      break

  if email is None:
    email = f"{data._slug(base_name)}.{uuid.uuid4().hex[:6]}@{data.random_demo_domain()}"

  user = User(
    username=username,
    email=email,
    password_hash=get_password_hash(secrets.token_urlsafe(32)),
    is_email_verified=True,
    is_demo=True,
    timezone=data.random_timezone(),
  )
  db.add(user)
  await db.commit()
  await db.refresh(user)
  return user


async def create_demo_event(db: AsyncSession, creator: User) -> Event:
  location, lat, lng = data.random_location()
  starts_at = datetime.now(timezone.utc) + timedelta(
    days=random.randint(3, 30),
    hours=random.randint(9, 20),
  )

  return await events_service.create_event(
    EventCreate(
      title=data.random_event_title(),
      description=data.random_description(),
      starts_at=starts_at,
      location=location,
      latitude=lat,
      longitude=lng,
      max_participants=random.randint(8, 40),
  ),
    db,
    creator.id,
  )


async def join_demo_user_to_event(db: AsyncSession, user: User, event: Event) -> bool:
  try:
    await registration_service.join_event(
      db,
      event_id=event.id,
      user_id=user.id,
    )
    return True
  except (
    registration_exceptions.AlreadyRegisteredError,
    registration_exceptions.EventFullError,
    registration_exceptions.EventCreatorCannotJoinError,
    registration_exceptions.EventAlreadyStartedError,
    registration_exceptions.EventNotFoundError,
  ):
    return False


async def run_demo_simulator_tick(db: AsyncSession) -> str:
  if not settings.demo_simulator_enabled:
    return "disabled"

  demo_count = await count_demo_users(db)

  actions: list[str] = []

  if demo_count < settings.demo_simulator_max_users:
    actions.append("user")

  if demo_count > 0:
    actions.append("event")
    actions.append("join")

  if not actions:
      return "nothing to do"

  action = random.choice(actions)

  if action == "user":
    user = await create_demo_user(db)
    return f"created user id={user.id} username={user.username}"

  if action == "event":
    creator = await pick_random_demo_user(db)
    if creator is None:
      user = await create_demo_user(db)
      return f"created user id={user.id} (no demo users yet)"

    event = await create_demo_event(db, creator)
    return f"created event id={event.id} title={event.title}"

  user = await pick_random_demo_user(db)
  if user is None:
    user = await create_demo_user(db)
    return f"created user id={user.id} (fallback)"

  event = await pick_random_future_event(db, exclude_creator_id=user.id)
  if event is None:
    event = await create_demo_event(db, user)
    return f"created event id={event.id} (no events to join)"

  joined = await join_demo_user_to_event(db, user, event)
  if joined:
    return f"joined user id={user.id} to event id={event.id}"

  creator = await pick_random_demo_user(db)
  if creator is None:
    return "skipped"

  event = await create_demo_event(db, creator)
  return f"join failed, created event id={event.id}"