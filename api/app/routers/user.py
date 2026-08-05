from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from ..cache import cache_get, cache_set
from ..config import settings
from ..database import get_db
from ..dependencies import get_current_user
from ..models.user import User
from ..redis_client import get_redis
from ..schemas.event import EventOut, EventsCountOut
from ..schemas.user import (
  UserOut,
  UserUpdate,
  UserPasswordUpdate,
  UserListItemOut,
  UsersCountOut,
  UserEventStatsOut,
  EmailChangeRequest,
  EmailChangeConfirm,
  EmailChangePendingOut,
  RegisterPendingOut,
)
from ..notifications import dispatch
from ..services import events as events_service
from ..services import users as users_service
from ..services import email_verification

SortOrder = Literal["asc", "desc"]

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=list[UserListItemOut], summary="Get registered users")
async def list_registered_users(
  db: AsyncSession = Depends(get_db),
  current_user: User = Depends(get_current_user),
  skip: int = 0,
  limit: int = 100,
  search: str | None = None,
  include_me: bool = True,
):
  exclude_user_id = None if include_me else current_user.id

  users = await users_service.list_users(
    db,
    skip=skip,
    limit=limit,
    search=search,
    exclude_user_id=exclude_user_id,
  )

  return [
    UserListItemOut(
      id=user.id,
      username=user.username,
      email=user.email,
      created_at=user.created_at,
      is_me=user.id == current_user.id,
    )
    for user in users
  ]


@router.get("/count", response_model=UsersCountOut, summary="Get registered users count")
async def get_registered_users_count(
  db: AsyncSession = Depends(get_db),
  current_user: User = Depends(get_current_user),
  search: str | None = None,
  include_me: bool = True,
):
  exclude_user_id = None if include_me else current_user.id

  total = await users_service.count_users(
    db,
    search=search,
    exclude_user_id=exclude_user_id,
  )

  return {"total": total}


@router.get("/me/stats", response_model=UserEventStatsOut, summary="Get current user event stats")
async def get_my_event_stats(
  db: AsyncSession = Depends(get_db),
  current_user: User = Depends(get_current_user),
):
  return await users_service.get_user_event_stats(db, user_id=current_user.id)


@router.get("/me/events", response_model=list[EventOut], summary="Get current user events")
async def get_my_events(
  db: AsyncSession = Depends(get_db),
  current_user: User = Depends(get_current_user),
  skip: int = 0,
  limit: int = 100,
  search: str | None = None,
  sort: SortOrder = "asc",
  redis: Redis = Depends(get_redis),
):
  cache_key = (
    f"events:my:user={current_user.id}:"
    f"skip={skip}:limit={limit}:search={search or ''}:sort={sort}"
  )

  cached = await cache_get(redis, cache_key)
  if cached is not None:
    return [EventOut.model_validate(item) for item in cached]

  events = await users_service.get_user_events(
    db,
    user_id=current_user.id,
    skip=skip,
    limit=limit,
    search=search,
    sort=sort,
  )

  data = [
    event_out.model_dump(mode="json")
    for event_out in await events_service.build_events_out(db, events)
  ]
  await cache_set(redis, cache_key, data, settings.cache_ttl_seconds)
  return [EventOut.model_validate(item) for item in data]


@router.get("/me/events/count", response_model=EventsCountOut)
async def get_my_events_count(
  db: AsyncSession = Depends(get_db),
  current_user: User = Depends(get_current_user),
  search: str | None = None,
):
  total = await users_service.count_user_events(db, current_user.id, search)
  return {"total": total}


@router.get("/me/joined-events", response_model=list[EventOut], summary="Get events current user joined")
async def get_my_joined_events(
  db: AsyncSession = Depends(get_db),
  current_user: User = Depends(get_current_user),
  skip: int = 0,
  limit: int = 100,
  search: str | None = None,
  sort: SortOrder = "asc",
  redis: Redis = Depends(get_redis),
):
  cache_key = (
    f"events:joined:user={current_user.id}:"
    f"skip={skip}:limit={limit}:search={search or ''}:sort={sort}"
  )

  cached = await cache_get(redis, cache_key)
  if cached is not None:
    return [EventOut.model_validate(item) for item in cached]

  events = await users_service.get_user_joined_events(
    db,
    user_id=current_user.id,
    skip=skip,
    limit=limit,
    search=search,
    sort=sort,
  )

  data = [
    event_out.model_dump(mode="json")
    for event_out in await events_service.build_events_out(db, events)
  ]
  await cache_set(redis, cache_key, data, settings.cache_ttl_seconds)
  return [EventOut.model_validate(item) for item in data]


@router.get("/me/joined-events/count", response_model=EventsCountOut)
async def get_my_joined_events_count(
  db: AsyncSession = Depends(get_db),
  current_user: User = Depends(get_current_user),
  search: str | None = None,
):
  total = await users_service.count_user_joined_events(
    db,
    current_user.id,
    search,
  )
  return {"total": total}


@router.get("/{user_id}/events", response_model=list[EventOut], summary="Get events by creator")
async def get_events_by_creator(
  user_id: int,
  db: AsyncSession = Depends(get_db),
  current_user: User = Depends(get_current_user),
  skip: int = 0,
  limit: int = 100,
  search: str | None = None,
  sort: SortOrder = "asc",
  redis: Redis = Depends(get_redis),
):
  try:
    await users_service.get_user_or_raise(db, user_id)
  except users_service.UserNotFoundError as e:
    raise HTTPException(status_code=404, detail=str(e))

  cache_key = (
    f"events:by-user={user_id}:"
    f"skip={skip}:limit={limit}:search={search or ''}:sort={sort}"
  )

  cached = await cache_get(redis, cache_key)
  if cached is not None:
    return [EventOut.model_validate(item) for item in cached]

  events = await users_service.get_user_events(
    db,
    user_id=user_id,
    skip=skip,
    limit=limit,
    search=search,
    sort=sort,
  )

  data = [
    event_out.model_dump(mode="json")
    for event_out in await events_service.build_events_out(db, events)
  ]
  await cache_set(redis, cache_key, data, settings.cache_ttl_seconds)
  return [EventOut.model_validate(item) for item in data]


@router.get("/{user_id}/events/count", response_model=EventsCountOut)
async def get_events_by_creator_count(
  user_id: int,
  db: AsyncSession = Depends(get_db),
  current_user: User = Depends(get_current_user),
  search: str | None = None,
):
  try:
    await users_service.get_user_or_raise(db, user_id)
  except users_service.UserNotFoundError as e:
    raise HTTPException(status_code=404, detail=str(e))

  total = await users_service.count_user_events(db, user_id, search)
  return {"total": total}


@router.patch("/me", response_model=UserOut, summary="Update current user profile")
async def update_me(
  data: UserUpdate,
  db: AsyncSession = Depends(get_db),
  current_user: User = Depends(get_current_user),
):
  try:
    user, changes = await users_service.update_user_profile(db, current_user, data)

    if changes:
      await dispatch.notify.profile.updated(user.id, user.email, user.username, [c.__dict__ for c in changes])
  except users_service.UsernameAlreadyTakenError as e:
    raise HTTPException(
      status_code=409,
      detail={"message": str(e), "field": "username"},
    )
  return user


@router.patch("/me/password", status_code=204, summary="Change current user password")
async def change_password(
  data: UserPasswordUpdate,
  db: AsyncSession = Depends(get_db),
  current_user: User = Depends(get_current_user),
):
  try:
    await users_service.update_user_password(db, current_user, data)
    await dispatch.notify.profile.password_changed(
      current_user.id, current_user.email, current_user.username
    )
  except users_service.InvalidCurrentPasswordError as e:
    raise HTTPException(status_code=400, detail=str(e))
  except users_service.SamePasswordError as e:
    raise HTTPException(status_code=400, detail=str(e))
  

@router.post("/me/email-change/request", response_model=EmailChangePendingOut)
async def request_email_change(
  data: EmailChangeRequest,
  db: AsyncSession = Depends(get_db),
  redis: Redis = Depends(get_redis),
  current_user: User = Depends(get_current_user),
):
  try:
    code = await users_service.request_email_change(
      db, redis, current_user, str(data.new_email)
    )
  except users_service.SameEmailError as e:
    raise HTTPException(status_code=400, detail=str(e))
  except users_service.EmailAlreadyTakenError as e:
    raise HTTPException(
      status_code=409,
      detail={"message": str(e), "field": "email"},
    )
  except email_verification.ResendTooSoonError as e:
    raise HTTPException(
      status_code=429,
      detail={"message": str(e), "retry_after": e.retry_after},
      headers={"Retry-After": str(e.retry_after)},
    )

  await dispatch.notify.profile.email_change_code(
    current_user.id,
    str(data.new_email),
    code,
  )

  return EmailChangePendingOut(
    message="Confirmation code sent to the new email",
    new_email=data.new_email,
  )


@router.post("/me/email-change/confirm", response_model=UserOut)
async def confirm_email_change(
  data: EmailChangeConfirm,
  db: AsyncSession = Depends(get_db),
  redis: Redis = Depends(get_redis),
  current_user: User = Depends(get_current_user),
):
  
  try:
    old_email = current_user.email

    user = await users_service.confirm_email_change(
      db, redis, current_user, data.token
    )

    await dispatch.notify.profile.email_changed(
      user.id,
      user.email,
      user.username,
      old_email,
    )
  except users_service.InvalidEmailChangeCodeError as e:
    raise HTTPException(status_code=400, detail=str(e))
  except users_service.EmailAlreadyTakenError as e:
    raise HTTPException(
      status_code=409,
      detail={"message": str(e), "field": "email"},
    )

  return user