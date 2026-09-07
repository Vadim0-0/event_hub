from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import settings
from ..database import get_db
from ..dependencies import get_current_user
from ..models.user import User
from ..schemas.push import PushSubscribeIn, PushUnsubscribeIn, VapidPublicKeyOut
from ..services.push import services as push_service

router = APIRouter(prefix="/push", tags=["push"])


@router.get("/vapid-public-key", response_model=VapidPublicKeyOut)
async def get_vapid_public_key():
  return VapidPublicKeyOut(
    public_key=settings.vapid_public_key,
    enabled=settings.push_enabled,
  )


@router.post("/subscribe", status_code=204)
async def subscribe_push(
  data: PushSubscribeIn,
  request: Request,
  db: AsyncSession = Depends(get_db),
  current_user: User = Depends(get_current_user),
):
  if not settings.push_enabled:
    return

  await push_service.upsert_subscription(
    db,
    user_id=current_user.id,
    data=data,
    user_agent=request.headers.get("user-agent"),
  )


@router.delete("/subscribe", status_code=204)
async def unsubscribe_push(
  data: PushUnsubscribeIn,
  db: AsyncSession = Depends(get_db),
  current_user: User = Depends(get_current_user),
):
  await push_service.remove_subscription(
    db,
    user_id=current_user.id,
    endpoint=data.endpoint,
  )