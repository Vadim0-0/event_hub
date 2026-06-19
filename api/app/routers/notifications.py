from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends
from redis.asyncio import Redis

from ..database import get_db
from ..dependencies import get_current_user
from ..schemas.notification import NotificationOut
from ..models.user import User
from ..services import notifications as notifications_service
from ..redis_client import get_redis
from ..config import settings
from ..cache import cache_get, cache_set

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("/my", response_model=list[NotificationOut], summary="Get user notifications")
async def get_user_notifications(
  db: AsyncSession = Depends(get_db),
  current_user: User = Depends(get_current_user),
  skip: int = 0,
  limit: int = 100,
  redis: Redis = Depends(get_redis),
):
  """
    Get list of notifications by the current user
  """

  cache_key = f"notifications:my:user={current_user.id}:skip={skip}:limit={limit}"

  cached = await cache_get(redis, cache_key)
  if cached is not None:
    return [NotificationOut.model_validate(item) for item in cached]

  notifications = await notifications_service.get_user_notifications(
    db, 
    current_user = current_user, 
    skip=skip, 
    limit=limit
  )

  data = [NotificationOut.model_validate(e).model_dump(mode="json") for e in notifications]
  await cache_set(redis, cache_key, data, settings.cache_ttl_seconds)
  return [NotificationOut.model_validate(item) for item in data]