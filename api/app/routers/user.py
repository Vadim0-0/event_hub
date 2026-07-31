from fastapi import APIRouter, Depends, HTTPException
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Literal

from ..database import get_db
from ..dependencies import get_current_user
from ..models.user import User
from ..schemas.event import EventOut, EventsCountOut, UserEventStatsOut
from ..services import events as events_service
from ..cache import cache_get, cache_set
from ..redis_client import get_redis
from ..config import settings

SortOrder = Literal["asc", "desc"]

router = APIRouter(prefix="/users", tags=["users"])

@router.get( "/{user_id}/events", response_model=list[EventOut], summary="Get events by creator",)
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
  creator = await db.get(User, user_id)
  if creator is None:
    raise HTTPException(status_code=404, detail=f"User (id:{user_id}) not found")

  cache_key = (
    f"events:by-user={user_id}:"
    f"skip={skip}:limit={limit}:search={search or ''}:sort={sort}"
  )

  cached = await cache_get(redis, cache_key)
  if cached is not None:
    return [EventOut.model_validate(item) for item in cached]

  events = await events_service.get_user_events(
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


@router.get( "/{user_id}/events/count", response_model=EventsCountOut,)
async def get_events_by_creator_count(
  user_id: int,
  db: AsyncSession = Depends(get_db),
  current_user: User = Depends(get_current_user),
  search: str | None = None,
):
  creator = await db.get(User, user_id)
  if creator is None:
    raise HTTPException(status_code=404, detail=f"User (id:{user_id}) not found")

  total = await events_service.count_user_events(db, user_id, search)
  return {"total": total}